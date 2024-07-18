# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_tod_attack_miner_e2e first_candidate"] = {
    "block_dist": 0,
    "tx_access_hash": "0xcfb5968f11b15c15cfb23234dc56f16c5811485a6cae702195317a2f86ce2c6c",
    "tx_write_hash": "0x001811be6d2019216746d9c9da9f847160dc18a9d6dba362d4b265c2dd7e649a",
    "types": ["balance"],
}

snapshots["test_tod_attack_miner_e2e num_candidates"] = 157

snapshots["test_tod_attack_miner_e2e stats"] = {
    "accesses": {"balance": 4663, "code": 2248, "nonce": 4332, "storage": 8239},
    "candidates": 157,
    "candidates_filters": {
        "candidates": {
            "before_filters": 2195,
            "final": 157,
            "original_without_same_value": 264234,
        },
        "filtered": {
            "block_producers": 786,
            "block_window": 62,
            "codes": 0,
            "indirect_dependencies_quick": 47,
            "indirect_dependencies_recursive": 38,
            "limited_collisions_per_address": 208,
            "limited_collisions_per_code_family": 2,
            "limited_collisions_per_code_hash": 2,
            "nonces": 658,
            "recipient_eth_transfer": 61,
            "same_sender": 174,
        },
    },
    "candidates_transactions_unique": 235,
    "collision_addresses_unique": 70,
    "collisions": {"balance": 63, "storage": 172},
    "collisions_before_filters": {"balance": 1526, "nonce": 879, "storage": 710},
    "frequencies": {
        "candidates_transactions": [(2, 79), (1, 156)],
        "collisions_addresses": [
            (10, 11),
            (6, 2),
            (5, 5),
            (4, 4),
            (3, 3),
            (2, 18),
            (1, 27),
        ],
    },
    "samples": {
        "candidates_transactions_frequent": [
            ("0x367b13927c05d804d67b2809daade8baba114e6d5a0f2d95cf7318ffdb656f97", 2),
            ("0x767e0cc6d695c96fb2b7be8a28f075c5a0729cdd646e3892230a6138a33925df", 2),
            ("0x4fa5690f54408827f28253342d0bf8c616b9377a9917ab7706be23c79079df9a", 2),
            ("0x7d98a6b0fa1b22bdd88bbaed71178105c121010dae17a6d96084e7576c055316", 2),
            ("0x5406c057c0fecf3d9ca3a200f9c8f58a10d57c2b732df59c5607b45412f40af6", 2),
        ],
        "collision_addresses_frequent": [
            ("0x0ec68c5b10f21effb74f2a5c61dfe6b08c0db6cb", 10),
            ("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49", 10),
            ("0x7777777f279eba3d3ad8f4e708545291a6fdba8b", 10),
            ("0x8390a1da07e376ef7add4be859ba74fb83aa02d5", 10),
            ("0x8fa3b4570b4c96f8036c13b64971ba65867eeb48", 10),
        ],
    },
    "state_diffs": {"balance": 2577, "code": 3, "nonce": 880, "storage": 2594},
    "transactions": 1002,
}
