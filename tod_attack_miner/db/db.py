from pathlib import Path
import sqlite3
from typing import Literal, Sequence
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate, TxStateDiff

_TABLES = {
    "transactions": "(hash TEXT PRIMARY KEY, block_number INTEGER, tx_index INTEGER) STRICT",
    "accesses": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, value TEXT) STRICT",
    "state_diffs": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, pre_value TEXT, post_value TEXT) STRICT",
    "collisions": "(tx_write_hash TEXT, tx_access_hash, type TEXT, key TEXT, block_dist INTEGER)",
}

ACCESS_TYPE = (
    Literal["storage"] | Literal["code"] | Literal["balance"] | Literal["nonce"]
)
types: Sequence[ACCESS_TYPE] = ["storage", "code", "balance", "nonce"]


class DB:
    def __init__(self, database_path: Path) -> None:
        self._con = sqlite3.connect(database_path)
        self._setup_tables()

    def _setup_tables(self):
        with self._con:
            cursor = self._con.cursor()
            for name, definition in _TABLES.items():
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {name} {definition}")

    def insert_prestate(self, block_number: int, tx_index: int, prestate: TxPrestate):
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

    def insert_state_diff(
        self, block_number: int, tx_index: int, state_diff: TxStateDiff
    ):
        pre, post = state_diff["result"]["pre"], state_diff["result"]["post"]
        with self._con:
            cursor = self._con.cursor()

            state_diffs: list[tuple[int, int, str, ACCESS_TYPE, str, str, str]] = []

            for addr, prestate in pre.items():
                poststate = post[addr]

                if (pre_balance := prestate.get("balance")) is not None:
                    assert "balance" in poststate
                    post_balance = poststate["balance"]
                    assert pre_balance != post_balance

                    state_diffs.append(
                        (
                            block_number,
                            tx_index,
                            state_diff["txHash"],
                            "balance",
                            addr,
                            pre_balance,
                            post_balance,
                        )
                    )
                if (pre_code := prestate.get("code")) is not None:
                    assert "code" in poststate
                    post_code = poststate["code"]
                    assert pre_code != post_code
                    state_diffs.append(
                        (
                            block_number,
                            tx_index,
                            state_diff["txHash"],
                            "code",
                            addr,
                            pre_code,
                            post_code,
                        )
                    )
                if (pre_nonce := prestate.get("nonce")) is not None:
                    assert "nonce" in poststate
                    post_nonce = poststate["nonce"]
                    assert pre_nonce != post_nonce
                    state_diffs.append(
                        (
                            block_number,
                            tx_index,
                            state_diff["txHash"],
                            "nonce",
                            addr,
                            str(pre_nonce),
                            str(post_nonce),
                        )
                    )
                pre_storage = prestate.get("storage", {})
                post_storage = poststate.get("storage", {})
                for key, pre_val in pre_storage.items():
                    post_val = post_storage[key]
                    assert pre_val != post_val
                    state_diffs.append(
                        (
                            block_number,
                            tx_index,
                            state_diff["txHash"],
                            "storage",
                            f"{addr}_{key}",
                            pre_val,
                            post_val,
                        )
                    )

        cursor.executemany(
            "INSERT INTO state_diffs VALUES (?, ?, ?, ?, ?, ?, ?)",
            state_diffs,
        )

    def insert_conflicts(self):
        cursor = self._con.cursor()
        sql = """
INSERT INTO collisions
SELECT state_diffs.tx_hash, accesses.tx_hash, accesses.type, accesses.key, accesses.block_number - state_diffs.block_number
FROM accesses
INNER JOIN state_diffs
ON accesses.type = state_diffs.type
    AND accesses.key = state_diffs.key
    /* NOTE: more similar to Zhang et al.: AND accesses.value != state_diffs.pre_value */
    AND accesses.value = state_diffs.post_value
    AND (
        accesses.block_number - state_diffs.block_number > 0
        OR (accesses.block_number = state_diffs.block_number
            AND accesses.tx_index > state_diffs.tx_index)
    )
GROUP BY accesses.tx_hash, state_diffs.tx_hash, accesses.type, accesses.key, accesses.block_number - state_diffs.block_number
"""
        cursor.execute(sql)

    def get_conflicts_stats(self):
        return (
            self._con.cursor()
            .execute("SELECT type, COUNT(*) FROM collisions GROUP BY type")
            .fetchall()
        )

    def insert_block(self, block: BlockWithTransactions):
        pass

    def count_prestates(self) -> int:
        cursor = self._con.cursor()
        cursor.execute("SELECT count(*) FROM transactions")
        return cursor.fetchone()

    def _get_collisions(self, additional_filters=[]):
        cursor = self._con.cursor()
        filter = ""
        if additional_filters:
            filter = "WHERE " + " AND ".join(additional_filters)
        sql = f"""
SELECT tx_write_hash, tx_access_hash, type, key TEXT, block_dist INTEGER
FROM collisions
{filter}
"""
        cursor.execute(sql)
        results: Sequence[tuple[str, str, str, str, int]] = cursor.fetchall()
        result_dicts = [
            {
                "tx_write": tx_a,
                "tx_access": tx_b,
                "type": type,
                "key": key,
                "block_dist": block_dist,
            }
            for tx_a, tx_b, type, key, block_dist in results
        ]
        return result_dicts

    def get_collisions(self) -> Sequence[tuple[str, str, tuple[str, str, int]]]:
        return [
            (c["tx_write"], c["tx_access"], (c["type"], c["key"], c["block_dist"]))
            for c in self._get_collisions()
        ]

    def get_accesses_stats(self):
        return (
            self._con.cursor()
            .execute("SELECT type, COUNT(*) FROM accesses GROUP by type")
            .fetchall()
        )

    def get_state_diffs_stats(self):
        return (
            self._con.cursor()
            .execute("SELECT type, COUNT(*) FROM state_diffs GROUP by type")
            .fetchall()
        )

    def get_unique_addresses_stats(self):
        cursor = self._con.cursor()
        sql = """
SELECT SUBSTR(key, 1, 42), COUNT(*) as n
FROM collisions
GROUP BY SUBSTR(key, 1, 42) HAVING COUNT(*) >= 10
ORDER BY n DESC
"""
        return cursor.execute(sql).fetchall()

    def get_unique_addresses_total(self):
        cursor = self._con.cursor()
        sql = """
SELECT COUNT(DISTINCT SUBSTR(key, 1, 42))
FROM collisions
"""
        return cursor.execute(sql).fetchall()
