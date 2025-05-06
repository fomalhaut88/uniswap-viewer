# uniswap-viewer

A lightweight Python library for accessing Uniswap V3 on-chain data.

`uniswap-viewer` provides a clean and efficient interface for reading price and 
tick information directly from Uniswap V3 smart contracts using `web3.py`. It 
supports both synchronous and asynchronous workflows and is ideal for 
developers, analysts, and algorithmic traders.

## Features

- Supports both sync and async Web3 clients  
- Fetches token prices using `sqrtPriceX96` and token decimals  
- Retrieves detailed tick data via ABI-decoded contract calls  
- Computes tick index, tick spacing, and tick slot  
- Includes block streaming generator to track new blocks in real time  
- Built-in utilities for loading ABIs and checking Ethereum addresses  

## Modules

- `viewer_sync.py` – synchronous Uniswap V3 viewer using `web3.Web3`
- `viewer_async.py` – asynchronous Uniswap V3 viewer using `web3.AsyncWeb3`
- `utils.py` – helper functions (ABI loading, tick keys, address filters)

## Usage

### Sync example

```python
from uniswap_viewer import ViewerSync, get_token_address
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("<your_provider_url>"))

viewer = ViewerSync(w3, "usdt", "weth", fee=3000)
viewer.init()
price = viewer.get_price()
```

### Async example

```python
from uniswap_viewer import ViewerAsync, get_token_address
from web3 import AsyncWeb3

w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider("<your_provider_url>"))

viewer = ViewerAsync(w3, "usdt", "weth", fee=3000)
await viewer.init()
price = await viewer.get_price()
```

## Requirements

- Python 3.8+
- `web3` library (sync or async)

## Motivation

This library is designed for:

- Developers integrating Uniswap data directly from the blockchain
- Quants and analysts building custom tooling
- Avoiding reliance on third-party APIs like The Graph

## License

MIT
