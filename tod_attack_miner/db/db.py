import hashlib
from typing import Iterable, Literal, Sequence, TypedDict, cast

import psycopg
import psycopg.sql
from tod_attack_miner.ethutils.skeleton import skeletize
from tod_attack_miner.rpc.types import BlockWithTransactions, TxPrestate, TxStateDiff

_TABLES = {
    "blocks": "(block_number INTEGER PRIMARY KEY, producer TEXT)",
    "transactions": "(hash TEXT PRIMARY KEY, block_number INTEGER, tx_index INTEGER, sender TEXT)",
    "accesses": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, value TEXT)",
    "state_diffs": "(block_number INTEGER, tx_index INTEGER, tx_hash TEXT, type TEXT, key TEXT, pre_value TEXT, post_value TEXT)",
    "collisions": "(tx_write_hash TEXT, tx_access_hash TEXT, type TEXT, key TEXT, block_dist INTEGER, PRIMARY KEY(tx_write_hash, tx_access_hash, type, key))",
    "candidates": "(tx_write_hash TEXT, tx_access_hash TEXT, PRIMARY KEY(tx_write_hash, tx_access_hash))",
    "codes": "(addr TEXT, code TEXT, hash TEXT, PRIMARY KEY(addr))",
    "skeletons": "(addr TEXT, family TEXT, hash TEXT, PRIMARY KEY(addr))",
}
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


class Candidate(TypedDict):
    tx_a: str
    tx_b: str
    block_dist: int
    types: Sequence[ACCESS_TYPE]


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
            codes: list[tuple[str, str, str]] = []

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
                    codes.append((addr.lower(), code, hash_code(code)))
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
            cursor.executemany(
                "INSERT INTO codes VALUES (%s, %s, %s) ON CONFLICT (addr) DO UPDATE SET code=EXCLUDED.code, hash=EXCLUDED.hash",
                codes,
            )
        self._con.commit()

    def insert_state_diff(
        self, block_number: int, tx_index: int, state_diff: TxStateDiff
    ):
        pre, post = state_diff["result"]["pre"], state_diff["result"]["post"]
        with self._con.cursor() as cursor:
            state_diffs: list[tuple[int, int, str, ACCESS_TYPE, str, str, str]] = []
            codes: list[tuple[str, str, str]] = []

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
                    # we use the post_code, since pre_code must always be empty
                    codes.append((addr.lower(), post_code, hash_code(post_code)))
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

            cursor.executemany(
                "INSERT INTO codes VALUES (%s, %s, %s) ON CONFLICT (addr) DO UPDATE SET code=EXCLUDED.code, hash=EXCLUDED.hash",
                codes,
            )
        self._con.commit()

    def insert_skeletons(self):
        codes = self.get_codes()
        mapped_codes = [(addr, code_skeleton_hash(c), hash) for addr, c, hash in codes]
        self._insert_code_skeletons(mapped_codes)

    def get_codes(self) -> Sequence[tuple[str, str, str]]:
        with self._con.cursor() as cursor:
            return cursor.execute("SELECT addr, code, hash FROM codes").fetchall()

    def _insert_code_skeletons(self, mapped_codes: Iterable[tuple[str, str, str]]):
        with self._con.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO skeletons VALUES (%s, %s, %s)", mapped_codes
            )

    def insert_collisions(self):
        self.insert_read_write_collisions()
        self.insert_write_write_collisions()

    def insert_read_write_collisions(self):
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
    ON CONFLICT DO NOTHING
    """
            cursor.execute(sql)
        self._con.commit()

    def insert_write_write_collisions(self):
        with self._con.cursor() as cursor:
            sql = """
    INSERT INTO collisions
    SELECT b.tx_hash, a.tx_hash, a.type, a.key, a.block_number - b.block_number
    FROM state_diffs a
    INNER JOIN state_diffs b
    ON a.type = b.type
        AND a.key = b.key
        AND a.pre_value = b.post_value
        AND (
            a.block_number - b.block_number > 0
            OR (a.block_number = b.block_number
                AND a.tx_index > b.tx_index)
        )
    GROUP BY a.tx_hash, b.tx_hash, a.type, a.key, a.block_number - b.block_number
    ON CONFLICT DO NOTHING
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
            self._con.commit()
            return cursor.rowcount

    def remove_collisions_without_candidate(self) -> int:
        sql = """DELETE FROM collisions
WHERE NOT EXISTS (
    SELECT *
    FROM candidates c
    WHERE c.tx_write_hash = collisions.tx_write_hash
      AND c.tx_access_hash = collisions.tx_access_hash
)"""
        with self._con.cursor() as cursor:
            cursor.execute(sql)
            self._con.commit()
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

    def count_transactions(self) -> int:
        with self._con.cursor() as cursor:
            return cursor.execute("SELECT COUNT(*) FROM transactions").fetchall()[0][0]

    def count_candidates(self) -> int:
        with self._con.cursor() as cursor:
            return cursor.execute("SELECT COUNT(*) FROM candidates").fetchall()[0][0]

    def count_unique_candidate_transactions(self) -> int:
        sql = """
SELECT COUNT(DISTINCT hash)
FROM transactions
INNER JOIN candidates ON tx_write_hash = hash OR tx_access_hash = hash"""
        with self._con.cursor() as cursor:
            return cursor.execute(sql).fetchall()[0][0]

    def most_frequent_candidate_transactions(self) -> Sequence[tuple[str, int]]:
        sql = """
SELECT hash, COUNT(*) as n
FROM transactions
INNER JOIN candidates ON tx_write_hash = hash OR tx_access_hash = hash
GROUP BY hash
ORDER BY n DESC
LIMIT 5"""
        with self._con.cursor() as cursor:
            return cursor.execute(sql).fetchall()

    def transactions_candidate_frequency(self) -> Sequence[tuple[int, int]]:
        sql = """
SELECT n, COUNT(*)
FROM (
    SELECT COUNT(*) as n
    FROM transactions
    INNER JOIN candidates ON tx_write_hash = hash OR tx_access_hash = hash
    GROUP BY hash
) x
GROUP BY n
ORDER BY n DESC
"""
        with self._con.cursor() as cursor:
            return cursor.execute(sql).fetchall()

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

    def get_candidates(self) -> Sequence[Candidate]:
        with self._con.cursor() as cursor:
            sql = """
SELECT candidates.tx_write_hash, candidates.tx_access_hash, block_dist, string_agg(DISTINCT type, '|')
FROM candidates
INNER JOIN collisions
ON candidates.tx_write_hash = collisions.tx_write_hash AND candidates.tx_access_hash = collisions.tx_access_hash 
GROUP BY candidates.tx_write_hash, candidates.tx_access_hash, block_dist
"""
            candidates: Iterable[tuple[str, str, int, str]] = cursor.execute(sql)

            return [
                {
                    "tx_a": tx_a,
                    "tx_b": tx_b,
                    "block_dist": block_dist,
                    "types": cast(Sequence[ACCESS_TYPE], types.split("|")),
                }
                for tx_a, tx_b, block_dist, types in candidates
            ]

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

    def get_collisions_stats(self):
        sql = """
SELECT type, COUNT(*)
FROM collisions
GROUP BY type
"""
        return dict(self._con.cursor().execute(sql).fetchall())

    def most_frequent_collisions_addresses(self):
        cursor = self._con.cursor()
        sql = """
SELECT SUBSTR(key, 1, 42) as addr, COUNT(*) as n
FROM collisions
GROUP BY SUBSTR(key, 1, 42)
ORDER BY n DESC, addr ASC
LIMIT 5
"""
        return cursor.execute(sql).fetchall()

    def collisions_addresses_frequency(self) -> Sequence[tuple[int, int]]:
        sql = """
SELECT n, COUNT(*)
FROM (
    SELECT SUBSTR(key, 1, 42) as addr, COUNT(*) as n
    FROM collisions
    GROUP BY SUBSTR(key, 1, 42)
) x
GROUP BY n
ORDER BY n DESC
"""
        with self._con.cursor() as cursor:
            return cursor.execute(sql).fetchall()

    def count_unique_collision_addresses(self):
        cursor = self._con.cursor()
        sql = """
SELECT COUNT(DISTINCT SUBSTR(key, 1, 42))
FROM collisions
"""
        return cursor.execute(sql).fetchall()[0][0]


def hash_code(code: str) -> str:
    """Some hash of the code, not the EVM hash"""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def code_skeleton_hash(code: str) -> str:
    code_without_prefix = code[2:]
    if code_without_prefix == "0":
        code_without_prefix = ""
    skelcode = skeletize(bytes.fromhex(code_without_prefix)).hex()
    return hash_code(skelcode)
