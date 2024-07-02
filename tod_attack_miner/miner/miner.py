from typing import Sequence
from tod_attack_miner.db.db import DB
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


class Miner:
    def __init__(self, rpc: RPC, db: DB) -> None:
        self.rpc = rpc
        self.db = db

    def fetch(self, start: int, end: int) -> None:
        fetch_block_range(self.rpc, self.db, BlockRange(start, end))

    def find_conflicts(self) -> None:
        self.db.insert_conflicts()

    def get_conflicts(
        self, start: int, end: int
    ) -> Sequence[tuple[str, str, tuple[str, str, int]]]:
        # TODO: only get attacks in the specified range
        return self.db.get_collisions()

    def get_stats(self):
        return {
            "accesses": self.db.get_accesses_stats(),
            "state_diffs": self.db.get_state_diffs_stats(),
            "conflicts": self.db.get_conflicts_stats(),
            "candidates_original": self.db.count_candidates_original(),
            "candidates_semi": self.db.count_candidates_semi_direct_deps(),
            "addresses_est": self.db.get_unique_addresses_stats(),
            "addresses_est_total": self.db.get_unique_addresses_total(),
        }
