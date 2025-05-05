# uniswap-viewer

uniswap-viewer - A lightweight Uniswap V3 data access library for Python.

This library provides a convenient interface for accessing on-chain data from Uniswap V3 pools,
including price calculation, tick information, and block streaming.

Features:
- Support for both synchronous and asynchronous Web3 clients.
- Price retrieval based on `sqrtPriceX96` and token decimals.
- Tick data decoding using Uniswap V3 ABI and tick key mappings.
- Tick spacing and tick slot calculations based on pool fee tiers.
- Utility functions for ABI loading and token address filtering.
- Block streaming generator to react to new blocks in real time.

Modules:
- `utils.py`: Internal helpers (ABI loading, tick keys, address filtering).
- `viewer_sync.py`: Synchronous Uniswap V3 pool viewer using `web3.py`.
- `viewer_async.py`: Asynchronous viewer compatible with async Web3 providers.
- (Pluggable design: future viewers can be added for batched queries, multicall, etc.)

Requirements:
- Python 3.8+
- `web3` library (with appropriate provider setup)

Usage example (sync):
    >>> from uniswap_viewer.viewer_sync import Viewer
    >>> from web3 import Web3
    >>> w3 = Web3(Web3.HTTPProvider(...))
    >>> v = Viewer(w3, token0_address, token1_address, fee=3000)
    >>> v.init()
    >>> price = v.get_price()

Usage example (async):
    >>> from uniswap_viewer.viewer_async import Viewer
    >>> from web3 import AsyncWeb3
    >>> w3 = AsyncWeb3(...)
    >>> v = Viewer(w3, token0_address, token1_address, fee=3000)
    >>> await v.init()
    >>> price = await v.get_price()

This library is designed for developers, analysts, and trading systems
that need efficient and readable access to raw Uniswap V3 data without relying
on external APIs like The Graph.

License: MIT
