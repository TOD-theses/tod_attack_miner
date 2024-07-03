from typing import Sequence
from tod_attack_miner.db.db import DB
from tod_attack_miner.db.filters import (
    filter_indirect_dependencies_recursive,
    filter_indirect_dependencies_quick,
    filter_same_sender,
    filter_second_tx_ether_transfer,
)
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


class Miner:
    def __init__(self, rpc: RPC, db: DB) -> None:
        self.rpc = rpc
        self.db = db
        self._filter_stats = {"candidates": {}, "filtered": {}}

    def fetch(self, start: int, end: int) -> None:
        fetch_block_range(self.rpc, self.db, BlockRange(start, end))

    def find_conflicts(self) -> None:
        self.db.insert_conflicts()
        self.db.insert_candidates()

    def filter_candidates(self) -> None:
        self._filter_stats["candidates"]["before_filters"] = self.db.count_candidates()
        self._filter_stats["filtered"]["indirect_dependencies_quick"] = (
            filter_indirect_dependencies_quick(self.db)
        )
        self._filter_stats["filtered"]["indirect_dependencies_recursive"] = (
            filter_indirect_dependencies_recursive(self.db)
        )
        self._filter_stats["filtered"]["same_sender"] = filter_same_sender(self.db)
        self._filter_stats["filtered"]["recipient_eth_transfer"] = (
            filter_second_tx_ether_transfer(self.db)
        )
        self._filter_stats["candidates"]["final"] = self.db.count_candidates()

    def count_candidates(self) -> int:
        return self.db.count_candidates()

    def get_candidates(self) -> Sequence[tuple[str, str]]:
        return self.db.get_candidates()

    def get_stats(self):
        self._filter_stats["candidates"]["original_without_same_value"] = (
            self.db.count_candidates_original()
        )
        return {
            "accesses": self.db.get_accesses_stats(),
            "state_diffs": self.db.get_state_diffs_stats(),
            "conflicts": self.db.get_conflicts_stats(),
            "candidates_filters": self._filter_stats,
            "candidates": self.db.count_candidates(),
            "addresses_est": self.db.get_unique_addresses_stats(),
            "addresses_est_total": self.db.get_unique_addresses_total(),
        }
