#!/usr/bin/env python3
import os, sys, opencc

def convert(src_path, dst_path, cfg='s2twp.json'):
    converter = opencc.OpenCC(cfg)
    with open(src_path, "r", encoding='utf-8') as src, open(dst_path, "w+", encoding='utf-8') as dst:
        dst.write("\n".join(
            converter.convert(line.rstrip()).replace('(img/', '(../img/')
                .replace('髮送', '傳送')
                .replace('髮布', '釋出')
                .replace('髮生', '發生')
                .replace('髮出', '發出')
                .replace('嚐試', '嘗試')
                .replace('線上性一致', '在線性一致')    # 优先按“在线”解析了？
                .replace('復雜', '複雜')
                .replace('討論瞭', '討論了')
                .replace('倒黴', '倒楣')
                .replace('區域性性', '區域性')
                .replace('下麵條件', '下面條件')        # 优先按“面条”解析了？
                .replace('當日志', '當日誌')            # 优先按“当日”解析了，没有考虑后面的“日志”？
                .replace('真即時間', '真實時間')        # 优先按“实时”解析了，没有考虑前面的“真实”？
                .replace('面向物件', '物件導向')
                for line in src))
    print("convert %s to %s" % (src_path, dst_path))

if __name__ == '__main__':
    print(sys.argv)
    home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..'))
    os.chdir(home)
    for f in os.listdir():
        if f.endswith('.md'):
            convert(f, "zh-tw/" + f)
