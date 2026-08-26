#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四柱八字精确排盘脚本（基于 lunar-python 历法库）
================================================
本脚本是 bazi-accurate skill 的核心排盘工具。它使用经过验证的 lunar-python
历法库计算四柱八字，确保日柱、时柱等所有干支绝对准确，杜绝手工推算错误。

用法：
    python3 paipan.py --solar 1990-05-15 --shichen 未 --gender female
    python3 paipan.py --solar 1988-10-01 --hour 23 --gender male

参数：
    --solar    阳历日期，格式 YYYY-MM-DD（必填）
    --hour     出生小时（0-23 整数），自动换算时辰（可选，与 --shichen 二选一）
    --shichen  时辰名（子丑寅卯辰巳午未申酉戌亥），可选
    --gender   性别 male/female 或 男/女（必填，影响大运顺逆）

输出：完整排盘数据（四柱、十神、藏干、纳音、十二长生、大运、流年）
"""
import argparse
import sys

try:
    from lunar_python import Solar
except ImportError:
    print("错误：未安装 lunar-python 库。请先执行：pip install lunar-python --break-system-packages")
    sys.exit(1)

SHICHEN_MAP = {
    "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
    "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11,
}
SHICHEN_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 时辰对应的小时范围（每个时辰2小时）
SHICHEN_HOURS = [
    (23, 0), (1, 2), (3, 4), (5, 6), (7, 8), (9, 10),
    (11, 12), (13, 14), (15, 16), (17, 18), (19, 20), (21, 22),
]


def hour_to_shichen(hour):
    """小时数(0-23)转时辰索引。夜子时23点归次日子时。"""
    if hour == 23:
        return 0
    return (hour + 1) // 2


def main():
    parser = argparse.ArgumentParser(description="四柱八字精确排盘")
    parser.add_argument("--solar", required=True, help="阳历日期 YYYY-MM-DD")
    parser.add_argument("--hour", type=int, help="出生小时 0-23")
    parser.add_argument("--shichen", help="时辰名 子丑寅卯辰巳午未申酉戌亥")
    parser.add_argument("--gender", required=True, help="性别 male/female 或 男/女")
    args = parser.parse_args()

    # 解析日期
    try:
        parts = args.solar.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        print("错误：日期格式应为 YYYY-MM-DD")
        sys.exit(1)

    # 确定时辰
    if args.shichen:
        if args.shichen not in SHICHEN_MAP:
            print("错误：时辰名无效，应为 子丑寅卯辰巳午未申酉戌亥 之一")
            sys.exit(1)
        shichen_idx = SHICHEN_MAP[args.shichen]
    elif args.hour is not None:
        if not 0 <= args.hour <= 23:
            print("错误：小时应为 0-23")
            sys.exit(1)
        shichen_idx = hour_to_shichen(args.hour)
    else:
        print("错误：必须提供 --hour 或 --shichen")
        sys.exit(1)

    # 时辰对应的小时（取该时辰起始小时，避免边界问题）
    h_start, h_end = SHICHEN_HOURS[shichen_idx]
    hour_val = h_start

    # 性别
    gender = 1 if args.gender in ("male", "男") else 0

    # 排盘
    solar = Solar.fromYmdHms(y, m, d, hour_val, 0, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()

    # 时辰名称与范围
    shichen_name = SHICHEN_NAMES[shichen_idx]
    h_s, h_e = SHICHEN_HOURS[shichen_idx]
    if h_s == 23:
        range_str = "23:00-00:59（夜子时）"
    else:
        range_str = f"{h_s:02d}:00-{h_e:02d}:59"

    out = []
    out.append("=" * 40)
    out.append("四柱八字排盘结果")
    out.append("=" * 40)
    out.append(f"阳历：{y}-{m:02d}-{d:02d}")
    out.append(f"时辰：{shichen_name}时（{range_str}）")
    out.append(f"农历：{lunar.toString()}")
    out.append(f"生肖：{lunar.getYearShengXiao()}")
    out.append(f"八字：{ec.toString()}")
    out.append(f"性别：{'男' if gender == 1 else '女'}")
    out.append("")

    # 四柱表
    out.append("【四柱】")
    out.append(f"年柱：{ec.getYear()}（干:{ec.getYearGan()} 支:{ec.getYearZhi()}）")
    out.append(f"月柱：{ec.getMonth()}（干:{ec.getMonthGan()} 支:{ec.getMonthZhi()}）")
    out.append(f"日柱：{ec.getDay()}（干:{ec.getDayGan()} 支:{ec.getDayZhi()}）★日主:{ec.getDayGan()}")
    out.append(f"时柱：{ec.getTime()}（干:{ec.getTimeGan()} 支:{ec.getTimeZhi()}）")
    out.append("")

    # 十神
    out.append("【十神】（以日干为基准）")
    out.append(f"年干：{ec.getYearShiShenGan()}")
    out.append(f"月干：{ec.getMonthShiShenGan()}")
    out.append(f"日干：日主")
    out.append(f"时干：{ec.getTimeShiShenGan()}")
    out.append("")

    # 藏干
    out.append("【藏干】")
    out.append(f"年支{ec.getYearZhi()}藏：{','.join(ec.getYearHideGan())}")
    out.append(f"月支{ec.getMonthZhi()}藏：{','.join(ec.getMonthHideGan())}")
    out.append(f"日支{ec.getDayZhi()}藏：{','.join(ec.getDayHideGan())}")
    out.append(f"时支{ec.getTimeZhi()}藏：{','.join(ec.getTimeHideGan())}")
    out.append("")

    # 纳音
    out.append("【纳音】")
    out.append(f"年柱：{ec.getYearNaYin()}")
    out.append(f"月柱：{ec.getMonthNaYin()}")
    out.append(f"日柱：{ec.getDayNaYin()}")
    out.append(f"时柱：{ec.getTimeNaYin()}")
    out.append("")

    # 大运
    out.append("【大运】")
    yun = ec.getYun(gender)
    direction = "顺排" if yun.isForward() else "逆排"
    out.append(f"大运方向：{direction}")
    out.append(f"起运：出生后{yun.getStartYear()}年{yun.getStartMonth()}月{yun.getStartDay()}日")
    out.append(f"起运阳历：{yun.getStartSolar().toYmd()}")
    dayuns = yun.getDaYun()
    for d in dayuns:
        if d.getIndex() < 10:
            out.append(f"  第{d.getIndex()+1}步：{d.getStartAge()}-{d.getEndAge()}岁（{d.getStartYear()}-{d.getEndYear()}）{d.getGanZhi()}")
    out.append("")

    # 当前大运（基于当前年份）
    import datetime
    current_year = datetime.date.today().year
    out.append(f"【当前大运（{current_year}年）】")
    found = False
    for d in dayuns:
        if d.getStartYear() <= current_year <= d.getEndYear():
            out.append(f"  当前大运：{d.getGanZhi()}（{d.getStartAge()}-{d.getEndAge()}岁，{d.getStartYear()}-{d.getEndYear()}）")
            found = True
            break
    if not found:
        out.append("  当前年份超出已排大运范围")
    out.append("")

    # 流年（近6年）
    out.append(f"【流年（{current_year-2}年-{current_year+3}年）】")
    for year in range(current_year - 2, current_year + 4):
        y_liu = Solar.fromYmd(year, 7, 1).getLunar()
        out.append(f"  {year}年：{y_liu.getYearInGanZhiByLiChun()}")

    print("\n".join(out))


if __name__ == "__main__":
    main()
