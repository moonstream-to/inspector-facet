import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from .abi import project_abis
from .facets import (
    events_from_moonworm_crawldata,
    facets_from_loupe,
    facets_from_events,
    CUT_ACTION_ADD,
    CUT_ACTION_REMOVE,
    CUT_ACTION_REPLACE,
)
from .inspector import inspect_diamond
from .version import VERSION


def print_timeline_event_for_human(
    result: Dict[str, Any],
    maybe_previous_result: Optional[Dict[str, Any]],
    event: Dict[str, Any],
) -> None:
    print(
        f"# DiamondCut at block number {event['blockNumber']} (transaction hash: {event['transactionHash']})"
    )

    cuts = event["args"]["_diamondCut"]
    initializer_address = event["args"]["_init"]
    calldata = event["args"]["_calldata"]
    print(
        f"Cuts were made with initializer: {initializer_address} (calldata: {calldata})"
    )

    print("## Modifications")
    for cut in cuts:
        facet_address = cut[0]
        action = cut[1]
        selectors = cut[2]

        if facet_address not in result:
            print(f"### Facet at address: {facet_address}")
            print("This address did not match any of the given contracts.")
        else:
            print(
                f"This address could be one of the following contracts: {' or '.join(result[facet_address]['matches'])}."
            )

        action_text = "added"
        if action == CUT_ACTION_REMOVE:
            action_text = "removed"
        elif action == CUT_ACTION_REPLACE:
            action_text = "replaced"

        print(f"The following selectors were {action_text} on the Diamond:")
        all_selectors: List[Tuple[str, str, str]] = [
            (item["contract"], item["function"], item["selector"])
            for known_facet_address in result
            for item in result[known_facet_address]["selectors"]
        ]
        if maybe_previous_result is not None:
            all_selectors += [
                (item["contract"], item["function"], item["selector"])
                for known_facet_address in maybe_previous_result
                for item in maybe_previous_result[known_facet_address]["selectors"]
            ]
        all_selectors = list(set(all_selectors))

        selector_matches: Dict[str, List[Tuple[str, str]]] = {}
        for selector in selectors:
            selector_matches[selector] = []
            for contract, function, known_selector in all_selectors:
                if selector == known_selector:
                    selector_matches[selector].append((contract, function))

        for selector in selectors:
            if not selector_matches[selector]:
                print(f"\t{selector}")
            else:
                snippets = [
                    f"{function} from {contract}"
                    for contract, function in selector_matches[selector]
                ]
                print(f"\t{selector} - {' or '.join(snippets)}")
    print("## Cumulative functionality")
    print_result_for_human(result)


def print_result_for_human(result: Dict[str, Any]) -> None:
    for address, address_result in result.items():
        print(f"### Facet at address: {address}")
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
    else:
        if args.crawldata is None:
            raise ValueError("--timeline mode can only be used with --crawldata")

        diamond_cut_events = events_from_moonworm_crawldata(args.crawldata)
        results_with_diffs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        for i, event in enumerate(diamond_cut_events):
            intermediate_result = inspect_diamond(
                facets_from_events(diamond_cut_events[: i + 1]), abis
            )
            results_with_diffs.append((intermediate_result, event))

        if args.format == "json":
            json.dump(results_with_diffs, sys.stdout)
        elif args.format == "human":
            for i, item in enumerate(results_with_diffs):
                result, event = item
                maybe_previous_result: Optional[Dict[str, Any]] = None
                if i > 0:
                    maybe_previous_result = results_with_diffs[i - 1][0]
                print_timeline_event_for_human(result, maybe_previous_result, event)
        else:
            raise ValueError(f"Unknown format: {args.format}")


if __name__ == "__main__":
    main()
