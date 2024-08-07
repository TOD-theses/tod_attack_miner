from typing import Sequence, TypedDict

TxData = TypedDict(
    "TxData",
    {
        "accessList": Sequence[dict],
        "blobVersionedHashes": Sequence[str],
        "blockHash": str,
        "blockNumber": int,
        "chainId": int,
        "data": bytes | str,
        "from": str,
        "gas": int,
        "gasPrice": int,
        "maxFeePerBlobGas": int,
        "maxFeePerGas": int,
        "maxPriorityFeePerGas": int,
        "hash": str,
        "input": str,
        "nonce": int,
        "r": str,
        "s": str,
        "to": str,
        "transactionIndex": int,
        "type": int | str,
        "v": int,
        "value": int,
        "yParity": int,
    },
)


class BlockWithTransactions(TypedDict):
    baseFeePerGas: int
    difficulty: int
    extraData: str
    gasLimit: int
    gasUsed: int
    hash: str
    logsBloom: str
    miner: str
    mixHash: str
    nonce: str
    number: int
    parentHash: str
    receiptsRoot: str
    sha3Uncles: str
    size: int
    stateRoot: str
    timestamp: int
    totalDifficulty: int
    transactions: Sequence[TxData]
    transactionsRoot: str
    uncles: Sequence[str]
    withdrawals: Sequence[dict]
    withdrawalsRoot: str
    parentBeaconBlockRoot: str
    blobGasUsed: int
    excessBlobGas: int

    # ExtraDataToPOAMiddleware replaces extraData w/ proofOfAuthorityData
    proofOfAuthorityData: str


class AccountState(TypedDict, total=False):
    balance: str
    code: str
    nonce: int
    storage: dict[str, str]


class TxPrestate(TypedDict):
    txHash: str
    result: dict[str, AccountState]


class PrePostState(TypedDict):
    pre: dict[str, AccountState]
    post: dict[str, AccountState]


class TxStateDiff(TypedDict):
    txHash: str
    result: PrePostState
