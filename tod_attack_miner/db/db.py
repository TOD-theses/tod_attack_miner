from pathlib import Path
import sqlite3
from typing import Any, Literal, Sequence
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate

_TABLES = {
    "transactions": "(hash TEXT PRIMARY KEY) STRICT",
    "accesses": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, value TEXT) STRICT",
}

ACCESS_TYPE = (
    Literal["storage"] | Literal["code"] | Literal["balance"] | Literal["nonce"]
)


class DB:
    def __init__(self, database_path: Path) -> None:
        self._con = sqlite3.connect(database_path)
        self._setup_tables()
        self._prestate_traces: list[tuple[int, TxPrestate]] = []
        self._blocks: list[BlockWithTransactions] = []

    def _setup_tables(self):
        with self._con:
            cursor = self._con.cursor()
            for name, definition in _TABLES.items():
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} {definition}")

    def insert_prestate(self, block_number: int, tx_index: int, prestate: TxPrestate):
        self._prestate_traces.append((block_number, prestate))
        with self._con:
            cursor = self._con.cursor()
            cursor.execute("INSERT INTO transactions VALUES (?)", (prestate["txHash"],))

            accesses: list[tuple[int, int, str, ACCESS_TYPE, str, str]] = []
            for addr, state in prestate["result"].items():
                if (balance := state.get("balance")) is not None:
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"],
                            "balance",
                            addr,
                            balance,
                        )
                    )
                if (code := state.get("code")) is not None:
                    accesses.append(
                        (block_number, tx_index, prestate["txHash"], "code", addr, code)
                    )
                if (nonce := state.get("nonce")) is not None:
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"],
                            "nonce",
                            addr,
                            str(nonce),
                        )
                    )
                for key, val in state.get("storage", {}).items():
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"],
                            "storage",
                            f"{addr}_{key}",
                            val,
                        )
                    )

        cursor.executemany(
            "INSERT INTO accesses VALUES (?, ?, ?, ?, ?, ?)",
            accesses,
        )

    def insert_block(self, block: BlockWithTransactions):
        self._blocks.append(block)

    def count_prestates(self) -> int:
        cursor = self._con.cursor()
        cursor.execute("SELECT count(*) FROM transactions")
        return cursor.fetchone()

    def get_storage_collision_tx_pairs(
        self,
    ) -> Sequence[tuple[str, str, frozenset[ACCESS_TYPE]]]:
        cursor = self._con.cursor()
        sql = """
SELECT a.tx_hash, b.tx_hash, group_concat(a.type)
FROM accesses a
INNER JOIN accesses b
ON a.type = b.type
    AND a.type = 'storage'
    AND a.key = b.key
    AND a.value != b.value
    AND a.tx_index < b.tx_index
    AND abs(b.block_number - a.block_number) <= 0
    GROUP BY a.tx_hash, b.tx_hash
"""
        cursor.execute(sql)
        results: Sequence[tuple[str, str, str]] = cursor.fetchall()
        return [
            (tx_a, tx_b, frozenset(types.split(","))) for tx_a, tx_b, types in results
        ]  # type: ignore

    def get_storage_collisions_contract_addresses(self) -> Any:
        cursor = self._con.cursor()
        sql = """
SELECT a.addr, count(a.tx_hash)/2 as tx_count
FROM accesses a
INNER JOIN accesses b
ON a.type = b.type
    AND a.type = 'storage'
    AND a.value != b.value
    AND abs(b.block_number - a.block_number) <= 0
    GROUP BY a.addr
ORDER BY tx_count DESC
"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def get_all_blocks(self) -> list[BlockWithTransactions]:
        return self._blocks
