from typing import Any, cast, Dict, List, Tuple

from .abi import encode_function_signature
from . import DiamondLoupeFacet

UNKNOWN_FUNCTION = "<unknown function>"
UNKNOWN_CONTRACT = "<unknown contract>"


def inspect_diamond(
    facets: Dict[str, List[str]], abis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Inspects the Diamond proxy on the given network at the given address against the given ABIs. Matches
    each facet address to an ABI and describes which of the functions in that ABI are loaded onto the contract.

    Assumes that brownie is connected to a network.
    """
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

    facet_recalls: Dict[str, Dict[str, float]] = {}
    facet_precisions: Dict[str, Dict[str, int]] = {}
    max_recall: Dict[str, float] = {}
    for address, selectors in facets.items():
        if len(selectors) == 0:
            continue
        # Recall
        facet_recalls[address] = {}
        for selector in selectors:
            selector_contracts = selector_index.get(selector)
            if selector_contracts is not None:
                for contract_name in selector_contracts:
                    if facet_recalls[address].get(contract_name) is None:
                        facet_recalls[address][contract_name] = 0.0
                    facet_recalls[address][contract_name] += 1.0
        for contract_name in facet_recalls[address]:
            facet_recalls[address][contract_name] /= len(selectors)

        max_recall[address] = max([0] + [value for _, value in facet_recalls[address].items()])

        # Precision
        facet_precisions[address] = {}
        for contract_name, selectors in contract_selectors.items():
            if len(selectors) == 0:
                facet_precisions[address][contract_name] = 0.0
                continue
            facet_precisions[address][contract_name] = 0.0
            for selector in selectors:
                if selector in facets[address]:
                    facet_precisions[address][contract_name] += 1.0
            facet_precisions[address][contract_name] /= len(selectors)

    result: Dict[str, Dict[str, Any]] = {}
    for address, selectors in facets.items():
        address_result: Dict[str, Any] = {}
        max_recall_contracts = [
            contract_name
            for contract_name in contract_selectors
            if facet_recalls[address].get(contract_name, 0.0) == max_recall[address]
        ]
        max_precision_for_max_recall_contracts = max(
            precision
            for contract_name, precision in facet_precisions[address].items()
            if contract_name in max_recall_contracts
        )
        address_result["matches"] = [
            contract_name
            for contract_name in max_recall_contracts
            if facet_precisions[address][contract_name]
            == max_precision_for_max_recall_contracts
        ]

        address_result["misses"] = [
            {
                "contract": contract_name,
                "selector": selector,
                "function": function_name,
            }
            for contract_name in address_result["matches"]
            for selector, function_name in contract_selectors[contract_name].items()
            if selector not in facets[address]
        ]

        address_result["selectors"] = [
            {
                "contract": contract_name,
                "selector": selector,
                "function": contract_selectors[contract_name][selector],
            }
            for contract_name in address_result["matches"]
            for selector in selectors
            if selector in contract_selectors[contract_name]
        ]

        result[address] = address_result

    return result
