"""Convert zh-cn to zh-tw
Refer to https://github.com/BYVoid/OpenCC
"""
import click
import opencc

from pathlib import Path
from pprint import pprint


@click.group()
def cli():
    pass


def convert(infile: str, outfile: str, cfg: str):
    """read >> convert >> write file
    Args:
        infile (str): input file
        outfile (str): output file
        cfg (str): config
    """
    converter = opencc.OpenCC(cfg)
    with open(infile, "r") as inf, open(outfile, "w+") as outf:
        outf.write("\n".join(converter.convert(line) for line in inf))
    print(f"Convert to {outfile}")


@cli.command()
@click.option("-i", "--input", "infile", required=True)
@click.option("-o", "--output", "outfile", required=True)
@click.option("-c", "--config", "cfg", required=True, default="s2twp.json")
def file(infile: str, outfile: str, cfg: str):
    """read >> convert >> write file
    Args:
        infile (str): input file
        outfile (str): output file
        cfg (str): config
    """
    convert(infile, outfile, cfg)


@cli.command()
@click.option("-i", "--input", "infolder", required=True)
@click.option("-o", "--output", "outfolder", required=True)
@click.option("-c", "--config", "cfg", required=True, default="s2twp.json")
def repo(infolder, outfolder, cfg):
    if not Path(outfolder).exists():
        Path(outfolder).mkdir(parents=True)
        print(f"Create {outfolder}")
    infiles = Path(infolder).resolve().glob("*.md")
    pair = [
        {"infile": str(infile), "outfile": str(Path(outfolder).resolve() / infile.name)}
        for idx, infile in enumerate(infiles)
    ]
    for p in pair:
        convert(p["infile"], p["outfile"], cfg)


if __name__ == "__main__":
    cli()
