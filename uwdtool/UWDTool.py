import argparse

from Common import print_err, HELP_STR
from Unpacker import Unpacker
from Packer import Packer
from Inspector import Inspector


class Main:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog = "uwdtool",
            description = HELP_STR,
            formatter_class = argparse.RawTextHelpFormatter
        )
        g = self.parser.add_mutually_exclusive_group()

        g.add_argument("-p", "--pack", action="store_true", help="packing files in input-path directory")
        g.add_argument("-u", "--unpack", action="store_true", help="unpacking input-path file to output-path directory")
        g.add_argument("-isp", "--inspect", action="store_true", help="show file information list of input-path file")

        self.parser.add_argument("-i", dest="ARG_INPUT", help="input path")
        self.parser.add_argument("-o", dest="ARG_OUTPUT", help="output path")

    def main(self):
        args = self.parser.parse_args()

        if args.pack:
            pass  # TODO Packer(args.ARG_INPUT, args.ARG_OUTPUT).pack()
        elif args.unpack:
            Unpacker(args.ARG_INPUT, args.ARG_OUTPUT).unpack()
        elif args.inspect:
            Inspector(args.ARG_INPUT).inspect()
        else:
            print_err("Please select option.")


if __name__ == "__main__":
    Main().main()
