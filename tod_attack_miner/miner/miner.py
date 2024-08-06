from typing import Callable, Sequence
from tod_attack_miner.db.db import DB, Candidate
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


class Miner:
    def __init__(self, rpc: RPC, db: DB) -> None:
        self.rpc = rpc
        self.db = db
        self._filter_stats = {"candidates": {}, "filtered": {}}
        self._original_collisions = {}

    def reset_db(self) -> None:
        self.db.reset()

    def fetch(self, start: int, end: int) -> None:
        fetch_block_range(self.rpc, self.db, BlockRange(start, end))

    def compute_skelcodes(self) -> None:
        self.db.insert_skeletons()

    def find_collisions(self) -> None:
        self.db.insert_collisions()
        self.db.insert_candidates()
        self._original_collisions = self.db.get_collisions_stats()

    def filter_candidates(
        self, filters: Sequence[tuple[str, Callable[[DB], int]]]
    ) -> None:
        self._filter_stats["candidates"]["before_filters"] = self.db.count_candidates()
        for name, filter in filters:
            self._filter_stats["filtered"][name] = filter(self.db)
        self._filter_stats["candidates"]["final"] = self.db.count_candidates()

    def count_candidates(self) -> int:
        return self.db.count_candidates()

    def get_candidates(self) -> Sequence[Candidate]:
        return self.db.get_candidates()

    def get_stats(self, quick=False):
        if quick:
            self._filter_stats["candidates"]["original_without_same_value"] = (
                "<omitted because of quick stats>"
            )
        else:
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
