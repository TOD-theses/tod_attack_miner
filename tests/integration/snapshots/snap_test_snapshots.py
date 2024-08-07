# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_tod_attack_miner_e2e first_candidate"] = {
    "block_dist": 0,
    "tx_a": "0x001811be6d2019216746d9c9da9f847160dc18a9d6dba362d4b265c2dd7e649a",
    "tx_b": "0xcfb5968f11b15c15cfb23234dc56f16c5811485a6cae702195317a2f86ce2c6c",
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

snapshots["test_tod_attack_miner_evaluation evaluation results"] = [
    {
        "filter": "indirect_dependencies_recursive",
        "tx_a": "0x1b99d2ee257a00b5196b39534366fde8fded0cd3bfe639f161d12a9ca011adaf",
        "tx_b": "0x9213ae52ca8bf02107081b9340dd0d03ff533ac1040abeb873b686ed6427b303",
    },
    {
        "filter": "recipient_eth_transfer",
        "tx_a": "0x3904535cb0f60bc6a3bf7082d05fb363a4375eb0ca1c85dee827007192b00413",
        "tx_b": "0x6016a7e14ef9b7ecc80985ace338e8894de892a58e941dd45dbb90c729079cb4",
    },
    {
        "filter": "collision",
        "tx_a": "0x40ca117ccc4933dd5b30e399f64673068c622802bdbd728f84b212cd197bf51a",
        "tx_b": "0x31c5b4782a75a1f5f513cd86ede1a8c0af54baa9511982f43a57988036ed0fed",
    },
    {
        "filter": "nonces",
        "tx_a": "0x5e6e4bae8fa62e86b85b2c5f74f67ee97628112e3b12c20f348ace13a2548ca3",
        "tx_b": "0xd884d83c00fa8ddc79306c290988c5b8c81c6fceeae1986add056cd1bf7d5f88",
    },
    {
        "filter": "same_sender",
        "tx_a": "0x6d936541a9e0befab9bf765c153fe1f0b9728dd6a6b6ba67cc757a56d115a2e8",
        "tx_b": "0x112ac55e0122204165ab94bad060ffcee026e4db572f74b3325d56bd0950ade1",
    },
    {
        "filter": None,
        "tx_a": "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "tx_b": "0x1ea1709059406a15686edef98de051fdfb5e854cc0991687b9573cba9005b021",
    },
    {
        "filter": "same-value collision",
        "tx_a": "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "tx_b": "0x65df49728edca9888255b262f082c1a13beaf1dca58bcb8004920b1fbb53e86b",
    },
    {
        "filter": "indirect_dependencies_recursive",
        "tx_a": "0x775232180c49821d4208b3c5470d6367de5b96810c79ae0993aeb98ada762ee8",
        "tx_b": "0x94029b952ede83cd26f48ab40fad24851a517696b2785b631cdacb02795934cf",
    },
    {
        "filter": "block_producers",
        "tx_a": "0x98054dd5b5973d3b953029fb286e416994736313f4f986ba3d11143f4b9fbc72",
        "tx_b": "0xa68290ce02acc90bd3abd5ab1dd7b6fa26dd92d0b4e43fbb29737e8d6d54d926",
    },
    {
        "filter": "indirect_dependencies_quick",
        "tx_a": "0xf812335569705e032f8eca9fff94d3348e29d748bd9ed4e2acd76fe54dbec42d",
        "tx_b": "0xd2b8e8cff425ae336c6084a9d7fc1c7d33d599fdf00c93eda40339e37ca6b12d",
    },
]
