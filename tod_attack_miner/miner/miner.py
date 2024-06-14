from pathlib import Path
from typing import Sequence
from tod_attack_miner.db.db import DB
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


class Miner:
    def __init__(self, archive_node_provider_url: str, database_path: Path) -> None:
        self.rpc = RPC(archive_node_provider_url)
        self.db = DB(database_path)

    def fetch(self, start: int, end: int) -> None:
        fetch_block_range(self.rpc, self.db, BlockRange(start, end))

    def get_attacks(self, start: int, end: int) -> Sequence[tuple[str, str]]:
        # TODO: only get attacks in the specified range
        return self.db.get_storage_collisions_tx_pairs()
