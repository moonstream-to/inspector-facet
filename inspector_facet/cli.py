import argparse
import json
import sys
from typing import Any, Dict

from .abi import project_abis
from .facets import (
    events_from_moonworm_crawldata,
    facets_from_loupe,
    facets_from_events,
)
from .inspector import inspect_diamond
from .version import VERSION


def print_result_for_human(result: Dict[str, Any]) -> None:
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
                print(f"\t\tSelector: {item['selector']}, Function: {item['function']}")


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

    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Produce a timeline view of the changes to the Diamond contract (can only be used with --crawldata)",
    )

    args = parser.parse_args()

    abis = project_abis(args.project)

    if not args.timeline:
        facets = None
        if args.network is not None:
            if args.address is None:
                raise ValueError(
                    "You must provide an address for the Diamond contract that you want to pull facet information for from the network"
                )
            facets = facets_from_loupe(args.network, args.address)
        elif args.crawldata is not None:
            diamond_cut_events = events_from_moonworm_crawldata(args.crawldata)
            facets = facets_from_events(diamond_cut_events)

        if facets is None:
            raise ValueError(
                "Could not reconstruct information about currently attached methods on Diamond"
            )

        result = inspect_diamond(facets, abis)

        if args.format == "json":
            json.dump(result, sys.stdout)
        elif args.format == "human":
            print_result_for_human(result)
        else:
            raise ValueError(f"Unknown format: {args.format}")


if __name__ == "__main__":
    main()
