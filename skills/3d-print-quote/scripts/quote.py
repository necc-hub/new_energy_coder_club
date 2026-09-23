#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3D 打印报价计算器：输入切片数据 + 料价 + 运费，输出成本明细与三档报价。"""
import argparse
import math
import json


def r10(x):
    """向上取整到 10 元。"""
    return math.ceil(x / 10) * 10


def main():
    p = argparse.ArgumentParser(description="3D print quote calculator")
    p.add_argument("--weight", type=float, required=True, help="总耗材重量(克)，含支撑")
    p.add_argument("--hours", type=float, required=True, help="总打印时长(小时)")
    p.add_argument("--filament-price", type=float, required=True, help="耗材单价(元/kg)")
    p.add_argument("--shipping", type=float, default=0, help="运费(元)，默认0")
    p.add_argument("--labor-min", type=float, default=30, help="后处理人工(分钟)，默认30；支撑多可调到60")
    p.add_argument("--labor-rate", type=float, default=40, help="人工时薪(元/h)，默认40")
    p.add_argument("--power", type=float, default=0.2, help="机器平均功率(kW)，默认0.2")
    p.add_argument("--elec-price", type=float, default=0.6, help="电价(元/度)，默认0.6")
    p.add_argument("--depreciation", type=float, default=0.75, help="机器折旧损耗(元/h)，默认0.75")
    p.add_argument("--margin", type=float, default=1.3, help="合理价利润率系数，默认1.3")
    p.add_argument("--json", action="store_true", help="输出 JSON")
    a = p.parse_args()

    material = a.weight / 1000 * a.filament_price
    elec = a.hours * a.power * a.elec_price
    depr = a.hours * a.depreciation
    labor = a.labor_min / 60 * a.labor_rate
    cost = material + elec + depr + labor

    breakeven = r10(cost + a.shipping)          # 保本价（含运费）
    fair = r10((cost * a.margin) + a.shipping)  # 合理价（含运费）
    friend = r10(cost + a.shipping - 10)        # 友情价（保本价减10）
    per_g = (fair - a.shipping) / a.weight      # 折算克单价，用于市场行情交叉校验

    out = {
        "成本明细": {
            "材料费": round(material, 1),
            "电费": round(elec, 1),
            "机器折旧损耗": round(depr, 1),
            "人工后处理": round(labor, 1),
            "硬成本小计": round(cost, 1),
            "运费": a.shipping,
        },
        "报价": {
            "保本价": breakeven,
            "合理价": fair,
            "友情价": friend,
            "折算克单价_元每克": round(per_g, 2),
        },
    }

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("== 成本明细 ==")
        for k, v in out["成本明细"].items():
            print(f"  {k}: {v} 元")
        print("== 报价 ==")
        for k, v in out["报价"].items():
            unit = " 元/g" if "克单价" in k else " 元"
            print(f"  {k}: {v}{unit}")
        if per_g < 0.2:
            print("⚠️ 折算克单价低于 0.2 元/g，低于市场行情，建议按 0.25~0.35 元/g 重新核价")
        elif per_g > 0.35:
            print("⚠️ 折算克单价高于 0.35 元/g，高于常见市场行情，需向客户说明价值点")


if __name__ == "__main__":
    main()
