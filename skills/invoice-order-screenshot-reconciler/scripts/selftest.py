import base64
import json
import subprocess
import sys
import tempfile
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from openpyxl import Workbook, load_workbook


SCRIPT = Path(__file__).with_name('reconcile_order_screenshots.py')
NORMAL_DIR = '01_正常报销_票款一致_付款齐全'
CATEGORY = '正常报销（票款一致、付款资料齐全）'
REPORT_DATE = '20990101'
DASHBOARD_NAME = '自定义票款总看板.html'
PNG_BYTES = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
)


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.body_rows = 0
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tbody':
            self.in_body = True
        elif tag == 'tr' and self.in_body:
            self.body_rows += 1
        elif tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == 'tbody':
            self.in_body = False


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {
        str(path.relative_to(root)): digest(path)
        for path in root.rglob('*')
        if path.is_file()
    }


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
                linked = (path.parent / unquote(target)).resolve()
                assert linked.exists(), f'{path.name}!{sheet.title}!{cell.coordinate}死链：{target}'
                count += 1
    assert count > 0, f'{path.name}没有可验证的本地超链接'
    return workbook, count


def verify_html(path):
    parser = DocumentParser()
    parser.feed(path.read_text(encoding='utf-8'))
    assert parser.links, f'{path.name}没有链接'
    for href in parser.links:
        if urlparse(href).scheme or href.startswith('#'):
            continue
        linked = (path.parent / unquote(href)).resolve()
        assert linked.exists(), f'{path.name}死链：{href}'
    return parser


def run_cli(config_path, apply=False):
    command = [sys.executable, str(SCRIPT), '--config', str(config_path)]
    if apply:
        command.append('--apply')
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert result.returncode == 0, f'命令失败：{result.stdout}\n{result.stderr}'
    return result.stdout


def create_fixture(root):
    folder = root / NORMAL_DIR
    folder.mkdir(parents=True)
    workbook = Workbook()
    overview = workbook.active
    overview.title = '总览'
    overview['A1'] = '匿名测试总览'
    overview['A2'] = '3笔，60.00元'
    sheet = workbook.create_sheet('全部测试笔')
    headers = ['序号', '分类', 'C', 'D', 'E', 'F', 'G', 'H', '商品', '发票金额', '实付金额', '票款差额', '发票号码', 'N', '核对状态', '复核事项', '发票文件', '付款及订单凭证', '备注']
    sheet.append(headers)
    for seq, amount in [(1, 10), (2, 20), (3, 30)]:
        invoice = f'发票{seq:02d}_{amount:.2f}元_匿名商品.pdf'
        evidence = f'发票{seq:02d}_{amount:.2f}元_匿名商品_付款记录_01.png'
        (folder / invoice).write_bytes(f'%PDF-1.4\n% anonymous invoice {seq}\n'.encode())
        (folder / evidence).write_bytes(PNG_BYTES + f'original-{seq}'.encode())
        sheet.append([seq, CATEGORY, None, None, None, None, None, None, f'匿名商品{seq}', amount, amount, 0, f'NO{seq}', None, '票款一致', '', invoice, evidence, ''])
        row = sheet.max_row
        sheet.cell(row, 17).hyperlink = f'{NORMAL_DIR}/{invoice}'
        sheet.cell(row, 18).hyperlink = f'{NORMAL_DIR}/{evidence}'
    master_path = root / '匿名总表.xlsx'
    workbook.save(master_path)

    for index in range(1, 5):
        (folder / f'未命名_{index:02d}.png').write_bytes(PNG_BYTES + f'new-{index}'.encode())

    (root / DASHBOARD_NAME).write_text(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>匿名总看板</title></head>'
        '<body><main><div><div>无关容器必须保留</div></div>'
        '<div class="links"><a href="匿名总表.xlsx">总表</a></div>'
        '<h2>逐笔文件对应</h2><p>此内容应由脚本重建</p></main></body></html>',
        encoding='utf-8',
    )
    config = {
        'root': str(root),
        'normal_dir': NORMAL_DIR,
        'master_workbook': master_path.name,
        'master_sheet': '全部测试笔',
        'overview_sheet': '总览',
        'normal_category': CATEGORY,
        'report_date': REPORT_DATE,
        'expected_totals': {
            'all_count': 3,
            'all_amount': 60,
            'normal_count': 3,
            'normal_amount': 60,
        },
        'main_dashboard': DASHBOARD_NAME,
        'category_dirs': {CATEGORY: NORMAL_DIR},
        'columns': {
            'seq': 1,
            'category': 2,
            'invoice_amount': 10,
            'status': 15,
            'review': 16,
            'invoice_file': 17,
            'evidence': 18,
        },
        'screenshots': [
            {
                'source': '未命名_01.png',
                'source_tag': '匿名01',
                'status': 'matched',
                'invoice_seq': 1,
                'amount': 10,
                'screenshot_amount': 10,
                'product': '匿名商品1',
                'match_basis': '匿名品名、金额和订单号一致',
                'advice': '人工复核后处理原图',
            },
            {
                'source': '未命名_02.png',
                'source_tag': '匿名02',
                'status': 'review_product',
                'invoice_seq': 2,
                'amount': 20,
                'screenshot_amount': 20,
                'product': '匿名商品2',
                'match_basis': '金额和时间一致，品名待人工确认',
                'advice': '确认品名后再处理原图',
            },
            {
                'source': '未命名_03.png',
                'source_tag': '匿名03',
                'status': 'unmatched_combined',
                'possible_invoices': [3],
                'screenshot_amount': 30,
                'label': '合并付款30.00元',
                'match_basis': '匿名合并订单不能拆成一一对应',
                'advice': '查看完整订单拆分，原图保留',
            },
            {
                'source': '未命名_04.png',
                'source_tag': '匿名04',
                'status': 'unmatched_conflict',
                'invoice_seq': 3,
                'amount': 30,
                'screenshot_amount': 30,
                'label': '30.00元品名冲突',
                'match_basis': '同金额但匿名品名冲突',
                'advice': '另找正确订单，原图保留',
            },
        ],
    }
    config_path = root / 'config.json'
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    return config_path


def main():
    with tempfile.TemporaryDirectory(prefix='invoice-screenshot-reconciler-') as temporary:
        root = Path(temporary)
        config_path = create_fixture(root)
        folder = root / NORMAL_DIR
        master_path = root / '匿名总表.xlsx'
        audit_xlsx = folder / f'订单截图匹配审核清单_{REPORT_DATE}.xlsx'
        audit_html = folder / f'订单截图匹配审核看板_{REPORT_DATE}.html'
        normal_xlsx = folder / f'正常报销清单_{REPORT_DATE}.xlsx'
        before_dry_run = snapshot(root)

        dry_output = run_cli(config_path)
        assert '预检通过：4张新截图，计划重命名6个文件' in dry_output
        assert '未修改任何文件' in dry_output
        assert snapshot(root) == before_dry_run, '预检模式修改了文件'
        assert not audit_xlsx.exists() and not audit_html.exists() and not normal_xlsx.exists()

        apply_output = run_cli(config_path, apply=True)
        assert '6个文件重命名且SHA-256一致' in apply_output
        assert all(not (folder / f'未命名_{index:02d}.png').exists() for index in range(1, 5))
        expected_names = {
            '发票01_10.00元_订单付款截图_已匹配_原匿名01.png',
            '发票02_20.00元_订单付款截图_品名待复核_原匿名02.png',
            '未匹配_合并付款30.00元_待复核_原匿名03.png',
            '未匹配_30.00元品名冲突_待复核_原匿名04.png',
            '发票01_10.00元_原付款截图_待审核删除_01.png',
            '发票02_20.00元_原付款截图_待审核删除_01.png',
        }
        assert all((folder / name).is_file() for name in expected_names)
        assert (folder / '发票03_30.00元_匿名商品_付款记录_01.png').is_file(), '异常关联原图被错误标待删'

        master, master_links = verify_workbook(master_path)
        sheet = master['全部测试笔']
        assert sheet.max_row == 4
        assert sum(sheet.cell(row, 10).value for row in range(2, 5)) == 60
        assert sheet.cell(2, 18).value.splitlines()[0] == '发票01_10.00元_订单付款截图_已匹配_原匿名01.png'
        assert '待审核删除' in sheet.cell(2, 18).value
        assert sheet.cell(3, 18).value.splitlines()[0] == '发票02_20.00元_订单付款截图_品名待复核_原匿名02.png'
        assert '品名待人工确认' in sheet.cell(3, 16).value
        assert sheet.cell(4, 18).value == '发票03_30.00元_匿名商品_付款记录_01.png'

        normal, normal_links = verify_workbook(normal_xlsx)
        assert normal['正常报销'].max_row == 4
        assert '总览' in normal.sheetnames
        audit, audit_links = verify_workbook(audit_xlsx)
        audit_sheet = audit['订单截图审核']
        statuses = Counter(audit_sheet.cell(row, 7).value for row in range(5, 9))
        assert statuses == Counter({'已匹配': 1, '品名待复核': 1, '未匹配（合并付款）': 1, '未匹配（品名冲突）': 1})
        hashes = audit['重命名哈希']
        assert hashes.max_row == 7
        for row in range(2, 8):
            before = hashes.cell(row, 3).value
            after = hashes.cell(row, 4).value
            assert before == after and len(after) == 64
            assert hashes.cell(row, 5).value == '一致'
            assert digest(folder / hashes.cell(row, 2).value) == after

        audit_parser = verify_html(audit_html)
        assert audit_parser.body_rows == 4
        assert f'../{DASHBOARD_NAME}' in audit_parser.links
        dashboard_parser = verify_html(root / DASHBOARD_NAME)
        assert dashboard_parser.body_rows == 3
        assert '无关容器必须保留' in (root / DASHBOARD_NAME).read_text(encoding='utf-8')
        assert f'{NORMAL_DIR}/订单截图匹配审核看板_{REPORT_DATE}.html' in dashboard_parser.links

        print('自测通过：预检零修改；4种状态各1条；6个文件重命名且哈希一致。')
        print(f'链接有效：总表{master_links}个，正常清单{normal_links}个，审核清单{audit_links}个，审核HTML{len(audit_parser.links)}个，主HTML{len(dashboard_parser.links)}个。')
        print('总表保持3笔/60.00元，主看板3行，审核清单4条，异常关联原图保留。')


if __name__ == '__main__':
    main()
