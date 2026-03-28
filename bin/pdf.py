#!/usr/bin/env python3
"""PDF generation from Markdown using pandoc + LaTeX."""

import os
import re
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional, List, Dict
import shutil
import importlib.util


CHAPTER_ORDER = [
    "_index.md",
    "preface.md",
    "part-i.md",
    "ch1.md", "ch2.md", "ch3.md", "ch4.md",
    "part-ii.md",
    "ch5.md", "ch6.md", "ch7.md", "ch8.md", "ch9.md",
    "part-iii.md",
    "ch10.md", "ch11.md", "ch12.md", "ch13.md", "ch14.md",
    "colophon.md", "glossary.md",
]

DEFAULT_FONTS = {
    "mainfont": "PingFang SC",
    "sansfont": "Heiti SC",
}

YAML_FRONT_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
TITLE_RE = re.compile(r'^title:\s*["\']?([^"\'\n]+)["\']?\s*$', re.MULTILINE)
CHAPTER_NUM_RE = re.compile(r'^\d+\.\s*')
CHAPTER_FILE_RE = re.compile(r'^ch(\d+)\.md$')
CALLOUT_RE = re.compile(r'^> \[!(NOTE|TIP|WARNING|CAUTION|DANGER)\] ', re.MULTILINE)


def convert_pdf_markdown(text: str, filename: str) -> str:
    """PDF-specific markdown conversions."""
    text = _convert_callouts(text)
    text = _add_title_heading(text, filename)
    return text


def _convert_callouts(text: str) -> str:
    """Convert [!NOTE], [!TIP], etc. to Chinese."""
    def replace_callout(match):
        callout_type = match.group(1).lower()
        title_map = {
            'note': '注',
            'tip': '提示',
            'warning': '警告',
            'caution': '注意',
            'danger': '危险'
        }
        return f"**{title_map.get(callout_type, callout_type)}**: "

    text = CALLOUT_RE.sub(replace_callout, text)
    text = re.sub(r'^> ?', '', text, flags=re.MULTILINE)
    return text


def _add_title_heading(text: str, filename: str) -> str:
    """Add title heading from YAML frontmatter."""
    match = YAML_FRONT_RE.match(text)
    if match:
        frontmatter = match.group(1)
        title_match = TITLE_RE.search(frontmatter)
        if title_match:
            title = title_match.group(1)
            body = text[match.end():]
            clean_title = CHAPTER_NUM_RE.sub('', title)

            if CHAPTER_FILE_RE.match(filename):
                heading = f"# {clean_title}"
            else:
                heading = f"## {clean_title}"

            return f"---\n{frontmatter}\n---\n\n{heading}\n\n{body}"
    return text


def check_cmd(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def get_available_engine() -> Optional[str]:
    if check_cmd("xelatex"):
        return "xelatex"
    if check_cmd("lualatex"):
        return "lualatex"
    return None


def check_dependencies() -> List[str]:
    missing = []
    if not check_cmd("pandoc"):
        missing.append("pandoc")
    if not get_available_engine():
        missing.append("xelatex or lualatex (LaTeX engine)")
    return missing


def preprocess_markdown(input_dir: Path, output_dir: Path) -> None:
    script_dir = Path(__file__).parent
    preprocess_script = script_dir / "preprocess-epub.py"
    spec = importlib.util.spec_from_file_location("preprocess_epub", preprocess_script)
    if spec is None:
        raise RuntimeError("Failed to load preprocess module")
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("Failed to load preprocess module loader")
    spec.loader.exec_module(module)

    output_dir.mkdir(parents=True, exist_ok=True)
    md_files = sorted(input_dir.glob("*.md"))

    print(f"Preprocessing {len(md_files)} files...")
    for md_file in md_files:
        temp_output = output_dir / "tmp_preprocess.md"
        module.process_file(str(md_file), str(temp_output))

        with open(temp_output, 'r', encoding='utf-8') as f:
            content = f.read()

        content = convert_pdf_markdown(content, md_file.name)

        with open(output_dir / md_file.name, 'w', encoding='utf-8') as f:
            f.write(content)

        temp_output.unlink()


def generate_pdf(
    temp_dir: Path,
    output_file: Path,
    metadata_file: Optional[str],
    engine: str,
    fonts: Dict[str, str],
    margin: str = "1in",
) -> None:
    chapters = [str(temp_dir / ch) for ch in CHAPTER_ORDER if (temp_dir / ch).exists()]

    if not chapters:
        raise ValueError("No valid chapter files found")

    script_dir = Path(__file__).parent
    header_file = script_dir / "header.tex"

    cmd = [
        "pandoc", "-o", str(output_file),
        "--metadata-file", metadata_file or "",
        "-H", str(header_file),
        "--toc",
        "--toc-depth=2",
        "--top-level-division=chapter",
        "--file-scope",
        f"--pdf-engine={engine}",
        f"-V geometry:margin={margin}",
        "-V linestretch=1.5",
        "-V book=true",
        "-V classoption=openany",
        "-V mainfont=PingFang SC",
    ]
    cmd = [c for c in cmd if c]
    cmd.extend(chapters)

    print(f"Generating PDF with {engine}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"PDF generation failed: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Generate PDF from Markdown")
    parser.add_argument("-i", "--input", default="content/zh", help="Input directory")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    parser.add_argument("-m", "--metadata", help="Metadata YAML file")
    parser.add_argument("-e", "--engine", choices=["xelatex", "lualatex"], help="PDF engine")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep temp files")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    input_dir = project_root / args.input
    output_dir = project_root / args.output
    temp_dir = output_dir / "temp"

    missing = check_dependencies()
    if missing:
        print("Error: Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall: brew install pandoc && brew install --cask mactex")
        sys.exit(1)

    detected_engine = get_available_engine()
    if detected_engine is None:
        print("Error: No PDF engine available")
        sys.exit(1)

    engine = args.engine or detected_engine
    metadata = args.metadata or str(project_root / "metadata.yaml")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ddia.pdf"
    output_file.unlink(missing_ok=True)

    preprocess_markdown(input_dir, temp_dir)
    generate_pdf(temp_dir, output_file, metadata, engine, DEFAULT_FONTS)

    if not args.no_cleanup and temp_dir.exists():
        shutil.rmtree(temp_dir)

    print(f"PDF created: {output_file}")


if __name__ == "__main__":
    main()
