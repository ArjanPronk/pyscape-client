#!/usr/bin/python3

import sys

from pyscape.core import Pyscape
from pyscape.util.flagindex import FlagIndex
from pyscape.util.preset_handler import PresetHandler
from pyscape.util import custom
from pyscape.util import credentials
from pyscape.util import output

from src.cli import *

def main():

    parser = build_parser()
    args = parser.parse_args()
    preset = get_preset(args)

    # load API credentials
    with open('keys.json', 'r') as k:
        creds = credentials.load(k)

    with open('data/bitflags.json') as b:
        flag_index = FlagIndex(b)

    with open('data/defaults.json') as d:
        ph = PresetHandler(d, flag_index)

    url = args.source
    pys = Pyscape(*creds)
    pys.set_reporting(True)
    ph.set_preset(preset)

    if args.command != 'bulk-metrics' and \
       args.command != 'ose-style':
        data = pys.query(url, ph.get_args())
    elif args.command == 'bulk-metrics':
        # replace this call with custom.py 
        urls = []
        with open(args.source, 'r') as s:
            for line in s:
                urls.append(line.rstrip())
        data = custom.get_bulk_metrics(pys, urls, ph.get_args())
    elif args.command == 'ose-style':
        data = pys.query(url, ph.get_args())
        print("Writing OSE-style CSV.")
        with open(args.dest, 'w') as outfile:
            output.ose_style(outfile, data)
        sys.exit()

    # write output
    print('Writing file.')
    with open(args.dest, 'w') as outfile:
        if args.json:
            output.to_json(outfile, data)
        elif args.csv:
            output.to_csv(outfile, ph, preset, data)

if __name__ == '__main__':
    sys.exit(main())