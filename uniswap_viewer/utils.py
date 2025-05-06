"""
utils.py - Utility functions and constants for the uniswap_viewer library.

This module provides common helpers used throughout the uniswap_viewer codebase,
including:

- A list of standard tick keys used in Uniswap V3 pools.
- A helper function to filter out zero addresses.
- A utility to load ABI definitions from local JSON files.

The module assumes ABI files are located under the `uniswap_viewer/source` 
package.

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
"""
Keys used in Uniswap V3 tick structure.
"""


TOKEN_MAP = {
    "WETH": "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC": "0xA0b86991C6218B36c1d19D4a2e9Eb0cE3606eB48",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    "SNX": "0xC011A72400E58ecD99Ee497CF89E3775d4bd732F",
    "YFI": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
    "BAT": "0x0D8775F648430679A709E98d2b0Cb6250d2887EF",
    "ZRX": "0xE41d2489571d322189246DaFA5ebDe1F4699F498",
    "MANA": "0x0f5D2fB29fb7d3CFeE444a200298f468908cC942",
}
"""
List of the most liquid tokens on Uniswap V3.
"""


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


def get_token_address(symbol: str) -> str:
    """
    Returns the Ethereum address of a commonly used token on Uniswap V3 by its 
    symbol.

    Looks up the token symbol in a predefined dictionary of liquid tokens 
    supported by the `uniswap-viewer` library. The symbol matching is 
    case-insensitive.

    Args:
        symbol (str): The token symbol (e.g., "USDC", "WETH", "DAI").

    Returns:
        str: The Ethereum address of the corresponding token.

    Raises:
        KeyError: If the symbol is not found in the internal token map.

    Example:
        >>> get_token_address("usdc")
        '0xA0b86991C6218B36c1d19D4a2e9Eb0cE3606eB48'
    """
    try:
        return TOKEN_MAP[symbol.upper()]
    except KeyError as exc:
        raise KeyError(
            f"Could not find address {str(exc)} within uniswap-viewer library"
        )
