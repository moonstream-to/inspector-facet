"""
Various methods to pull information about the facet-method correspondence for a deployed Diamond contract.
"""
import json
from typing import Any, Dict, List

from brownie import network

from . import DiamondLoupeFacet


CUT_ACTION_ADD = 0
CUT_ACTION_REPLACE = 1
CUT_ACTION_REMOVE = 2


def facets_from_loupe(network_id: str, address: str) -> Dict[str, List[str]]:
    network.connect(network_id)
    contract = DiamondLoupeFacet.DiamondLoupeFacet(address)
    mounted_facets = contract.facets()
    facets: Dict[str, List[str]] = {}
    for address, selectors in mounted_facets:
        facets[address] = [str(selector) for selector in selectors]
    return facets


def events_from_moonworm_crawldata(crawldata_jsonl: str) -> List[Dict[str, Any]]:
    diamond_cut_events: List[Dict[str, Any]] = []
    with open(crawldata_jsonl, "r") as ifp:
        for line in ifp:
            crawl_item = json.loads(line)
            if crawl_item.get("event", "") == "DiamondCut":
                diamond_cut_events.append(crawl_item)
    return diamond_cut_events


def facets_from_events(
    diamond_cut_events: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    """
    Accepts a JSON Lines file, containing a separate JSON object on each line as produced by `moonworm watch`.

    Scans this file for `DiamondCut` events and reconstructs the facet attachments onto the crawled
    Diamond contract from those events.
    """
    raw_facets: Dict[str, List[str]] = {}
    selector_index: Dict[str, str] = {}
    for event in diamond_cut_events:
        cut_items = event["args"]["_diamondCut"]
        for item in cut_items:
            facet_address = item[0]
            action = item[1]
            selectors = item[2]

            if raw_facets.get(facet_address) is None:
                raw_facets[facet_address] = []

            if action == CUT_ACTION_ADD:
                raw_facets[facet_address].extend(selectors)
                for selector in selectors:
                    selector_index[selector] = facet_address
            elif action == CUT_ACTION_REPLACE:
                raw_facets[facet_address].extend(selectors)
                for selector in selectors:
                    old_facet = selector_index[selector]
                    raw_facets[old_facet].remove(selector)
                    selector_index[selector] = facet_address
            elif action == CUT_ACTION_REMOVE:
                for selector in selectors:
                    # Users can remove methods using the 0 address as the facet addres. That necessitates
                    # this correspondence.
                    actual_facet_address = selector_index[selector]
                    raw_facets[actual_facet_address].remove(selector)
                    del selector_index[selector]

    facets = {
        facet_address: selectors
        for facet_address, selectors in raw_facets.items()
        if selectors
    }

    return facets
