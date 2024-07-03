from dataclasses import dataclass

from tqdm import tqdm

from tod_attack_miner.db.db import DB
from tod_attack_miner.rpc.rpc import RPC
from tod_attack_miner.rpc.state_diff_utils import (
    state_diff_fill_implicit_fields,
    state_diff_remove_unchanged_fields,
)


@dataclass
class BlockRange:
    """First block in the range"""

    start: int
    """Last block in the range (inclusive)"""
    end: int

    def __post_init__(self):
        assert (
            self.start <= self.end
        ), f"BlockRange start must not be higher than the end: {self}"


def fetch_block_range(rpc: RPC, db: DB, block_range: BlockRange):
    for block_number in (
        bar := tqdm(
            range(block_range.start, block_range.end + 1),
            desc="Fetch traces and block metadata",
        )
    ):
        bar.set_postfix_str(f"block {block_number}")
        rpc.fetch_block_with_transactions(block_number)
        prestates = rpc.fetch_prestates(block_number)
        state_diffs = rpc.fetch_state_diffs(block_number)

        db.insert_block(rpc.fetch_block_with_transactions(block_number))
        for i, prestate in enumerate(prestates):
            db.insert_prestate(block_number, i, prestate)
        for i, state_diff in enumerate(state_diffs):
            state_diff_fill_implicit_fields(state_diff)
            state_diff_remove_unchanged_fields(state_diff)

            db.insert_state_diff(block_number, i, state_diff)
