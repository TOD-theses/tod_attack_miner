from tod_attack_miner.rpc.state_diff_utils import (
    state_diff_fill_implicit_fields,
    state_diff_remove_unchanged_fields,
)
from tod_attack_miner.rpc.types import TxStateDiff


def test_state_diff_fill_implicit_fields_empty():
    state_diff: TxStateDiff = {
        "txHash": "0xabcd",
        "result": {
            "pre": {},
            "post": {},
        },
    }

    state_diff_fill_implicit_fields(state_diff)

    assert not state_diff["result"]["pre"]
    assert not state_diff["result"]["post"]


def test_state_diff_fill_implicit_fields_modified():
    state_diff: TxStateDiff = {
        "txHash": "0x546ae70f03245666451baa00dafa31f548b6d43a92ec5d900f1ea5c33ba294e0",
        "result": {
            "post": {
                "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5": {
                    "balance": "0xcb409091cfdb008d"
                },
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x170e9331b28b174",
                    "nonce": 51,
                },
                "0xdb765e0b103b548a625163796b58065e161a7d12": {
                    "balance": "0x313281aa453c3a00",
                    "storage": {
                        "0x1234": "0x1111",
                    },
                },
            },
            "pre": {
                "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5": {
                    "balance": "0xcb406a5eecc6608d",
                    "nonce": 982337,
                },
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x3291e8457bbf451c",
                    "nonce": 50,
                },
                "0xdb765e0b103b548a625163796b58065e161a7d12": {
                    "balance": "0x11e66bbc5a3a00",
                    "nonce": 7,
                    "storage": {
                        "0x5678": "0x2222",
                    },
                },
            },
        },
    }

    state_diff_fill_implicit_fields(state_diff)

    assert state_diff["result"]["post"][
        "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5"
    ] == {
        "balance": "0xcb409091cfdb008d",
        "nonce": 982337,
    }
    assert state_diff["result"]["post"][
        "0xd143677c48256c4a22560add96e44eebfa331840"
    ] == {"balance": "0x170e9331b28b174", "nonce": 51}
    assert state_diff["result"]["post"][
        "0xdb765e0b103b548a625163796b58065e161a7d12"
    ] == {
        "balance": "0x313281aa453c3a00",
        "nonce": 7,
        "storage": {
            "0x1234": "0x1111",
            "0x5678": "0x0",
        },
    }
    assert state_diff["result"]["pre"][
        "0xdb765e0b103b548a625163796b58065e161a7d12"
    ].get("storage") == {
        "0x1234": "0x0",
        "0x5678": "0x2222",
    }


def test_state_diff_fill_implicit_fields_inserted_account():
    state_diff: TxStateDiff = {
        "txHash": "0x546ae70f03245666451baa00dafa31f548b6d43a92ec5d900f1ea5c33ba294e0",
        "result": {
            "post": {
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x170e9331b28b174",
                    "nonce": 1,
                    "storage": {"0x1234": "0x1111"},
                },
            },
            "pre": {},
        },
    }

    state_diff_fill_implicit_fields(state_diff)

    assert state_diff["result"]["pre"].get(
        "0xd143677c48256c4a22560add96e44eebfa331840"
    ) == {
        "balance": "0x0",
        "nonce": 0,
        "storage": {
            "0x1234": "0x0",
        },
    }


def test_state_diff_fill_implicit_fields_deleted_account():
    state_diff: TxStateDiff = {
        "txHash": "0x546ae70f03245666451baa00dafa31f548b6d43a92ec5d900f1ea5c33ba294e0",
        "result": {
            "post": {},
            "pre": {
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x170e9331b28b174",
                    "nonce": 1,
                    "storage": {"0x1234": "0x1111"},
                },
            },
        },
    }

    state_diff_fill_implicit_fields(state_diff)

    assert state_diff["result"]["post"].get(
        "0xd143677c48256c4a22560add96e44eebfa331840"
    ) == {
        "balance": "0x0",
        "nonce": 0,
        "storage": {
            "0x1234": "0x0",
        },
    }


def test_state_diff_remove_unchanged_fields():
    state_diff: TxStateDiff = {
        "txHash": "0x546ae70f03245666451baa00dafa31f548b6d43a92ec5d900f1ea5c33ba294e0",
        "result": {
            "post": {
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x170e9331b28b174",
                    "nonce": 2,
                },
            },
            "pre": {
                "0xd143677c48256c4a22560add96e44eebfa331840": {
                    "balance": "0x170e9331b28b174",
                    "nonce": 1,
                },
            },
        },
    }

    state_diff_remove_unchanged_fields(state_diff)

    assert state_diff["result"]["pre"][
        "0xd143677c48256c4a22560add96e44eebfa331840"
    ] == {"nonce": 1}
    assert state_diff["result"]["post"][
        "0xd143677c48256c4a22560add96e44eebfa331840"
    ] == {"nonce": 2}
