# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_tod_attack_miner_e2e num_candidates"] = 633

snapshots["test_tod_attack_miner_e2e stats"] = {
    "accesses": {"balance": 4663, "code": 2248, "nonce": 4332, "storage": 8239},
    "addresses_est": [
        ("0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5", 1067),
        ("0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97", 568),
        ("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 254),
        ("0xdac17f958d2ee523a2206206994597c13d831ec7", 97),
        ("0x28c6c06298d514db089934071355e5743bf21d60", 76),
        ("0x916b2aff900d06c526b4935f999462b65f1a24fe", 45),
        ("0x0481ef8086d96ddb32d1aefedadac619bea579db", 38),
        ("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49", 38),
        ("0x9430801ebaf509ad49202aabc5f5bc6fd8a3daf8", 38),
        ("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 31),
    ],
    "addresses_est_total": 233,
    "candidates": 633,
    "candidates_filters": {
        "candidates": {
            "before_filters": 2193,
            "final": 633,
            "original_without_same_value": 264234,
        },
        "filtered": {
            "block_producers": 786,
            "indirect_dependencies_quick": 386,
            "indirect_dependencies_recursive": 49,
            "recipient_eth_transfer": 151,
            "same_sender": 188,
        },
    },
    "conflicts": {"balance": 1526, "nonce": 879, "storage": 708},
    "state_diffs": {"balance": 2577, "code": 3, "nonce": 880, "storage": 2594},
}
