import json
from typing import Any
from web3 import Web3
from web3.types import RPCEndpoint
from web3.method import Method
from web3.datastructures import AttributeDict

from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate, TxStateDiff


class RPC:
    def __init__(self, archive_node_provider_url: str) -> None:
        self.w3 = Web3(Web3.HTTPProvider(archive_node_provider_url))

        self.w3.eth.attach_methods(
            {
                "debug_traceBlockByNumber": Method(
                    RPCEndpoint("debug_traceBlockByNumber")
                ),
                "eth_getBlockByNumber": Method(RPCEndpoint("eth_getBlockByNumber")),
                # NOTE: the stateDiff RPC method is expensive to call
                # rpc.trace_replay_block_transactions(block_number, ["stateDiff"])
            }
        )

    def fetch_block_with_transactions(self, block_number: int) -> BlockWithTransactions:
        block: AttributeDict = self.w3.eth.eth_getBlockByNumber(hex(block_number), True)  # type: ignore
        return _attribute_dict_to_dict(block)

    def fetch_prestates(self, block_number: int) -> list[TxPrestate]:
        trace: list[AttributeDict] = self.w3.eth.debug_traceBlockByNumber(  # type: ignore
            hex(block_number), {"tracer": "prestateTracer"}
        )
        return [_attribute_dict_to_dict(prestate) for prestate in trace]

    def fetch_state_diffs(self, block_number: int) -> list[TxStateDiff]:
        trace: list[AttributeDict] = self.w3.eth.debug_traceBlockByNumber(  # type: ignore
            hex(block_number),
            {"tracer": "prestateTracer", "tracerConfig": {"diffMode": True}},
        )
        return [_attribute_dict_to_dict(statediff) for statediff in trace]


def _attribute_dict_to_dict(attribute_dict: AttributeDict) -> Any:
    return json.loads(Web3.to_json(attribute_dict))  # type: ignore
