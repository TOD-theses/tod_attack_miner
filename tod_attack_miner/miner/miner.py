from typing import Sequence
from tod_attack_miner.db.db import DB, Candidate
from tod_attack_miner.db.filters import (
    filter_codes,
    filter_nonces,
    filter_block_window,
    filter_indirect_dependencies_recursive,
    filter_indirect_dependencies_quick,
    filter_same_sender,
    filter_second_tx_ether_transfer,
    filter_block_producers,
    limit_collisions_per_address,
)
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


class Miner:
    def __init__(self, rpc: RPC, db: DB) -> None:
        self.rpc = rpc
        self.db = db
        self._filter_stats = {"candidates": {}, "filtered": {}}
        self._original_collisions = {}

    def fetch(self, start: int, end: int) -> None:
        fetch_block_range(self.rpc, self.db, BlockRange(start, end))

    def find_collisions(self) -> None:
        self.db.insert_collisions()
        self.db.insert_candidates()
        self._original_collisions = self.db.get_collisions_stats()

    def filter_candidates(self, window_size: int | None) -> None:
        self._filter_stats["candidates"]["before_filters"] = self.db.count_candidates()
        self._filter_stats["filtered"]["block_window"] = filter_block_window(
            self.db, window_size
        )
        self._filter_stats["filtered"]["block_producers"] = filter_block_producers(
            self.db
        )
        self._filter_stats["filtered"]["nonces"] = filter_nonces(self.db)
        self._filter_stats["filtered"]["codes"] = filter_codes(self.db)
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
        self._filter_stats["filtered"]["limited_collisions_per_address"] = (
            limit_collisions_per_address(self.db)
        )
        self._filter_stats["candidates"]["final"] = self.db.count_candidates()

    def count_candidates(self) -> int:
        return self.db.count_candidates()

    def get_candidates(self) -> Sequence[Candidate]:
        return self.db.get_candidates()

    def get_stats(self):
        self._filter_stats["candidates"]["original_without_same_value"] = (
            self.db.count_candidates_original()
        )
        return {
            "accesses": self.db.get_accesses_stats(),
            "state_diffs": self.db.get_state_diffs_stats(),
            "collisions": self.db.get_collisions_stats(),
            "collisions_before_filters": self._original_collisions,
            "candidates_filters": self._filter_stats,
            "candidates": self.db.count_candidates(),
            "candidates_transactions_unique": self.db.count_unique_candidate_transactions(),
            "transactions": self.db.count_transactions(),
            "collision_addresses_unique": self.db.count_unique_collision_addresses(),
            "samples": {
                "candidates_transactions_frequent": self.db.most_frequent_candidate_transactions(),
                "collision_addresses_frequent": self.db.most_frequent_collisions_addresses(),
            },
            "frequencies": {
                "candidates_transactions": self.db.transactions_candidate_frequency(),
                "collisions_addresses": self.db.collisions_addresses_frequency(),
            },
        }
