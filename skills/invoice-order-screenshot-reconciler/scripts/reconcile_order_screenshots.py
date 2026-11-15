import argparse
import json
import re
from collections import Counter
from copy import copy
from decimal import Decimal
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

STATUS_TEXT = {
    'matched': '已匹配',
    'review_product': '品名待复核',
    'unmatched_combined': '未匹配（合并付款）',
    'unmatched_conflict': '未匹配（品名冲突）',
}
DEFAULT_COLUMNS = {
    'seq': 1,
    'category': 2,
    'invoice_amount': 10,
    'status': 15,
    'review': 16,
    'invoice_file': 17,
    'evidence': 18,
}


def digest(path):
    value = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'))


def safe_component(value):
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', str(value)).strip().rstrip('.')
    return cleaned[:60] or '未命名'


def save_atomic(workbook, path):
    temporary = path.with_name(path.stem + '.tmp.xlsx')
    workbook.save(temporary)
    temporary.replace(path)


def file_link(name, text=None):
    return f'<a href="{escape(str(name), quote=True)}">{escape(str(text or name))}</a>'


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)


def verify_html_links(path):
    parser = LinkParser()
    parser.feed(path.read_text(encoding='utf-8'))
    broken = []
    for href in parser.links:
        if urlparse(href).scheme or href.startswith('#'):
            continue
        if not (path.parent / unquote(href)).resolve().exists():
            broken.append(href)
    if broken:
        raise RuntimeError(f'{path.name}存在无效链接：{broken}')
    return len(parser.links)


def verify_workbook(path):
    workbook = load_workbook(path, data_only=False)
    count = 0
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if not cell.hyperlink or not cell.hyperlink.target:
                    continue
                target = cell.hyperlink.target
                if urlparse(target).scheme:
                    continue
                if not (path.parent / unquote(target)).resolve().exists():
                    raise RuntimeError(f'{path.name}!{sheet.title}!{cell.coordinate}链接无效：{target}')
                count += 1
    return count


def copy_sheet(source, target, source_rows):
    for column in range(1, source.max_column + 1):
        letter = get_column_letter(column)
        target.column_dimensions[letter].width = source.column_dimensions[letter].width
        target.column_dimensions[letter].hidden = source.column_dimensions[letter].hidden
    for target_row, source_row in enumerate(source_rows, 1):
        for column in range(1, source.max_column + 1):
            source_cell = source.cell(source_row, column)
            target_cell = target.cell(target_row, column, source_cell.value)
            if source_cell.has_style:
                target_cell._style = copy(source_cell._style)
            target_cell.number_format = source_cell.number_format
            target_cell.alignment = copy(source_cell.alignment)
    target.freeze_panes = 'A2'
    target.auto_filter.ref = target.dimensions
    target.sheet_view.showGridLines = False


def build_normal_workbook(master, config, columns, normal_rows, normal_dir, output_path):
    output = Workbook()
    output.remove(output.active)
    overview_name = config.get('overview_sheet', '总览')
    if overview_name in master.sheetnames:
        overview = output.create_sheet(overview_name)
        source = master[overview_name]
        copy_sheet(source, overview, range(1, source.max_row + 1))
    source = master[config.get('master_sheet', '全部83笔')]
    target = output.create_sheet('正常报销')
    copy_sheet(source, target, [1] + normal_rows)
    for row in range(2, target.max_row + 1):
        invoice = target.cell(row, columns['invoice_file'])
        evidence = target.cell(row, columns['evidence'])
        invoice.hyperlink = f'../{normal_dir}/{invoice.value}'
        evidence_names = [x for x in str(evidence.value or '').splitlines() if x and x != '无']
        if evidence_names:
            evidence.hyperlink = f'../{normal_dir}/{evidence_names[0]}'
    save_atomic(output, output_path)


def build_audit_workbook(records, rename_records, report_date, output_path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '订单截图审核'
    sheet.sheet_view.showGridLines = False
    headers = ['原文件', '新截图文件', '发票序号', '发票文件', '发票金额(元)', '截图金额(元)', '匹配状态', '匹配依据', '原截图标注', '审核建议']
    sheet.merge_cells('A1:J1')
    sheet['A1'] = '订单截图与发票匹配审核清单'
    sheet['A1'].font = Font(name='微软雅黑', size=16, bold=True, color='FFFFFF')
    sheet['A1'].fill = PatternFill('solid', fgColor='1E40AF')
    sheet['A1'].alignment = Alignment(horizontal='center', vertical='center')
    counts = Counter(record['status'] for record in records)
    sheet.merge_cells('A2:J2')
    sheet['A2'] = f"共{len(records)}张：已匹配{counts['matched']}张，品名待复核{counts['review_product']}张，未匹配{counts['unmatched_combined'] + counts['unmatched_conflict']}张。仅重命名，不删除文件。"
    sheet['A2'].fill = PatternFill('solid', fgColor='EFF6FF')
    sheet['A2'].alignment = Alignment(wrap_text=True, vertical='center')
    for column, value in enumerate(headers, 1):
        cell = sheet.cell(4, column, value)
        cell.font = Font(name='微软雅黑', bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1E40AF')
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin = Side(style='thin', color='D7DEE8')
    for row_index, record in enumerate(records, 5):
        values = [
            record['source'], record['new_name'], record['invoice_seq_text'], record['invoice_text'],
            record['invoice_amount'], record['screenshot_amount'], STATUS_TEXT[record['status']],
            record['match_basis'], record['old_text'], record['advice'],
        ]
        fill = 'F0FDF4' if record['status'] == 'matched' else ('FFF7ED' if record['status'] == 'review_product' else 'FEF2F2')
        for column, value in enumerate(values, 1):
            cell = sheet.cell(row_index, column, value)
            cell.font = Font(name='微软雅黑', size=10)
            cell.alignment = Alignment(vertical='top', wrap_text=True)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.fill = PatternFill('solid', fgColor=fill)
        for column, target in [(2, record['new_name']), (4, record['invoice_links'][0][1]), (9, record['old_links'][0][1])]:
            sheet.cell(row_index, column).hyperlink = target
            sheet.cell(row_index, column).font = Font(name='微软雅黑', size=10, color='0563C1', underline='single')
        sheet.cell(row_index, 5).number_format = '0.00'
        sheet.cell(row_index, 6).number_format = '0.00'
        sheet.row_dimensions[row_index].height = 90
    for column, width in enumerate([31, 47, 22, 58, 14, 14, 22, 68, 57, 52], 1):
        sheet.column_dimensions[get_column_letter(column)].width = width
    sheet.freeze_panes = 'A5'
    sheet.auto_filter.ref = f'A4:J{4 + len(records)}'
    sheet.row_dimensions[1].height = 30
    sheet.row_dimensions[2].height = 32
    hashes = workbook.create_sheet('重命名哈希')
    hashes.append(['原文件', '新文件', '重命名前SHA-256', '重命名后SHA-256', '校验'])
    for cell in hashes[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1E40AF')
    for item in rename_records:
        hashes.append([item['old'], item['new'], item['before'], item['after'], '一致' if item['before'] == item['after'] else '不一致'])
        row = hashes.max_row
        hashes.cell(row, 2).hyperlink = item['new']
        hashes.cell(row, 2).font = Font(color='0563C1', underline='single')
    hashes.column_dimensions['A'].width = 58
    hashes.column_dimensions['B'].width = 58
    hashes.column_dimensions['C'].width = 68
    hashes.column_dimensions['D'].width = 68
    hashes.freeze_panes = 'A2'
    hashes.auto_filter.ref = hashes.dimensions
    save_atomic(workbook, output_path)


def build_audit_html(records, report_date, normal_list_name, output_path, main_dashboard_name=None):
    counts = Counter(record['status'] for record in records)
    old_count = sum(1 for record in records if record['status'] in {'matched', 'review_product'} for _ in record['old_links'])
    rows = []
    for record in records:
        style = 'ok' if record['status'] == 'matched' else ('pending' if record['status'] == 'review_product' else 'unmatched')
        invoices = '<br>'.join(file_link(name, f'发票{seq:02d}') for seq, name in record['invoice_links'])
        originals = '<br>'.join(file_link(target, name) for name, target in record['old_links'])
        invoice_amount = '—' if record['invoice_amount'] is None else f"¥{record['invoice_amount']:.2f}"
        cells = [
            f'<th scope="row">{escape(record["source"])}</th>',
            f'<td data-label="新截图文件">{file_link(record["new_name"])}</td>',
            f'<td data-label="发票序号">{escape(record["invoice_seq_text"])}</td>',
            f'<td data-label="发票文件">{invoices}</td>',
            f'<td data-label="发票金额">{invoice_amount}</td>',
            f'<td data-label="截图金额">¥{record["screenshot_amount"]:.2f}</td>',
            f'<td data-label="匹配状态"><strong>{STATUS_TEXT[record["status"]]}</strong></td>',
            f'<td data-label="匹配依据">{escape(record["match_basis"])}</td>',
            f'<td data-label="原截图标注">{originals}</td>',
            f'<td data-label="审核建议">{escape(record["advice"])}</td>',
        ]
        rows.append(f'<tr class="{style}">' + ''.join(cells) + '</tr>')
    dashboard_link = f'<a href="../{escape(main_dashboard_name, quote=True)}">返回票款核对总看板</a>' if main_dashboard_name else ''
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>订单截图匹配审核看板</title>
<style>
body{{font-family:"Microsoft YaHei",sans-serif;margin:0;background:#f4f6fa;color:#1f2937;line-height:1.6}}main{{max-width:1600px;margin:auto;padding:28px}}h1{{margin:0 0 8px}}.muted{{color:#64748b;font-size:12px}}.links{{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}}.links a{{padding:8px 12px;background:#fff;border-radius:8px;text-decoration:none;color:#1d4ed8;min-block-size:24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:20px 0}}.card{{background:#fff;border-radius:12px;padding:16px;border-top:5px solid #2563eb;box-shadow:0 2px 8px #0001}}.card.ok{{border-color:#16a34a}}.card.pending{{border-color:#d97706}}.card.unmatched{{border-color:#dc2626}}.num{{font-size:28px;font-weight:700}}.notice{{background:#fff7ed;border-left:4px solid #ea580c;padding:14px 18px;border-radius:8px;margin-bottom:20px}}.table-wrapper{{overflow:auto;max-inline-size:100%;max-block-size:80vh;container-type:inline-size;background:#fff;border-radius:10px}}table{{border-collapse:separate;border-spacing:0;width:100%;font-size:12px}}caption{{text-align:left;font-weight:700;font-size:16px;padding:12px;background:#fff}}thead{{position:sticky;inset-block-start:0;z-index:2}}th,td{{border-inline-end:1px solid #e2e8f0;border-block-end:1px solid #e2e8f0;padding:9px;vertical-align:top;text-align:left}}thead th{{background:#1e40af;color:#fff}}tbody th{{position:sticky;inset-inline-start:0;background:#fff;min-width:190px;max-width:230px;overflow-wrap:anywhere}}td{{min-width:100px;max-width:310px;overflow-wrap:anywhere}}tr.ok td{{background:#f0fdf4}}tr.pending td{{background:#fff7ed}}tr.unmatched td{{background:#fef2f2}}a{{color:#1d4ed8}}a:focus-visible,.table-wrapper:focus-visible{{outline:3px solid #d97706;outline-offset:3px}}@container (width < 900px){{table,thead,tbody,tr,th,td{{display:block}}thead{{display:none}}tr{{margin:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden}}tbody th{{position:static;min-width:0;max-width:none;background:#e2e8f0}}td{{min-width:0;max-width:none}}td::before{{content:attr(data-label) ": ";display:block;font-weight:700;color:#475569}}}}
</style></head><body><main>
<h1>订单截图匹配审核看板</h1><div class="muted">整理日期：{escape(report_date)} · 只重命名，不删除文件</div>
<nav class="links" aria-label="审核资料"><a href="订单截图匹配审核清单_{escape(report_date)}.xlsx">打开审核清单Excel</a>{dashboard_link}<a href="{escape(normal_list_name, quote=True)}">打开正常报销清单</a></nav>
<div class="grid"><div class="card"><div>新订单截图</div><div class="num">{len(records)} 张</div></div><div class="card ok"><div>确认一一对应</div><div class="num">{counts['matched']} 张</div></div><div class="card pending"><div>品名待复核</div><div class="num">{counts['review_product']} 张</div></div><div class="card unmatched"><div>未匹配待复核</div><div class="num">{counts['unmatched_combined'] + counts['unmatched_conflict']} 张</div></div><div class="card"><div>原图标注待审核删除</div><div class="num">{old_count} 张</div></div></div>
<div class="notice"><strong>审核方式：</strong>逐笔打开新截图和发票。确认无误后，由原图所有者自行处理带“待审核删除”的文件；品名待复核和未匹配记录不得直接视为已确认。</div>
<div class="table-wrapper" tabindex="0" role="region" aria-labelledby="audit-caption"><table><caption id="audit-caption">{len(records)}张订单截图逐笔对应关系</caption><thead><tr><th scope="col">原文件</th><th scope="col">新截图文件</th><th scope="col">发票序号</th><th scope="col">发票文件</th><th scope="col">发票金额</th><th scope="col">截图金额</th><th scope="col">匹配状态</th><th scope="col">匹配依据</th><th scope="col">原截图标注</th><th scope="col">审核建议</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></main></body></html>'''
    output_path.write_text(html, encoding='utf-8')


def update_main_dashboard(path, master, config, columns, records, normal_dir, report_date):
    text = path.read_text(encoding='utf-8')
    marker = config.get('main_dashboard_marker', '<h2>逐笔文件对应</h2>')
    if marker not in text:
        raise ValueError(f'主看板缺少标记：{marker}')
    prefix = text.split(marker, 1)[0]
    prefix = re.sub(r'<!-- screenshot-reconciler:(?:links|notice):start -->.*?<!-- screenshot-reconciler:(?:links|notice):end -->', '', prefix, flags=re.S)
    audit_dir = f'{normal_dir}/订单截图匹配审核看板_{report_date}.html'
    audit_xlsx = f'{normal_dir}/订单截图匹配审核清单_{report_date}.xlsx'
    links = f'<!-- screenshot-reconciler:links:start --><a href="{escape(audit_dir, quote=True)}">打开订单截图审核看板</a><a href="{escape(audit_xlsx, quote=True)}">打开截图审核清单</a><!-- screenshot-reconciler:links:end -->'
    if '<div class="links">' in prefix:
        prefix, replacements = re.subn(r'(<div class="links">)(.*?)(</div>)', lambda match: match.group(1) + match.group(2) + links + match.group(3), prefix, count=1, flags=re.S)
        if replacements != 1:
            raise ValueError('主看板链接容器不完整')
    else:
        prefix += '<nav>' + links + '</nav>\n'
    counts = Counter(record['status'] for record in records)
    notice = f'<!-- screenshot-reconciler:notice:start --><div class="notice"><b>订单截图整理：</b>新增{len(records)}张截图，{counts["matched"]}张确认对应，{counts["review_product"]}张品名待复核，{counts["unmatched_combined"] + counts["unmatched_conflict"]}张未匹配；只重命名，未删除文件。</div><!-- screenshot-reconciler:notice:end -->\n'
    prefix += notice
    category_dirs = config.get('category_dirs', {})
    sheet = master[config.get('master_sheet', '全部83笔')]
    body = []
    for row in range(2, sheet.max_row + 1):
        seq = sheet.cell(row, columns['seq']).value
        category = sheet.cell(row, columns['category']).value
        if category not in category_dirs:
            raise ValueError(f'category_dirs缺少分类：{category}')
        folder = category_dirs[category]
        invoice = sheet.cell(row, columns['invoice_file']).value
        evidence = sheet.cell(row, columns['evidence']).value
        if invoice and invoice != '无本地PDF' and (path.parent / folder / invoice).exists():
            invoice_cell = file_link(f'{folder}/{invoice}', '打开发票')
        elif invoice and invoice != '无本地PDF':
            invoice_cell = f'<span class="warn">未随分类包：{escape(invoice)}</span>'
        else:
            invoice_cell = '<span class="warn">无本地PDF</span>'
        evidence_cells = []
        for name in [x for x in str(evidence or '').splitlines() if x]:
            if name == '无':
                evidence_cells.append('无')
            elif (path.parent / folder / name).exists():
                evidence_cells.append(file_link(f'{folder}/{name}', name))
            else:
                evidence_cells.append(f'<span class="warn">未随分类包：{escape(name)}</span>')
        status = escape(str(sheet.cell(row, columns['status']).value or ''))
        review = escape(str(sheet.cell(row, columns['review']).value or ''))
        values = [seq, category, sheet.cell(row, 9).value, sheet.cell(row, 10).value, sheet.cell(row, 11).value, sheet.cell(row, 12).value, sheet.cell(row, 13).value]
        row_class = folder[:2] if folder[:2].isdigit() else '90'
        body.append(f'<tr class="row{row_class}">' + ''.join(f'<td>{escape("" if value is None else str(value))}</td>' for value in values) + f'<td>{invoice_cell}</td><td>{"<br>".join(evidence_cells) or "无"}</td><td>{status}<br><span class="muted">{review}</span></td></tr>')
    table = marker + '<div class="tablebox"><table><thead><tr><th>序号</th><th>分类</th><th>商品/内容</th><th>发票金额</th><th>实付金额</th><th>票款差额</th><th>发票号码</th><th>发票</th><th>付款/订单凭证</th><th>状态及复核事项</th></tr></thead><tbody>' + ''.join(body) + '</tbody></table></div>\n</main></body></html>'
    path.write_text(prefix + table, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='按人工核对映射整理订单截图，默认只预检。')
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    root = (args.root or Path(config['root'])).resolve()
    normal_dir = config['normal_dir']
    folder = root / normal_dir
    master_path = root / config['master_workbook']
    master = load_workbook(master_path)
    sheet = master[config.get('master_sheet', '全部83笔')]
    columns = dict(DEFAULT_COLUMNS)
    columns.update(config.get('columns', {}))
    records_by_seq = {int(sheet.cell(row, columns['seq']).value): row for row in range(2, sheet.max_row + 1)}
    normal_rows = [row for row in range(2, sheet.max_row + 1) if sheet.cell(row, columns['category']).value == config['normal_category']]
    expected = config['expected_totals']
    actual = {
        'all_count': sheet.max_row - 1,
        'all_amount': sum(money(sheet.cell(row, columns['invoice_amount']).value) for row in range(2, sheet.max_row + 1)),
        'normal_count': len(normal_rows),
        'normal_amount': sum(money(sheet.cell(row, columns['invoice_amount']).value) for row in normal_rows),
    }
    for key in ('all_count', 'normal_count'):
        if actual[key] != expected[key]:
            raise ValueError(f'{key}不符：实际{actual[key]}，预期{expected[key]}')
    for key in ('all_amount', 'normal_amount'):
        if actual[key] != money(expected[key]):
            raise ValueError(f'{key}不符：实际{actual[key]}，预期{expected[key]}')
    input_records = config['screenshots']
    if not input_records:
        raise ValueError('screenshots不能为空')
    sources = [item['source'] for item in input_records]
    if len(sources) != len(set(sources)):
        raise ValueError('screenshots存在重复source')
    rename_plan = []
    audit_records = []
    invoice_names = {}
    original_names = {}

    def get_invoice(seq):
        if seq not in records_by_seq:
            raise ValueError(f'总表没有发票序号{seq}')
        row = records_by_seq[seq]
        name = sheet.cell(row, columns['invoice_file']).value
        if not (folder / name).is_file():
            raise FileNotFoundError(folder / name)
        invoice_names[seq] = name
        evidence = [x for x in str(sheet.cell(row, columns['evidence']).value or '').splitlines() if x]
        images = [x for x in evidence if Path(x).suffix.lower() in {'.png', '.jpg', '.jpeg'} and '_付款记录_' in x]
        original_names[seq] = images
        return row, name, images

    for item in input_records:
        status = item['status']
        if status not in STATUS_TEXT:
            raise ValueError(f'未知status：{status}')
        source = folder / item['source']
        if not source.is_file():
            raise FileNotFoundError(source)
        tag = safe_component(item.get('source_tag', source.stem))
        seqs = []
        invoice_amount = None
        invoice_links = []
        if status in {'matched', 'review_product'}:
            seq = int(item['invoice_seq'])
            seqs = [seq]
            row, invoice_name, images = get_invoice(seq)
            amount = money(item['amount'])
            if money(sheet.cell(row, columns['invoice_amount']).value) != amount:
                raise ValueError(f'{source.name}金额{amount}与发票{seq}金额不一致')
            if money(item.get('screenshot_amount', amount)) != amount:
                raise ValueError(f'{source.name}截图金额与映射amount不一致')
            label = '已匹配' if status == 'matched' else '品名待复核'
            new_name = f'发票{seq:02d}_{amount:.2f}元_订单付款截图_{label}_原{tag}{source.suffix.lower()}'
            invoice_amount = float(amount)
            invoice_links = [(seq, invoice_name)]
            invoice_seq_text = f'发票{seq:02d}'
            old_links = []
            if not images:
                raise ValueError(f'发票{seq}未找到原付款截图')
            for index, old_name in enumerate(images, 1):
                marked_name = f'发票{seq:02d}_{amount:.2f}元_原付款截图_待审核删除_{index:02d}{Path(old_name).suffix.lower()}'
                rename_plan.append((folder / old_name, folder / marked_name))
                old_links.append((marked_name, marked_name))
            old_text = '\n'.join(name for name, _ in old_links)
        else:
            if status == 'unmatched_combined':
                seqs = [int(seq) for seq in item['possible_invoices']]
                invoice_seq_text = '可能关联' + '、'.join(f'发票{seq:02d}' for seq in seqs)
            else:
                seqs = [int(item['invoice_seq'])]
                invoice_seq_text = f'仅可能关联发票{seqs[0]:02d}'
                invoice_amount = float(money(item['amount']))
            for seq in seqs:
                _, name, _ = get_invoice(seq)
                invoice_links.append((seq, name))
            new_name = f'未匹配_{safe_component(item["label"])}_待复核_原{tag}{source.suffix.lower()}'
            retained = []
            for seq in seqs:
                retained.extend(original_names[seq])
            old_links = [(name, name) for name in retained]
            old_text = '原图保留，未标待删：\n' + '\n'.join(retained)
        rename_plan.append((source, folder / new_name))
        audit_records.append({
            'source': source.name,
            'new_name': new_name,
            'status': status,
            'invoice_seq_text': invoice_seq_text,
            'invoice_text': '\n'.join(name for _, name in invoice_links),
            'invoice_links': invoice_links,
            'invoice_amount': invoice_amount,
            'screenshot_amount': float(money(item['screenshot_amount'])),
            'match_basis': item['match_basis'],
            'advice': item['advice'],
            'old_links': old_links,
            'old_text': old_text,
            'seqs': seqs,
        })
    if len({source for source, _ in rename_plan}) != len(rename_plan) or len({target for _, target in rename_plan}) != len(rename_plan):
        raise ValueError('重命名计划存在重复源或目标')
    for source, target in rename_plan:
        if not source.is_file():
            raise FileNotFoundError(source)
        if target.exists():
            raise FileExistsError(target)
    report_date = str(config['report_date'])
    audit_xlsx = folder / f'订单截图匹配审核清单_{report_date}.xlsx'
    audit_html = folder / f'订单截图匹配审核看板_{report_date}.html'
    normal_list = folder / config.get('normal_list', f'正常报销清单_{report_date}.xlsx')
    for output in (audit_xlsx, audit_html):
        if output.exists():
            raise FileExistsError(f'审核成果已存在，请先人工检查：{output}')
    counts = Counter(record['status'] for record in audit_records)
    print(f'预检通过：{len(input_records)}张新截图，计划重命名{len(rename_plan)}个文件；' + '，'.join(f'{STATUS_TEXT[key]}{counts[key]}张' for key in STATUS_TEXT))
    if not args.apply:
        for source, target in rename_plan:
            print(f'计划：{source.name} -> {target.name}')
        print('当前为预检模式，未修改任何文件；确认后加--apply执行。')
        return

    hashes = {source: digest(source) for source, _ in rename_plan}
    rename_records = []
    for source, target in rename_plan:
        source.rename(target)
        after = digest(target)
        if after != hashes[source]:
            raise RuntimeError(f'哈希校验失败：{target}')
        rename_records.append({'old': source.name, 'new': target.name, 'before': hashes[source], 'after': after})
    for record in audit_records:
        if record['status'] not in {'matched', 'review_product'}:
            continue
        seq = record['seqs'][0]
        row = records_by_seq[seq]
        evidence = [x for x in str(sheet.cell(row, columns['evidence']).value or '').splitlines() if x]
        replacements = {source.name: target.name for source, target in rename_plan}
        sheet.cell(row, columns['evidence']).value = '\n'.join([record['new_name']] + [replacements.get(name, name) for name in evidence])
        sheet.cell(row, columns['evidence']).hyperlink = f'{normal_dir}/{record["new_name"]}'
        if record['status'] == 'review_product':
            review_cell = sheet.cell(row, columns['review'])
            note = record['match_basis']
            if note not in str(review_cell.value or ''):
                review_cell.value = f'{review_cell.value}；{note}' if review_cell.value else note
    save_atomic(master, master_path)
    master = load_workbook(master_path)
    build_normal_workbook(master, config, columns, normal_rows, normal_dir, normal_list)
    build_audit_workbook(audit_records, rename_records, report_date, audit_xlsx)
    build_audit_html(audit_records, report_date, normal_list.name, audit_html, Path(config['main_dashboard']).name if config.get('main_dashboard') else None)
    if config.get('main_dashboard'):
        update_main_dashboard(root / config['main_dashboard'], master, config, columns, audit_records, normal_dir, report_date)
    for source, _ in rename_plan:
        if source.exists():
            raise RuntimeError(f'源文件仍存在：{source}')
    for workbook_path in (master_path, normal_list, audit_xlsx):
        count = verify_workbook(workbook_path)
        print(f'{workbook_path.name}：{count}个链接有效')
    for html_path in [audit_html] + ([root / config['main_dashboard']] if config.get('main_dashboard') else []):
        count = verify_html_links(html_path)
        print(f'{html_path.name}：{count}个链接有效')
    print(f'完成：{len(rename_records)}个文件重命名且SHA-256一致；未删除任何文件。')


if __name__ == '__main__':
    main()
