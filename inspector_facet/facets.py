"""
Various methods to pull information about the facet-method correspondence for a deployed Diamond contract.
"""
from typing import Dict, List

from brownie import network

from . import DiamondLoupeFacet


def facets_from_loupe(network_id: str, address: str) -> Dict[str, List[str]]:
    network.connect(network_id)
    contract = DiamondLoupeFacet.DiamondLoupeFacet(address)
    mounted_facets = contract.facets()
    facets: Dict[str, List[str]] = {}
    for address, selectors in mounted_facets:
        facets[address] = [str(selector) for selector in selectors]
    return facets
