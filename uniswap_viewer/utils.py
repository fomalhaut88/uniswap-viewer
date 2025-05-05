"""
utils.py - Utility functions and constants for the uniswap_viewer library.

This module provides common helpers used throughout the uniswap_viewer codebase,
including:

- A list of standard tick keys used in Uniswap V3 pools.
- A helper function to filter out zero addresses.
- A utility to load ABI definitions from local JSON files.

The module assumes ABI files are located under the `uniswap_viewer/source` package.

Typical use cases:
- Filtering out empty Ethereum addresses before display or storage.
- Loading ABI files to construct contract instances via web3.py.
- Interpreting tick data retrieved from Uniswap V3 pools.

All functions are intended for internal use, but may also be helpful for
developers extending or integrating the uniswap_viewer library.
"""

import json
import time
from importlib import resources
from typing import Optional


# Keys used in Uniswap V3 tick structure
TICKS_KEYS = [
    'liquidityGross',
    'liquidityNet',
    'feeGrowthOutside0X128',
    'feeGrowthOutside1X128',
    'tickCumulativeOutside',
    'secondsPerLiquidityOutsideX128',
    'secondsOutside',
    'initialized',
]


def address_checked(address: str) -> Optional[str]:
    """
    Returns the address if it's not the zero address, otherwise returns None.

    This function is used to filter out null Ethereum addresses typically
    represented as "0x0000000000000000000000000000000000000000".

    Args:
        address (str): The Ethereum address to check.

    Returns:
        str or None: The original address if valid, otherwise None.

    Example:
        >>> address_checked("0x0000000000000000000000000000000000000000")
        None
        >>> address_checked("0x1234567890abcdef1234567890abcdef12345678")
        '0x1234567890abcdef1234567890abcdef12345678'
    """
    if address != "0x0000000000000000000000000000000000000000":
        return address
    else:
        return None


def get_abi(abi: str) -> str:
    """
    Loads a JSON ABI file from the `uniswap_viewer.source` package.

    The function expects the ABI file to be named `<abi>.json` and
    located in the `uniswap_viewer/source` package directory.

    Args:
        abi (str): The name of the ABI file (without `.json` extension).

    Returns:
        dict: The parsed JSON ABI object.

    Raises:
        FileNotFoundError: If the ABI file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.

    Example:
        >>> pool_abi = get_abi("pool-api")
    """
    file = resources.files("uniswap_viewer.source").joinpath(f"{abi}.json")
    with file.open(mode='r') as f:
        return json.load(f)
