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


evaluation_candidates = [
    (
        "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "0x65df49728edca9888255b262f082c1a13beaf1dca58bcb8004920b1fbb53e86b",
    ),
    (
        "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "0x94029b952ede83cd26f48ab40fad24851a517696b2785b631cdacb02795934cf",
    ),
    (
        "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "0x1ea1709059406a15686edef98de051fdfb5e854cc0991687b9573cba9005b021",
    ),
    (
        "0x40ca117ccc4933dd5b30e399f64673068c622802bdbd728f84b212cd197bf51a",
        "0x31c5b4782a75a1f5f513cd86ede1a8c0af54baa9511982f43a57988036ed0fed",
    ),
    (
        "0x98054dd5b5973d3b953029fb286e416994736313f4f986ba3d11143f4b9fbc72",
        "0xa68290ce02acc90bd3abd5ab1dd7b6fa26dd92d0b4e43fbb29737e8d6d54d926",
    ),
    (
        "0x5e6e4bae8fa62e86b85b2c5f74f67ee97628112e3b12c20f348ace13a2548ca3",
        "0xd884d83c00fa8ddc79306c290988c5b8c81c6fceeae1986add056cd1bf7d5f88",
    ),
    (
        "0xf812335569705e032f8eca9fff94d3348e29d748bd9ed4e2acd76fe54dbec42d",
        "0xd2b8e8cff425ae336c6084a9d7fc1c7d33d599fdf00c93eda40339e37ca6b12d",
    ),
    (
        "0x1b99d2ee257a00b5196b39534366fde8fded0cd3bfe639f161d12a9ca011adaf",
        "0x9213ae52ca8bf02107081b9340dd0d03ff533ac1040abeb873b686ed6427b303",
    ),
    (
        "0x6d936541a9e0befab9bf765c153fe1f0b9728dd6a6b6ba67cc757a56d115a2e8",
        "0x112ac55e0122204165ab94bad060ffcee026e4db572f74b3325d56bd0950ade1",
    ),
    (
        "0x3904535cb0f60bc6a3bf7082d05fb363a4375eb0ca1c85dee827007192b00413",
        "0x6016a7e14ef9b7ecc80985ace338e8894de892a58e941dd45dbb90c729079cb4",
    ),
]


@pytest.mark.vcr
def test_tod_attack_miner_evaluation(
    postgresql: Connection, snapshot: PyTestSnapshotTest
):
    block_range = BlockRange(19895500, 19895504)

    miner = Miner(RPC(test_provider_url), DB(postgresql))

    miner.fetch(block_range.start, block_range.end)
    miner.find_collisions()
    results = miner.evaluate_candidates(
        get_filters_except_duplicate_limits(3), evaluation_candidates
    )

    snapshot.assert_match(results, "evaluation results")
