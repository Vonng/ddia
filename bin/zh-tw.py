#!/usr/bin/env python3
import os, sys, opencc
import re

def process_urls(text, src_folder, dst_folder):
    """处理 Markdown 中的相对 URL"""
    # 定义需要处理的页面路径（不带.md后缀）
    page_paths = [
        '/ch1', '/ch2', '/ch3', '/ch4', '/ch5', '/ch6',
        '/ch7', '/ch8', '/ch9', '/ch10', '/ch11', '/ch12', '/ch13',
        '/part-i', '/part-ii', '/part-iii', 
        '/preface', '/glossary', '/colophon'
    ]
    
    # 对每个页面路径进行替换
    for page_path in page_paths:
        # 匹配 Markdown 链接格式 [text](page_path) 或 [text](page_path#anchor)
        pattern = rf'\[([^\]]*)\]\(([^)]*)({re.escape(page_path)})(#[^)]*)?\)'
        # 替换为添加 /tw 前缀的版本
        def replace_func(match):
            text_part = match.group(1)
            folder_part = match.group(2) or ''
            page_part = match.group(3)
            anchor_part = match.group(4) or ''
            if not folder_part:
                return f'[{text_part}](/tw{page_part}{anchor_part})'            # 默认中文版本，没有 /zh 前缀，直接在前面添加 /tw 前缀
            elif folder_part[1:] == src_folder:
                return f'[{text_part}](/{dst_folder}{page_part}{anchor_part})'  # 其它中文版本，有类似 /v1 的前缀，根据输入参数进行替换
            else:
                text = f'[{text_part}]({folder_part}{page_part}{anchor_part})'
                print(f'unknown folder part in: {text}, keep it unchanged')
                return text
        text = re.sub(pattern, replace_func, text)
    
    return text

def convert_file(src_filepath, dst_filepath, src_folder, dst_folder, cfg='s2twp.json'):
    print("convert %s to %s" % (src_filepath, dst_filepath))
    converter = opencc.OpenCC(cfg)
    with open(src_filepath, "r", encoding='utf-8') as src, open(dst_filepath, "w+", encoding='utf-8') as dst:
        dst.write("\n".join(
            process_urls(
                converter.convert(line.rstrip())
                    .replace('一箇', '一個')
                    .replace('髮送', '傳送')
                    .replace('髮布', '釋出')
                    .replace('髮生', '發生')
                    .replace('髮出', '發出')
                    .replace('嚐試', '嘗試')
                    .replace('線上性一致', '在線性一致')    # 优先按"在线"解析了？
                    .replace('復雜', '複雜')
                    .replace('討論瞭', '討論了')
                    .replace('瞭解釋', '了解釋')
                    .replace('瞭如', '了如')                # 引入了如, 實現了如, 了如何, 了如果, 了如此
                    .replace('了如指掌', '瞭如指掌')        # 针对上一行的例外情况
                    .replace('明瞭', '明了')                # 闡明了, 聲明了, 指明了
                    .replace('倒黴', '倒楣')
                    .replace('區域性性', '區域性')
                    .replace('下麵條件', '下面條件')        # 优先按"面条"解析了？
                    .replace('當日志', '當日誌')            # 优先按"当日"解析了？
                    .replace('真即時間', '真實時間')        # 优先按"实时"解析了？
                    .replace('面向物件', '物件導向'),
                src_folder, dst_folder
            )
            for line in src))

def convert(zh_folder, tw_folder):
    home = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..'))
    zh_dirpath = os.path.join(home, 'content', zh_folder)
    tw_dirpath = os.path.join(home, 'content', tw_folder)
    for file in os.listdir(zh_dirpath):
        if file.endswith('.md'):
            zh_filepath = os.path.join(zh_dirpath, file)
            tw_filepath = os.path.join(tw_dirpath, file)
            convert_file(zh_filepath, tw_filepath, zh_folder, tw_folder)

if __name__ == '__main__':
    print(sys.argv)
    convert('zh', 'tw')
    convert('v1', 'v1_tw')
