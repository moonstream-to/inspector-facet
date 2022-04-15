import argparse
import json
import os

from brownie import network

from .abi import project_abis
from .inspector import inspect_diamond
from .DiamondLoupeFacet import add_default_arguments

def main():
    parser = argparse.ArgumentParser(description="Inspector Facet")
    add_default_arguments(parser, transact=False)
    parser.add_argument("-p", "--project", required=True, help="Path to brownie project")

    args = parser.parse_args()

    abis = project_abis(args.project)

    network.connect(args.network)

    result = inspect_diamond(args.address, abis)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
