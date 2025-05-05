"""
viewer_sync.py - Synchronous interface for accessing Uniswap V3 pool data.

This module provides a synchronous viewer for querying Uniswap V3 pools using
web3.py. It allows retrieving token prices, tick data, and computing tick-related
values such as tick index and tick slots.

Main components:
- `Viewer`: a class for interacting with a Uniswap V3 pool.
- `stream_new_blocks`: generator function to yield new block numbers as they appear.
- `get_decimals`: helper function to fetch token decimals from an ERC-20 contract.
"""

import math
import time
from typing import Optional, Dict, Any
from collections.abc import Generator

from web3 import Web3

from .utils import get_abi, TICKS_KEYS


class Viewer:
    """
    A synchronous Uniswap V3 pool viewer.

    This class enables price and tick queries for a specific Uniswap V3 pool
    defined by a token pair and a fee tier.
    """

    def __init__(self, w3: Web3, token0: str, token1: str, fee: int = 3000):
        """
        Initializes the Viewer instance.

        Args:
            w3 (Web3): Web3 instance.
            token0 (str): Address of the first token (must be > token1).
            token1 (str): Address of the second token.
            fee (int, optional): Pool fee in basis points. Allowed values are 
                                 100 (0.01%), 500 (0.05%), 3000 (0.3%), 10000 
                                 (1%). Defaults to 3000 (0.3%).

        Raises:
            AssertionError: If fee is invalid or token0 is not > token1 in bits.
        """
        # Check arguments
        assert fee in (100, 500, 3000, 10000), \
            "Allowed fee must be in (100, 500, 3000, 10000) " \
            "that corresponds to 0.01%, 0.05%, 0.3%, 1%."

        assert int(token0, 16) > int(token1, 16), \
            "token0 must go after token1 in bit representation."

        # Attributes
        self._w3 = w3
        self._token0 = self._w3.to_checksum_address(token0)
        self._token1 = self._w3.to_checksum_address(token1)
        self._fee = fee
        self._decimals0 = None
        self._decimals1 = None
        self._pool_address = None
        self._pool_contract = None

    def init(self):
        """
        Initializes the pool contract by resolving its address from the factory.

        Must be called before using methods like `get_price` or `get_tick_data`.

        Raises:
            AssertionError: If no pool exists for the provided tokens and fee.
        """
        self._decimals0 = get_decimals(self._w3, self._token0)
        self._decimals1 = get_decimals(self._w3, self._token1)
        self._pool_address = self._get_pool_address()
        self._pool_contract = self._w3.eth.contract(address=self._pool_address, 
                                                    abi=get_abi('pool-abi'))

    def get_price(self, block_num: Optional[int] = None) -> float:
        """
        Returns the current pool price as a floating-point value.

        The result is adjusted for token decimals.

        Args:
            block_num (int, optional): Specific block number. If None, uses latest.

        Returns:
            float: The spot price of token0 denominated in token1.
        """
        slot0 = self._pool_contract.functions.slot0().call(
            block_identifier=block_num
        )
        sqrtPriceX96 = slot0[0]
        price = (sqrtPriceX96 / (2**96)) ** 2
        price *= 10 ** (self._decimals1 - self._decimals0)
        return price

    def get_tick_data(self, tick: int, 
                      block_num: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches tick data for a given tick index from the pool.

        Args:
            tick (int): The tick index.
            block_num (int, optional): Specific block number. If None, uses latest.

        Returns:
            dict: A dictionary of tick data fields, keyed by TICKS_KEYS.
        """
        tick_data = self._pool_contract.functions.ticks(tick).call(
            block_identifier=block_num
        )
        return dict(zip(TICKS_KEYS, tick_data))

    def calc_tick(self, price: float) -> int:
        """
        Calculates the tick index corresponding to a given price.

        Args:
            price (float): Price of token0 in token1.

        Returns:
            int: The closest tick index that matches the price.
        """
        price *= 10 ** (self._decimals0 - self._decimals1)
        return math.floor(math.log(price) / math.log(1.0001))

    def tick_spacing(self) -> int:
        """
        Returns the tick spacing for the pool based on the fee tier.

        Returns:
            int: Tick spacing (1, 10, 60, or 200).
        """
        return {
            100: 1,
            500: 10,
            3000: 60,
            10000: 200,
        }[self._fee]

    def tick_slot(self, tick: int) -> int:
        """
        Calculates the tick slot for a given tick.

        A tick slot is the lower bound of the spacing interval that contains the tick.

        Args:
            tick (int): The tick index.

        Returns:
            int: The tick slot index.
        """
        return tick - tick % self.tick_spacing()

    def _get_pool_address(self) -> str:
        factory_contract = self._w3.eth.contract(
            address='0x1F98431c8aD98523631AE4a59f267346ea31F984', 
            abi=get_abi('factory-abi'),
        )
        pool_address = factory_contract.functions \
            .getPool(self._token1, self._token0, self._fee).call()
        assert pool_address != "0x0000000000000000000000000000000000000000", \
            "Could not find pool for the tokens."
        return pool_address


def stream_new_blocks(w3: Web3, timeout: int = 1) -> Generator[int]:
    """
    Yields new block numbers as they appear on-chain.

    This generator polls the chain at regular intervals to detect new blocks
    and yields all blocks that were mined since the last check.

    Args:
        w3 (Web3): An initialized Web3 instance.
        timeout (int): Time delay in seconds between polling. Defaults to 1.

    Yields:
        int: Block numbers in increasing order.
    """
    block_num_prev = None
    while True:
        block_num = w3.eth.block_number
        if block_num_prev is None:
            yield block_num
        else:
            yield from range(block_num_prev + 1, block_num + 1)
        block_num_prev = block_num
        time.sleep(timeout)


def get_decimals(w3: Web3, token: str) -> int:
    """
    Returns the number of decimals for a given ERC-20 token.

    Args:
        w3 (Web3): Web3 instance.
        token (str): Ethereum address of the token.

    Returns:
        int: Number of decimal places used by the token.
    """
    token_contract = w3.eth.contract(address=token, abi=get_abi('erc20-abi'))
    decimals = token_contract.functions.decimals().call()
    return decimals
