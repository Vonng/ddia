#!/usr/bin/env python3
import os, sys, opencc
import re

def process_urls(text):
    """处理 Markdown 中的相对 URL，在前面添加 /tw 前缀"""
    # 定义需要处理的页面路径（不带.md后缀）
    page_paths = [
        '/ch1', '/ch2', '/ch3', '/ch4', '/ch5', '/ch6',
        '/ch7', '/ch8', '/ch9', '/ch10', '/ch11', '/ch12',
        '/part-i', '/part-ii', '/part-iii', 
        '/preface', '/glossary', '/colophon'
    ]
    
    # 对每个页面路径进行替换
    for page_path in page_paths:
        # 匹配 Markdown 链接格式 [text](page_path) 或 [text](page_path#anchor)
        pattern = rf'\[([^\]]*)\]\(({re.escape(page_path)})(#[^)]*)?\)'
        # 替换为添加 /tw 前缀的版本
        def replace_func(match):
            text_part = match.group(1)
            path_part = match.group(2)
            anchor_part = match.group(3) or ''
            return f'[{text_part}](/tw{path_part}{anchor_part})'
        text = re.sub(pattern, replace_func, text)
    
    return text

def convert(src_path, dst_path, cfg='s2twp.json'):
    converter = opencc.OpenCC(cfg)
    with open(src_path, "r", encoding='utf-8') as src, open(dst_path, "w+", encoding='utf-8') as dst:
        dst.write("\n".join(
            process_urls(
                converter.convert(line.rstrip()).replace('(img/', '(../img/')
                    .replace('髮送', '傳送')
                    .replace('髮布', '釋出')
                    .replace('髮生', '發生')
                    .replace('髮出', '發出')
                    .replace('嚐試', '嘗試')
                    .replace('線上性一致', '在線性一致')    # 优先按"在线"解析了？
                    .replace('復雜', '複雜')
                    .replace('討論瞭', '討論了')
                    .replace('倒黴', '倒楣')
                    .replace('區域性性', '區域性')
                    .replace('下麵條件', '下面條件')        # 优先按"面条"解析了？
                    .replace('當日志', '當日誌')            # 优先按"当日"解析了，没有考虑后面的"日志"？
                    .replace('真即時間', '真實時間')        # 优先按"实时"解析了，没有考虑前面的"真实"？
                    .replace('面向物件', '物件導向')
            )
            for line in src))
    print("convert %s to %s" % (src_path, dst_path))

if __name__ == '__main__':
    print(sys.argv)
    home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..'))
    zh_dir = os.path.join(home, 'content', 'zh')
    tw_dir = os.path.join(home, 'content', 'tw')
    os.chdir(zh_dir)
    for f in os.listdir(zh_dir):
        if f.endswith('.md'):
            dst = os.path.join(tw_dir, f)
            convert(f, dst)
