# Inspector Facet

A tool that allows you to inspect deployed [EIP-2535 Diamond proxy](https://eips.ethereum.org/EIPS/eip-2535)
contracts from your command line.

Inspector Facet was inspired by [Louper.dev](https://louper.dev/) ([GitHub](https://github.com/mark3labs/louper-v2)).

Inspector Facet uses side information about facet ABIs to match the selectors that a Diamond proxy
is serving to human-understandable information about the facets and the functions.

We support side information obtained from:

- [x] [brownie](https://github.com/eth-brownie/brownie) build artifacts
- [ ] [hardhat](https://hardhat.org/) build artifacts
- [ ] Etherscan/Polygonscan/etc.

We support Diamond introspection:

- [x] Using the `DiamondLoupeFacet` interface
- [ ] From `DiamondCut` events crawled from the blockchain (using the [Moonstream API](https://moonstream.to)).

### Installation

Inspector Facet is written in Python 3 and is distributed using PyPI: https://pypi.org/project/inspector-facet/

To install Inspector Facet, run:

```bash
pip install inspector-facet
```

### Usage

```bash
inspector-facet --help
```

<a href="https://asciinema.org/a/487856" target="_blank"><img src="https://asciinema.org/a/487856.svg" /></a>

To use Inspector Facet with:

#### A `brownie` project

The following command produces human-readable output:

```bash
inspector-facet \
    --network <brownie network name for blockchain> \
    --address <address of diamond contract> \
    --project <path to brownie project (should contain build artifacts in build/contracts)> \
    --format human
```

The following command produces JSON output and can be used to inspect a Diamond contract programatically
(e.g. as part of a CI/CD pipeline):
```bash
inspector-facet \
    --network <brownie network name for blockchain> \
    --address <address of diamond contract> \
    --project <path to brownie project (should contain build artifacts in build/contracts)> \
    --format json
```

### Support

You can get help in any of the following ways:

1. [File an issue](https://github.com/bugout-dev/inspector-facet/issues/new)
2. Ask for help on [Moonstream Discord](https://discord.gg/K56VNUQGvA)
