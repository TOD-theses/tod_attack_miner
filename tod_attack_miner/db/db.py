from pathlib import Path
import sqlite3
from typing import Any, Literal, Sequence, cast
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate

_TABLES = {
    "transactions": "(hash TEXT PRIMARY KEY, block_number INTEGER, tx_index INTEGER) STRICT",
    "accesses": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, value TEXT) STRICT",
    "dependencies": "(tx_a TEXT, tx_b HASH, block_diff INTEGER)",
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
            cursor.execute(
                "INSERT INTO transactions VALUES (?, ?, ?)",
                (prestate["txHash"], block_number, tx_index),
            )

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

    def build_dependencies(self):
        # map tx (key) to closest tx it depends on
        dependencies: dict[str, dict] = {}

        for c in self._get_collisions():
            if c["tx_b"] not in dependencies:
                dependencies[c["tx_b"]] = c
            else:
                prev = c["tx_b"]
                if c["block_dist"] < prev["block_dist"]:
                    dependencies[c["tx_b"]] = c
                elif (
                    c["block_dist"] == prev["block_dist"]
                    and c["tx_a_index"] > prev["tx_a_index"]
                ):
                    dependencies[c["tx_b"]] = c

        values = [
            (c["tx_a"], c["tx_b"], c["block_dist"]) for c in dependencies.values()
        ]
        self._con.cursor().executemany(
            "INSERT INTO dependencies VALUES (?, ?, ?)", values
        )

    def get_dependencies(self):
        return self._con.cursor().execute("SELECT * FROM dependencies").fetchall()

    def insert_block(self, block: BlockWithTransactions):
        self._blocks.append(block)

    def count_prestates(self) -> int:
        cursor = self._con.cursor()
        cursor.execute("SELECT count(*) FROM transactions")
        return cursor.fetchone()

    def _get_collisions(self, additional_filters=[]):
        cursor = self._con.cursor()
        additional_filters_clauses = ""
        if additional_filters:
            additional_filters_clauses = "AND " + " AND ".join(additional_filters)
        sql = f"""
SELECT a.tx_hash, b.tx_hash, group_concat(a.type), b.block_number - a.block_number, a.tx_index, b.tx_index
FROM accesses a
INNER JOIN accesses b
ON a.type = b.type
    {additional_filters_clauses}
    AND a.key = b.key
    AND a.value != b.value
    AND a.tx_index < b.tx_index
    AND a.block_number <= b.block_number
    GROUP BY a.tx_hash, b.tx_hash, a.tx_index, b.tx_index, b.block_number - a.block_number
"""
        cursor.execute(sql)
        results: Sequence[tuple[str, str, str, int, int, int]] = cursor.fetchall()
        result_dicts = [
            {
                "tx_a": tx_a,
                "tx_b": tx_b,
                "types": frozenset(cast(list[ACCESS_TYPE], types.split(","))),
                "block_dist": block_distance,
                "tx_a_index": tx_a_index,
                "tx_b_index": tx_b_index,
            }
            for tx_a, tx_b, types, block_distance, tx_a_index, tx_b_index in results
        ]
        print(result_dicts)
        return result_dicts

    def get_storage_collision_tx_pairs(
        self,
    ) -> Sequence[tuple[str, str, frozenset[ACCESS_TYPE]]]:
        collisions = self._get_collisions(["a.type = 'storage'"])
        return [(c["tx_a"], c["tx_b"], c["types"]) for c in collisions]

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
