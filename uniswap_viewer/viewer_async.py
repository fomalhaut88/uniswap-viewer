"""
viewer_async.py - Asynchronous interface for accessing Uniswap V3 pool data.

This module provides an async viewer for interacting with Uniswap V3 pools
using asynchronous Web3 providers (e.g., Web3 AsyncMiddleware). It allows
retrieving token prices, tick data, and computing tick-related values.

Main components:
- `Viewer`: an async class for accessing Uniswap V3 pools.
- `stream_new_blocks`: async generator for tracking new block numbers.
- `get_decimals`: async utility to fetch token decimals from an ERC-20 token.
"""

import math
import asyncio

from .utils import get_abi, TICKS_KEYS


class Viewer:
    """
    Asynchronous Uniswap V3 pool viewer.

    This class allows querying price and tick information from a Uniswap V3 pool
    in an async context.
    """

    def __init__(self, w3, token0, token1, fee=3000):
        """
        Initializes the Viewer instance.

        Args:
            w3: Async-enabled Web3 instance.
            token0 (str): First token address (must be > token1 bitwise).
            token1 (str): Second token address.
            fee (int, optional): Pool fee (bps). One of 100, 500, 3000, 10000.
                                 Defaults to 3000 (0.3%).

        Raises:
            AssertionError: If invalid fee or token ordering.
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

    async def init(self):
        """
        Initializes decimals and resolves the pool address and contract.

        This method must be awaited before calling other methods that
        depend on pool context (e.g., price, tick queries).

        Raises:
            AssertionError: If pool is not found on-chain.
        """
        self._decimals0 = await get_decimals(self._w3, self._token0)
        self._decimals1 = await get_decimals(self._w3, self._token1)
        self._pool_address = await self._get_pool_address()
        self._pool_contract = self._w3.eth.contract(address=self._pool_address, 
                                                    abi=get_abi('pool-abi'))

    async def get_price(self, block_num=None):
        """
        Asynchronously fetches the pool price as a float.

        Args:
            block_num (int, optional): Specific block number, or latest if None.

        Returns:
            float: Price of token0 in terms of token1.
        """
        slot0 = await self._pool_contract.functions.slot0().call(
            block_identifier=block_num
        )
        sqrtPriceX96 = slot0[0]
        price = (sqrtPriceX96 / (2**96)) ** 2
        price *= 10 ** (self._decimals1 - self._decimals0)
        return price

    async def get_tick_data(self, tick, block_num=None):
        """
        Retrieves detailed tick information from the pool.

        Args:
            tick (int): The tick index.
            block_num (int, optional): Block to query from. Defaults to latest.

        Returns:
            dict: Tick data fields mapped by standard TICKS_KEYS.
        """
        tick_data = await self._pool_contract.functions.ticks(tick).call(
            block_identifier=block_num
        )
        return dict(zip(TICKS_KEYS, tick_data))

    def calc_tick(self, price):
        """
        Calculates the tick index corresponding to a given price.

        Args:
            price (float): Price of token0 in token1 units.

        Returns:
            int: Closest tick index.
        """
        price *= 10 ** (self._decimals0 - self._decimals1)
        return math.floor(math.log(price) / math.log(1.0001))

    def tick_spacing(self):
        """
        Returns the tick spacing associated with the pool's fee tier.

        Returns:
            int: Tick spacing (1, 10, 60, or 200).
        """
        return {
            100: 1,
            500: 10,
            3000: 60,
            10000: 200,
        }[self._fee]

    def tick_slot(self, tick):
        """
        Calculates the tick slot for a given tick index.

        Args:
            tick (int): Tick index.

        Returns:
            int: Lower-bound of the spacing interval containing the tick.
        """
        return tick - tick % self.tick_spacing()

    async def _get_pool_address(self):
        factory_contract = self._w3.eth.contract(
            address='0x1F98431c8aD98523631AE4a59f267346ea31F984', 
            abi=get_abi('factory-abi'),
        )
        pool_address = await factory_contract.functions \
            .getPool(self._token1, self._token0, self._fee).call()
        assert pool_address != "0x0000000000000000000000000000000000000000", \
            "Could not find pool for the tokens."
        return pool_address


async def stream_new_blocks(w3, timeout=1):
    """
    Asynchronously yields new block numbers as they appear on-chain.

    Polls the chain periodically and yields any new blocks that have appeared
    since the last poll.

    Args:
        w3: Async Web3 instance.
        timeout (int): Poll interval in seconds. Defaults to 1.

    Yields:
        int: New block numbers in sequence.
    """
    block_num_prev = None
    while True:
        block_num = await w3.eth.block_number
        if block_num_prev is None:
            yield block_num
        else:
            for num in range(block_num_prev + 1, block_num + 1):
                yield num
        block_num_prev = block_num
        await asyncio.sleep(timeout)


async def get_decimals(w3, token):
    """
    Asynchronously fetches the number of decimals of an ERC-20 token.

    Args:
        w3: Async Web3 instance.
        token (str): Ethereum address of the ERC-20 token.

    Returns:
        int: Number of decimals.
    """
    token_contract = w3.eth.contract(address=token, abi=get_abi('erc20-abi'))
    decimals = await token_contract.functions.decimals().call()
    return decimals
