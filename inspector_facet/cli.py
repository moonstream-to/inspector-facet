import argparse
import json
from multiprocessing.sharedctypes import Value
import sys

from brownie import network

from .abi import project_abis
from .facets import facets_from_loupe, facets_from_moonworm_crawldata
from .inspector import inspect_diamond
from .version import VERSION


def main():
    parser = argparse.ArgumentParser(description="Inspector Facet")
    parser.add_argument("--version", action="version", version=VERSION)

    raw_data_group = parser.add_mutually_exclusive_group(required=True)
    raw_data_group.add_argument(
        "--network", help="Name of brownie network to connect to"
    )
    raw_data_group.add_argument(
        "-c",
        "--crawldata",
        help="Path to JSONL (JSON Lines) file containing moonworm crawl data for contract",
    )

    parser.add_argument("--address", required=False, help="Address of Diamond contract")

    parser.add_argument("-p", "--project", help="Path to brownie project")

    parser.add_argument(
        "--format",
        choices=["json", "human"],
        default="json",
        help="Format in which to print output",
    )

    args = parser.parse_args()

    abis = project_abis(args.project)

    facets = None
    if args.network is not None:
        if args.address is None:
            raise ValueError(
                "You must provide an address for the Diamond contract that you want to pull facet information for from the network"
            )
        facets = facets_from_loupe(args.network, args.address)
    elif args.crawldata is not None:
        facets = facets_from_moonworm_crawldata(args.crawldata)

    if facets is None:
        raise ValueError(
            "Could not reconstruct information about currently attached methods on Diamond"
        )

    result = inspect_diamond(facets, abis)

    if args.format == "json":
        json.dump(result, sys.stdout)
    elif args.format == "human":
        for address, address_result in result.items():
            print("- - -")
            print(f"Facet at address: {address}")
            print(f"Possible contracts: {', '.join(address_result['matches'])}")
            for contract_name in address_result["matches"]:
                misses = [
                    item
                    for item in address_result["misses"]
                    if item["contract"] == contract_name
                ]

                selectors = [
                    item
                    for item in address_result["selectors"]
                    if item["contract"] == contract_name
                ]

                print(f"{contract_name}:")
                print(f"\tMissing methods:")
                for item in misses:
                    print(
                        f"\t\tMissing selector: {item['selector']}, Function: {item['function']}"
                    )
                print(f"\tMounted selectors:")
                for item in selectors:
                    print(
                        f"\t\tSelector: {item['selector']}, Function: {item['function']}"
                    )
    else:
        raise ValueError(f"Unknown format: {args.format}")


if __name__ == "__main__":
    main()
