"""Convert zh-cn to zh-tw
Refer to https://github.com/BYVoid/OpenCC
"""
import click
import opencc


@click.command()
@click.option("-i", "--input", "infile", required=True)
@click.option("-o", "--output", "outfile", required=True)
@click.option("-c", "--config", "cfg", required=True, default="s2twp.json")
def main(infile, outfile, cfg):
    converter = opencc.OpenCC(cfg)
    with open(infile, "r") as inf, open(outfile, "w+") as outf:
        data = inf.readlines()
        data = list(map(converter.convert, data))
        outf.writelines(data)


if __name__ == "__main__":
    main()
