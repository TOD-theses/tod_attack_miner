import hashlib
from typing import Literal, Sequence, cast

import psycopg
import psycopg.sql
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate, TxStateDiff

_TABLES = {
    "blocks": "(block_number INTEGER PRIMARY KEY, producer TEXT)",
    "transactions": "(hash TEXT PRIMARY KEY, block_number INTEGER, tx_index INTEGER, sender TEXT)",
    "accesses": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, value TEXT)",
    "state_diffs": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, pre_value TEXT, post_value TEXT)",
    "collisions": "(tx_write_hash TEXT, tx_access_hash TEXT, type TEXT, key TEXT, block_dist INTEGER)",
    "candidates": "(tx_write_hash TEXT, tx_access_hash TEXT, PRIMARY KEY(tx_write_hash, tx_access_hash))",
}
# TODO: check if indexes are worth it
_INDEXES = {
    "accesses_type_key": "accesses(type, key, value)",
    "accesses_tx_hash": "accesses(tx_hash)",
    "state_diffs_type_key": "state_diffs(type, key, post_value)",
    "transactions_hash_sender": "transactions(hash, sender)",
    "blocks_number_producer": "blocks(block_number, producer)",
}

ACCESS_TYPE = (
    Literal["storage"] | Literal["code"] | Literal["balance"] | Literal["nonce"]
)
types: Sequence[ACCESS_TYPE] = ["storage", "code", "balance", "nonce"]


class DB:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._con: psycopg.Connection = conn
        self._setup_tables()

    def _setup_tables(self):
        with self._con.cursor() as cursor:
            for name, definition in _TABLES.items():
                cursor.execute(
                    cast(
                        psycopg.sql.SQL,
                        f"CREATE TABLE IF NOT EXISTS {name} {definition}",
                    )
                )
            for name, definition in _INDEXES.items():
                cursor.execute(
                    cast(
                        psycopg.sql.SQL,
                        f"CREATE INDEX IF NOT EXISTS {name} ON {definition}",
                    )
                )
            self._con.commit()

    def insert_prestate(self, block_number: int, tx_index: int, prestate: TxPrestate):
        with self._con.cursor() as cursor:
            accesses: list[tuple[int, int, str, ACCESS_TYPE, str, str]] = []
            for addr, state in prestate["result"].items():
                if (balance := state.get("balance")) is not None:
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"].lower(),
                            "balance",
                            addr.lower(),
                            balance.lower(),
                        )
                    )
                if (code := state.get("code")) is not None:
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"].lower(),
                            "code",
                            addr.lower(),
                            hash_code(code),
                        )
                    )
                if (nonce := state.get("nonce")) is not None:
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"].lower(),
                            "nonce",
                            addr.lower(),
                            str(nonce),
                        )
                    )
                for key, val in state.get("storage", {}).items():
                    accesses.append(
                        (
                            block_number,
                            tx_index,
                            prestate["txHash"].lower(),
                            "storage",
                            f"{addr}_{key}".lower(),
                            val.lower(),
                        )
                    )

            cursor.executemany(
                "INSERT INTO accesses VALUES (%s, %s, %s, %s, %s, %s)",
                accesses,
            )
        self._con.commit()

    def insert_state_diff(
        self, block_number: int, tx_index: int, state_diff: TxStateDiff
    ):
        pre, post = state_diff["result"]["pre"], state_diff["result"]["post"]
        with self._con.cursor() as cursor:
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
                            state_diff["txHash"].lower(),
                            "balance",
                            addr.lower(),
                            pre_balance.lower(),
                            post_balance.lower(),
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
                            state_diff["txHash"].lower(),
                            "code",
                            addr.lower(),
                            hash_code(pre_code),
                            hash_code(post_code),
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
                            state_diff["txHash"].lower(),
                            "nonce",
                            addr.lower(),
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
                            state_diff["txHash"].lower(),
                            "storage",
                            f"{addr}_{key}".lower(),
                            pre_val.lower(),
                            post_val.lower(),
                        )
                    )

            cursor.executemany(
                "INSERT INTO state_diffs VALUES (%s, %s, %s, %s, %s, %s, %s)",
                state_diffs,
            )
        self._con.commit()

    def insert_conflicts(self):
        with self._con.cursor() as cursor:
            sql = """
    INSERT INTO collisions
    SELECT state_diffs.tx_hash, accesses.tx_hash, accesses.type, accesses.key, accesses.block_number - state_diffs.block_number
    FROM accesses
    INNER JOIN state_diffs
    ON accesses.type = state_diffs.type
        AND accesses.key = state_diffs.key
        AND accesses.value = state_diffs.post_value
        AND (
            accesses.block_number - state_diffs.block_number > 0
            OR (accesses.block_number = state_diffs.block_number
                AND accesses.tx_index > state_diffs.tx_index)
        )
    GROUP BY accesses.tx_hash, state_diffs.tx_hash, accesses.type, accesses.key, accesses.block_number - state_diffs.block_number
    """
            cursor.execute(sql)
        self._con.commit()

    def insert_candidates(self):
        with self._con.cursor() as cursor:
            sql = """INSERT INTO candidates SELECT tx_write_hash, tx_access_hash FROM collisions GROUP BY tx_write_hash, tx_access_hash"""
            cursor.execute(sql)
        self._con.commit()

    def remove_candidates_without_collision(self) -> int:
        sql = """DELETE FROM candidates
WHERE NOT EXISTS (
    SELECT *
    FROM collisions c
    WHERE c.tx_write_hash = candidates.tx_write_hash
      AND c.tx_access_hash = candidates.tx_access_hash
)"""
        with self._con.cursor() as cursor:
            cursor.execute(sql)
            return cursor.rowcount

    def count_candidates_original(self):
        with self._con.cursor() as cursor:
            sql = """
            SELECT COUNT(*)
            FROM (
    SELECT 1
    FROM accesses
    INNER JOIN state_diffs
    ON accesses.type = state_diffs.type
        AND accesses.key = state_diffs.key
        AND (
            accesses.block_number - state_diffs.block_number > 0
            OR (accesses.block_number = state_diffs.block_number
                AND accesses.tx_index > state_diffs.tx_index)
        )
    GROUP BY accesses.tx_hash, state_diffs.tx_hash
    ) x
    """
            return cursor.execute(sql).fetchall()[0][0]

    def count_candidates(self) -> int:
        with self._con.cursor() as cursor:
            return cursor.execute("SELECT COUNT(*) FROM candidates").fetchall()[0][0]

    def insert_block(self, block: BlockWithTransactions):
        tx_values = [
            (
                tx["hash"].lower(),
                block["number"],
                tx["transactionIndex"],
                tx["from"].lower(),
            )
            for tx in block["transactions"]
        ]

        with self._con.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO transactions VALUES (%s, %s, %s, %s)",
                tx_values,
            )
            cursor.execute(
                "INSERT INTO blocks VALUES (%s, %s)",
                (block["number"], block["miner"].lower()),
            )
        self._con.commit()

    def _get_collisions(self):
        cursor = self._con.cursor()
        sql = """
SELECT tx_write_hash, tx_access_hash, type, key TEXT, block_dist INTEGER
FROM collisions
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

    def get_candidates(self) -> Sequence[tuple[str, str]]:
        with self._con.cursor() as cursor:
            return cursor.execute(
                "SELECT tx_write_hash, tx_access_hash FROM candidates"
            ).fetchall()

    def get_accesses_stats(self):
        return dict(
            self._con.cursor()
            .execute("SELECT type, COUNT(*) FROM accesses GROUP by type")
            .fetchall()
        )

    def get_state_diffs_stats(self):
        return dict(
            self._con.cursor()
            .execute("SELECT type, COUNT(*) FROM state_diffs GROUP by type")
            .fetchall()
        )

    def get_conflicts_stats(self):
        sql = """
SELECT type, COUNT(*)
FROM collisions
INNER JOIN candidates
ON collisions.tx_write_hash = candidates.tx_write_hash
AND collisions.tx_access_hash = candidates.tx_access_hash
GROUP BY type
"""
        return dict(self._con.cursor().execute(sql).fetchall())

    def get_unique_addresses_stats(self):
        cursor = self._con.cursor()
        sql = """
SELECT SUBSTR(key, 1, 42) as addr, COUNT(*) as n
FROM collisions
INNER JOIN candidates
ON collisions.tx_write_hash = candidates.tx_write_hash
AND collisions.tx_access_hash = candidates.tx_access_hash
GROUP BY SUBSTR(key, 1, 42)
ORDER BY n DESC, addr ASC
LIMIT 10
"""
        return cursor.execute(sql).fetchall()

    def get_unique_addresses_total(self):
        cursor = self._con.cursor()
        sql = """
SELECT COUNT(DISTINCT SUBSTR(key, 1, 42))
FROM collisions
INNER JOIN candidates
ON collisions.tx_write_hash = candidates.tx_write_hash
AND collisions.tx_access_hash = candidates.tx_access_hash
"""
        return cursor.execute(sql).fetchall()[0][0]


def hash_code(code: str) -> str:
    """Some hash of the code, not the EVM hash"""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()
