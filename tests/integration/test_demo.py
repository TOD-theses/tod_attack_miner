from unittest.mock import MagicMock
from tod_attack_miner.analysis.analyzer import get_collisions
from tod_attack_miner.db.db import DB
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate


def run_collisions_test(
    prestates: list[TxPrestate],
    blocks: list[BlockWithTransactions],
    expected_collisions: list[set[str]],
):
    block_range = BlockRange(
        min(b["number"] for b in blocks), max(b["number"] for b in blocks)
    )

    rpc = MagicMock(spec_set=RPC)
    # TODO: list of blocks
    rpc.fetch_block_with_transactions.return_value = blocks[0]
    rpc.fetch_prestates.return_value = prestates

    db = DB()
    fetch_block_range(rpc, db, block_range)
    collision_transactions = get_collisions(db)

    expected_collisions_set = set(
        frozenset(collision) for collision in expected_collisions
    )

    assert collision_transactions == expected_collisions_set


def test_demo():
    prestates: list[TxPrestate] = [
        {
            "txHash": "0x1111",
            "result": {
                "0xabcd": {
                    "storage": {
                        "0xaaaa": "0x1234",
                        "0xbbbb": "0x5678",
                    }
                }
            },
        },
        {
            "txHash": "0x2222",
            "result": {
                "0xabcd": {
                    "storage": {
                        "0xaaaa": "0x1020",
                    }
                }
            },
        },
        {
            "txHash": "0x3333",
            "result": {
                # other address
                "0xef12": {
                    "storage": {
                        "0xaaaa": "0x1030",
                    }
                }
            },
        },
        {
            "txHash": "0x4444",
            "result": {
                "0xabcd": {
                    "storage": {
                        "0xbbbb": "0x1040",
                    }
                }
            },
        },
    ]
    blocks: list[BlockWithTransactions] = [
        {
            "number": 1,
            "transactions": [
                {"hash": "0x1111", "from": "someone1"},
                {"hash": "0x2222", "from": "someone2"},
                {"hash": "0x3333", "from": "someone3"},
                {"hash": "0x4444", "from": "someone4"},
            ],
        }
    ]  # type: ignore

    expected_collisions: list[set[str]] = [
        {"0x1111", "0x2222"},
        {"0x1111", "0x4444"},
    ]

    run_collisions_test(prestates, blocks, expected_collisions)
