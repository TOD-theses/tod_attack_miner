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

snapshots["test_tod_attack_miner_e2e num_candidates"] = 369

snapshots["test_tod_attack_miner_e2e stats"] = {
    "accesses": {"balance": 4663, "code": 2248, "nonce": 4332, "storage": 8239},
    "candidates": 369,
    "candidates_filters": {
        "candidates": {
            "before_filters": 2195,
            "final": 369,
            "original_without_same_value": 264234,
        },
        "filtered": {
            "block_producers": 786,
            "block_window": 62,
            "codes": 0,
            "indirect_dependencies_quick": 47,
            "indirect_dependencies_recursive": 38,
            "nonces": 658,
            "recipient_eth_transfer": 61,
            "same_sender": 174,
        },
    },
    "candidates_transactions_unique": 399,
    "collision_addresses_unique": 75,
    "collisions": {"balance": 229, "storage": 385},
    "collisions_before_filters": {"balance": 1526, "nonce": 879, "storage": 710},
    "frequencies": {
        "candidates_transactions": [(5, 2), (4, 5), (3, 30), (2, 256), (1, 106)],
        "collisions_addresses": [
            (184, 1),
            (90, 1),
            (30, 1),
            (27, 1),
            (18, 1),
            (16, 5),
            (14, 1),
            (12, 1),
            (11, 1),
            (9, 1),
            (6, 2),
            (5, 5),
            (4, 6),
            (3, 5),
            (2, 20),
            (1, 23),
        ],
    },
    "samples": {
        "candidates_transactions_frequent": [
            ("0xe91cfe5d2cd6d2f4fc353ed11b595f2ec2f32d01933dbdccc2f2bf0616bfdcbc", 5),
            ("0x6e97688f22ccd10ca137f292f806632fe08abb0dff3743f769ba517e6255ffc7", 5),
            ("0x6a6441644f1511f988446bd3bc0950677594b6830189fe4bb8e57c0eb90c45f7", 4),
            ("0x618f4b0392ac8ee3cb3c447c6dbe1ec4b472e8e49d302a393fd23e6d36164ec6", 4),
            ("0x1574e1c50915720812699177d7adbfc4ceb0aacf22dd0f259496ad6a8563d2cb", 4),
        ],
        "collision_addresses_frequent": [
            ("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 184),
            ("0xdac17f958d2ee523a2206206994597c13d831ec7", 90),
            ("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49", 30),
            ("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 27),
            ("0x8390a1da07e376ef7add4be859ba74fb83aa02d5", 18),
        ],
    },
    "state_diffs": {"balance": 2577, "code": 3, "nonce": 880, "storage": 2594},
    "transactions": 1002,
}
