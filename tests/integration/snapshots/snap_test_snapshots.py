# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_tod_attack_miner_e2e num_candidates"] = 633

snapshots["test_tod_attack_miner_e2e stats"] = {
    "accesses": {"balance": 4663, "code": 2248, "nonce": 4332, "storage": 8239},
    "addresses_est": [
        ("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", 186),
        ("0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5", 183),
        ("0xdac17f958d2ee523a2206206994597c13d831ec7", 90),
        ("0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97", 67),
        ("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49", 30),
        ("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 27),
        ("0x8390a1da07e376ef7add4be859ba74fb83aa02d5", 18),
        ("0x0d7e906bd9cafa154b048cfa766cc1e54e39af9b", 16),
        ("0x0ec68c5b10f21effb74f2a5c61dfe6b08c0db6cb", 16),
        ("0x6774bcbd5cecef1336b5300fb5186a12ddd8b367", 16),
    ],
    "addresses_est_total": 87,
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
    "conflicts": {"balance": 232, "nonce": 250, "storage": 412},
    "state_diffs": {"balance": 2577, "code": 3, "nonce": 880, "storage": 2594},
}
