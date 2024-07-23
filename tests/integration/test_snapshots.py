from pathlib import Path

import pytest
from tod_attack_miner.db.db import DB
from tod_attack_miner.db.filters import (
    get_filters_duplicate_limits,
    get_filters_except_duplicate_limits,
)
from tod_attack_miner.fetcher.fetcher import BlockRange
from tod_attack_miner.miner.miner import Miner

from snapshottest.pytest import PyTestSnapshotTest
from psycopg import Connection

from tod_attack_miner.rpc.rpc import RPC

test_provider_url = "http://localhost:8124/eth"
test_db_path = Path("test_database.db")


@pytest.mark.vcr
def test_tod_attack_miner_e2e(postgresql: Connection, snapshot: PyTestSnapshotTest):
    block_range = BlockRange(19895500, 19895504)

    miner = Miner(RPC(test_provider_url), DB(postgresql))

    miner.fetch(block_range.start, block_range.end)
    miner.find_collisions()
    miner.compute_skelcodes()
    miner.filter_candidates(
        get_filters_except_duplicate_limits(3) + get_filters_duplicate_limits(10)
    )

    candidates = miner.get_candidates()
    stats = miner.get_stats()

    snapshot.assert_match(len(candidates), "num_candidates")
    snapshot.assert_match(candidates[0], "first_candidate")
    snapshot.assert_match(stats, "stats")
