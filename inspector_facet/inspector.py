from typing import Any, cast, Dict, List, Tuple

from .abi import encode_function_signature
from . import DiamondLoupeFacet

UNKNOWN_FUNCTION = "<unknown function>"
UNKNOWN_CONTRACT = "<unknown contract>"


def inspect_diamond(address: str, abis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inspects the Diamond proxy on the given network at the given address against the given ABIs. Matches
    each facet address to an ABI and describes which of the functions in that ABI are loaded onto the contract.

    Assumes that brownie is connected to a network.
    """
    contract = DiamondLoupeFacet.DiamondLoupeFacet(address)
    contract_selectors: Dict[str, Dict[str, str]] = {}
    for name, abi in abis.items():
        contract_selectors[name] = {}
        for item in abi:
            item_name = item.get("name", UNKNOWN_FUNCTION)
            function_selector = encode_function_signature(item)
            if function_selector is not None:
                contract_selectors[name][function_selector] = item_name

    selector_index: Dict[str, List[str]] = {}
    for contract_name, selectors in contract_selectors.items():
        for selector in selectors:
            if selector_index.get(selector) is None:
                selector_index[selector] = []
            selector_index[selector].append(contract_name)

    mounted_facets = contract.facets()
    facets: Dict[str, List[str]] = {}
    for address, selectors in mounted_facets:
        facets[address] = [str(selector) for selector in selectors]

    facet_matches: Dict[str, Dict[str, int]] = {}
    max_matches: Dict[str, int] = {}
    for address, selectors in facets.items():
        facet_matches[address] = {}
        for selector in selectors:
            selector_contracts = selector_index.get(selector)
            if selector_contracts is not None:
                for contract_name in selector_contracts:
                    if facet_matches[address].get(contract_name) is None:
                        facet_matches[address][contract_name] = 0
                    facet_matches[address][contract_name] += 1
        max_matches[address] = max(value for _, value in facet_matches[address].items())

    result: Dict[str, Dict[str, Any]] = {}
    for address, selectors in facets.items():
        address_result: Dict[str, Any] = {}
        address_result["matches"] = [
            match
            for match, score in facet_matches[address].items()
            if score == max_matches[address]
        ]
        address_result["selectors"] = {
            selector: [
                {
                    "contract": contract_name,
                    "function": contract_selectors[contract_name][selector],
                }
                for contract_name in address_result["matches"]
                if selector in contract_selectors[contract_name]
            ]
            for selector in selectors
        }
        result[address] = address_result

    return result
