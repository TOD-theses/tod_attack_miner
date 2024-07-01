from pathlib import Path

import pytest
from tod_attack_miner.fetcher.fetcher import BlockRange
from tod_attack_miner.miner.miner import Miner

from snapshottest.pytest import PyTestSnapshotTest

test_provider_url = "http://localhost:8124/eth"
test_db_path = Path("test_database.db")


@pytest.mark.vcr
def test_tod_attack_miner_e2e(snapshot: PyTestSnapshotTest):
    block_range = BlockRange(19895500, 19895504)

    miner = Miner(test_provider_url, test_db_path)

    miner.fetch(block_range.start, block_range.end)
    miner.find_conflicts()

    stats = miner.get_stats()
    attacks = miner.get_attacks(block_range.start, block_range.end)

    snapshot.assert_match(stats, "stats")
    snapshot.assert_match(set(attacks), "attacks")
