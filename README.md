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

Inspector Facet can build a complete audit log of all Diamond-related operations on an EIP2535 proxy
contract. Use this functionality with the `--timeline` argument.

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

To use Inspector Facet:

#### With a `brownie` project

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

#### To build an audit log of Diamond operations on an EIP2535 proxy contract

To build an audit log, you will need to crawl `DiamondCut` events from the blockchain. You can do this using [`moonworm`](https://github.com/bugout-dev/moonworm).

First, you will need to install `moonworm`:

```bash
pip install moonworm
```

This should be done in a separate Python environment from `inspector-facet` because `brownie` pins its dependencies
and doesn't play nice with other libraries ([GitHub issue](https://github.com/eth-brownie/brownie/issues/1516)).

Once `moonworm` is installed, you can find the deployment block for your contract:

```bash
moonworm find-deployment -w <JSON RPC URL for blockchain node> -c <contract address> -t 0.5
```

Save the output of this command as `START_BLOCK`.

Then crawl the `DiamondCut` event data:

```bash
moonworm watch \
  -i inspector_facet/abis/DiamondCutFacetABI.json \
  -w <JSON RPC URL for blockchain node> \
  -c <contract address> \
  --start $START_BLOCK \
  --end <current block number> \
  --only-events \
  -o <output filename> \
  --min-blocks-batch 1000 \
  --max-blocks-batch 1000000
```

If you are crawling data from a POA chain (like Polygon), add `--poa` to the command above.

Then, invoke `inspector-facet` as:

```bash
inspector-facet \
  --crawldata <output filename> \
  --project <path to brownie project (should contain build artifacts in build/contracts)> \
  --format human \
  --timeline
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
