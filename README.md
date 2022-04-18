# Inspector Facet

<a href="https://media.giphy.com/media/14mgxYFJHXGmoo/giphy.gif" target="_blank"><img src="https://media.giphy.com/media/14mgxYFJHXGmoo/giphy.gif" /></a>

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
- [ ] From `DiamondCut` events crawled from the blockchain (using [`moonworm`](https://github.com/bugout-dev/moonworm)).

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

### Connecting to a blockchain

Internally, Inspector Facet uses [`brownie`](https://github.com/eth-brownie/brownie) to work with any
Ethereum-based blockchain. When you use `inspector-facet`, even with a `hardhat` project, `inspector-facet`
will still use `brownie` to interact with any blockchain.

Any `inspector-facet` command that calls out to a blockchain will take a `-n/--network` argument. The value
of this argument must be the name of a `brownie` network configured in your Python environment.

`brownie` is a dependency of `inspector-facet` and is automatically installed when you install `inspector-facet`.

To see a list of available `brownie` networks, activate the Python environment in which you installed
`inspector-facet` and run:

```bash
brownie networks list
```

The output will look like this (truncated for brevity):

```
$ brownie networks list

Brownie v1.17.2 - Python development framework for Ethereum

The following networks are declared:

Ethereum
  ├─Mainnet (Infura): mainnet
  ├─Ropsten (Infura): ropsten
  ├─Rinkeby (Infura): rinkeby
  ├─Goerli (Infura): goerli
  └─Kovan (Infura): kovan

Ethereum Classic
  ├─Mainnet: etc
  └─Kotti: kotti

Arbitrum
  └─Mainnet: arbitrum-main
...
```

To view the details for any particular network, use:

```bash
brownie networks modify $NETWORK
```

For example:

```
$ brownie networks modify mainnet

$ brownie networks modify mainnet
Brownie v1.17.2 - Python development framework for Ethereum

SUCCESS: Network 'Mainnet (Infura)' has been modified
  └─Mainnet (Infura)
    ├─id: mainnet
    ├─chainid: 1
    ├─explorer: https://api.etherscan.io/api
    ├─host: https://mainnet.infura.io/v3/$WEB3_INFURA_PROJECT_ID
    └─multicall2: 0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696
```

If you want to connect to this network, using Infura, all you have to do is set your `WEB3_INFURA_PROJECT_ID`
environment variable (get this information from your project dashboard on Infura) and set `--network mainnet`
when you invoke `inspector-facet`.

For networks which have publicly available nodes, it's even more straightforward:

```
$ brownie networks modify etc
Brownie v1.17.2 - Python development framework for Ethereum

SUCCESS: Network 'Mainnet' has been modified
  └─Mainnet
    ├─id: etc
    ├─chainid: 61
    ├─explorer: https://blockscout.com/etc/mainnet/api
    └─host: https://www.ethercluster.com/etc
```

You don't need any additional environment variables.

#### Adding a custom network

To add your own network, use the `brownie networks add` command.

The signature for this command is:

```
brownie networks add <label> <network-name> chainid=<chain ID for network> host=<JSON RPC endpoint> explorer=<API URL for blockchain explorer>
```

The `<label>` is purely for organizational purposes and can be set to whatever string you want.

For example, if you wanted to add the public Polygon RPC service as a network, you would do:

```bash
brownie networks add Polygon matic chainid=137 host=https://polygon-rpc.com explorer=https://api.polygonscan.com/api
```

### Support

You can get help in any of the following ways:

1. [File an issue](https://github.com/bugout-dev/inspector-facet/issues/new)
2. Ask for help on [Moonstream Discord](https://discord.gg/K56VNUQGvA)
