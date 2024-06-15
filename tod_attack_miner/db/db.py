from pathlib import Path
import sqlite3
from typing import Any, Sequence
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate

_TABLES = {
    "prestates": "(hash TEXT PRIMARY KEY) STRICT",
    "storage_prestates": "(tx_hash TEXT, block_number INTEGER, tx_index INTEGER, addr TEXT, key TEXT, value TEXT) STRICT",
}


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
            cursor.execute("INSERT INTO prestates VALUES (?)", (prestate["txHash"],))

            for addr in prestate["result"]:
                for key, val in prestate["result"][addr].get("storage", {}).items():
                    values = (
                        prestate["txHash"],
                        block_number,
                        tx_index,
                        addr,
                        key,
                        val,
                    )
                    cursor.execute(
                        "INSERT INTO storage_prestates VALUES (?, ?, ?, ?, ?, ?)",
                        values,
                    )

    def insert_block(self, block: BlockWithTransactions):
        self._blocks.append(block)

    def count_prestates(self) -> int:
        cursor = self._con.cursor()
        cursor.execute("SELECT count(*) FROM prestates")
        return cursor.fetchone()

    def get_storage_collisions_tx_pairs(self) -> Sequence[tuple[str, str]]:
        cursor = self._con.cursor()
        sql = """
SELECT a.tx_hash, b.tx_hash
FROM storage_prestates a
INNER JOIN storage_prestates b
ON a.addr = b.addr
	AND a.key = b.key
    AND a.value != b.value
    AND a.tx_index < b.tx_index
    AND abs(b.block_number - a.block_number) <= 0
    GROUP BY a.tx_hash, b.tx_hash
"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def get_storage_collisions_contract_addresses(self) -> Any:
        cursor = self._con.cursor()
        sql = """
SELECT a.addr, count(a.tx_hash)/2 as tx_count
FROM storage_prestates a
INNER JOIN storage_prestates b
ON a.addr = b.addr
	AND a.key = b.key
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
