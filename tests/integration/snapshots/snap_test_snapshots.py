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

snapshots["test_tod_attack_miner_e2e num_candidates"] = 163

snapshots["test_tod_attack_miner_e2e stats"] = {
    "accesses": {"balance": 4721, "code": 2301, "nonce": 4385, "storage": 8500},
    "candidates": 163,
    "candidates_filters": {
        "candidates": {
            "before_filters": 2222,
            "final": 163,
            "original_without_same_value": 264455,
        },
        "filtered": {
            "block_producers": 784,
            "block_window": 63,
            "codes": 0,
            "indirect_dependencies_quick": 55,
            "indirect_dependencies_recursive": 43,
            "limited_collisions_per_address": 213,
            "limited_collisions_per_code_family": 1,
            "limited_collisions_per_code_hash": 7,
            "nonces": 659,
            "recipient_eth_transfer": 61,
            "same_sender": 173,
        },
    },
    "candidates_transactions_unique": 240,
    "collision_addresses_unique": 73,
    "collisions": {"balance": 64, "storage": 175},
    "collisions_before_filters": {"balance": 1533, "nonce": 879, "storage": 766},
    "frequencies": {
        "candidates_transactions": [(3, 3), (2, 80), (1, 157)],
        "collisions_addresses": [
            (10, 10),
            (9, 1),
            (7, 1),
            (6, 1),
            (5, 2),
            (4, 6),
            (3, 6),
            (2, 19),
            (1, 27),
        ],
    },
    "samples": {
        "candidates_transactions_frequent": [
            ("0xbc0dca6b2bb6d8089d16824a3abc89c38f39af5af5edeeab534734c6db6f0ef9", 3),
            ("0x83f080e05913644ae70103139509caf246066d8111d432db8a5afe954b6a05e7", 3),
            ("0x618f4b0392ac8ee3cb3c447c6dbe1ec4b472e8e49d302a393fd23e6d36164ec6", 3),
            ("0x767e0cc6d695c96fb2b7be8a28f075c5a0729cdd646e3892230a6138a33925df", 2),
            ("0x7d98a6b0fa1b22bdd88bbaed71178105c121010dae17a6d96084e7576c055316", 2),
        ],
        "collision_addresses_frequent": [
            ("0x0ec68c5b10f21effb74f2a5c61dfe6b08c0db6cb", 10),
            ("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49", 10),
            ("0x7777777f279eba3d3ad8f4e708545291a6fdba8b", 10),
            ("0x8390a1da07e376ef7add4be859ba74fb83aa02d5", 10),
            ("0x916b2aff900d06c526b4935f999462b65f1a24fe", 10),
        ],
    },
    "state_diffs": {"balance": 2577, "code": 3, "nonce": 880, "storage": 2594},
    "transactions": 1002,
}
