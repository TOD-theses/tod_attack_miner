from typing import Literal
from tod_attack_miner.rpc.types import AccountState, TxStateDiff


def state_diff_fill_implicit_fields(state_diff: TxStateDiff) -> None:
    """
    Insert implicit fields, such that each field in pre has a corresponding field in post and vice versa.
    See https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers#prestate-tracer
    """
    res = state_diff["result"]
    pre, post = res["pre"], res["post"]

    pre_addresses = set(pre.keys())
    post_addresses = set(post.keys())

    for deleted_addr in pre_addresses - post_addresses:
        post[deleted_addr] = account_deleted_state(pre[deleted_addr])

    for inserted_addr in post_addresses - pre_addresses:
        pre[inserted_addr] = account_inserted_state(post[inserted_addr])

    for modified_addr in pre_addresses & post_addresses:
        fill_poststate_with_unchanged_prestate(pre[modified_addr], post[modified_addr])


def fill_poststate_with_unchanged_prestate(
    prestate: AccountState, poststate: AccountState
):
    if "balance" in prestate:
        poststate.setdefault("balance", prestate["balance"])
    if "code" in prestate:
        poststate.setdefault("code", prestate["code"])
    if "nonce" in prestate:
        poststate.setdefault("nonce", prestate["nonce"])
    if "storage" in prestate or "storage" in poststate:
        if "storage" not in prestate:
            prestate["storage"] = {}
        if "storage" not in poststate:
            poststate["storage"] = {}
        keys_prestate = prestate["storage"].keys()
        keys_poststate = poststate["storage"].keys()
        added_slots = keys_poststate - keys_prestate
        removed_slots = keys_prestate - keys_poststate

        for key in added_slots:
            prestate["storage"][key] = "0x0"
        for key in removed_slots:
            poststate["storage"][key] = "0x0"


def account_inserted_state(poststate: AccountState):
    prestate: AccountState = {}
    if "balance" in poststate:
        # not precise, balance could exist before account creation
        prestate["balance"] = "0x0"
    if "code" in poststate:
        prestate["code"] = "0x0"
    if "nonce" in poststate:
        prestate["nonce"] = 0
    if "storage" in poststate:
        prestate["storage"] = {}
        for key in poststate["storage"]:
            prestate["storage"][key] = "0x0"
    return prestate


def account_deleted_state(prestate: AccountState):
    poststate: AccountState = {}
    if "balance" in prestate:
        poststate["balance"] = "0x0"
    if "code" in prestate:
        poststate["code"] = "0x0"
    if "nonce" in prestate:
        poststate["nonce"] = 0
    if "storage" in prestate:
        poststate["storage"] = {}
        for key in prestate["storage"]:
            poststate["storage"][key] = "0x0"
    return poststate


def state_diff_remove_unchanged_fields(state_diff: TxStateDiff) -> None:
    """
    Remove fields that did not change between pre and post.
    Ignores storage, as these should not be equal in pre and post.
    """
    pre = state_diff["result"]["pre"]
    post = state_diff["result"]["post"]

    for addr, prestate in pre.items():
        poststate = post[addr]

        types: list[Literal["balance"] | Literal["code"] | Literal["nonce"]] = [
            "balance",
            "code",
            "nonce",
        ]

        for type in types:
            if type in prestate and type in poststate:
                if prestate.get(type) == poststate.get(type):
                    del prestate[type]
                    del poststate[type]
