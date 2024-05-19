from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate


class DB:
    def __init__(self) -> None:
        self._prestate_traces: list[tuple[int, TxPrestate]] = []
        self._blocks: list[BlockWithTransactions] = []

    def insert_prestate(self, block_number: int, prestate: TxPrestate):
        self._prestate_traces.append((block_number, prestate))

    def insert_block(self, block: BlockWithTransactions):
        self._blocks.append(block)

    def get_all_prestates(self) -> list[tuple[int, TxPrestate]]:
        return self._prestate_traces

    def get_all_blocks(self) -> list[BlockWithTransactions]:
        return self._blocks
