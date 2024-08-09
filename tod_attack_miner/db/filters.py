from typing import Callable, Iterable
import psycopg
import psycopg.sql
from tod_attack_miner.db.db import DB


def filter_block_producers(db: DB):
    sql = """
DELETE FROM collisions c
USING blocks
WHERE key = producer AND type = 'balance'
    """
    with db._con.cursor() as cursor:
        cursor.execute(sql)
    return db.remove_candidates_without_collision()


def create_block_window_filter(window_size: int | None):
    def block_window_filter(db: DB):
        if window_size is None:
            return 0
        sql = psycopg.sql.SQL("""
    DELETE FROM collisions c
    WHERE block_dist >= {}""").format(window_size)
        with db._con.cursor() as cursor:
            cursor.execute(sql)
        return db.remove_candidates_without_collision()

    return block_window_filter


def filter_nonces(db: DB):
    with db._con.cursor() as cursor:
        cursor.execute("DELETE FROM collisions WHERE type = 'nonce'")
    return db.remove_candidates_without_collision()


def filter_codes(db: DB):
    with db._con.cursor() as cursor:
        cursor.execute("DELETE FROM collisions WHERE type = 'code'")
    return db.remove_candidates_without_collision()


def filter_same_sender(db: DB):
    sql = """
DELETE FROM collisions
USING transactions a, transactions b
WHERE a.sender = b.sender
    AND collisions.tx_access_hash = a.hash
    AND collisions.tx_write_hash = b.hash
"""
    with db._con.cursor() as cursor:
        cursor.execute(sql)
    return db.remove_candidates_without_collision()


def filter_second_tx_ether_transfer(db: DB):
    sql = """
DELETE FROM collisions
WHERE NOT EXISTS (
    SELECT 1
    FROM accesses
    WHERE collisions.tx_access_hash = accesses.tx_hash
      AND accesses.type = 'code'
)
"""
    with db._con.cursor() as cursor:
        cursor.execute(sql)
    return db.remove_candidates_without_collision()


def filter_indirect_dependencies_quick(db: DB):
    with db._con.cursor() as cursor:
        sql = """
DELETE FROM candidates d
USING candidates a, candidates b
/* (A, X) (X, B). candidates d is (A, B). candidates a is (A, X). candidates b is (X, B) */
/* A = A AND B = B */
WHERE d.tx_write_hash = a.tx_write_hash AND d.tx_access_hash = b.tx_access_hash
/* B != X AND A != X */
  AND d.tx_access_hash != a.tx_access_hash AND d.tx_write_hash != b.tx_write_hash
/* X = X */
  AND a.tx_access_hash = b.tx_write_hash
"""
        cursor.execute(sql)
        deleted = cursor.rowcount
    db.remove_collisions_without_candidate()
    return deleted


def filter_indirect_dependencies_recursive(db: DB):
    sql = psycopg.sql.SQL("""
WITH RECURSIVE depends_on(tx_a, tx_b, min_block_number, min_tx_index, tx_x) AS (
    SELECT tx_write_hash, tx_access_hash, block_number, tx_index, tx_access_hash
    FROM candidates
    INNER JOIN transactions ON hash = tx_write_hash
  UNION
    SELECT tx_a, tx_b, min_block_number, min_tx_index, tx_write_hash
    FROM depends_on, candidates
    INNER JOIN transactions ON hash = tx_write_hash
    WHERE depends_on.tx_x = tx_access_hash
      AND (block_number > min_block_number
           OR block_number = min_block_number AND tx_index > min_tx_index) 
),
indirect_dependencies_candidates AS (
  SELECT tx_a, tx_b
  FROM depends_on
  INNER JOIN candidates ON tx_access_hash = tx_x
  WHERE tx_a = tx_write_hash
    AND tx_b != tx_x
    
  LIMIT {}
)
DELETE FROM candidates
USING indirect_dependencies_candidates
WHERE tx_write_hash = tx_a AND tx_access_hash = tx_b""").format(10000)
    finished = False
    deleted = 0
    while not finished:
        with db._con.cursor() as cursor:
            cursor.execute(sql)
            finished = cursor.rowcount == 0
            deleted += cursor.rowcount
        db._con.commit()
    db.remove_collisions_without_candidate()
    return deleted


def get_evaluation_indirect_dependencies_recursive(
    db: DB, max_depth: int
) -> Iterable[tuple[str, str, str]]:
    sql = psycopg.sql.SQL("""
WITH RECURSIVE depends_on(tx_a, tx_b, min_block_number, min_tx_index, tx_x, path, depth) AS (
    SELECT tx_write_hash, tx_access_hash, block_number, tx_index, tx_access_hash, tx_access_hash, 1
    FROM evaluation_candidates
    INNER JOIN transactions ON hash = tx_write_hash
  UNION
    SELECT tx_a, tx_b, min_block_number, min_tx_index, tx_write_hash, tx_write_hash || '|' || path, depth + 1
    FROM depends_on, candidates
    INNER JOIN transactions ON hash = tx_write_hash
    WHERE depends_on.tx_x = tx_access_hash
      AND depth <= {}
      AND (block_number > min_block_number
           OR block_number = min_block_number AND tx_index > min_tx_index) 
)
SELECT tx_a, tx_b, tx_a || '|' || path
FROM depends_on
INNER JOIN evaluation_candidates
ON tx_a = tx_write_hash AND tx_b = tx_access_hash
WHERE tx_b != tx_x
""").format(max_depth)
    with db._con.cursor() as cursor:
        return cursor.execute(sql).fetchall()


def create_limit_collisions_per_address(limit: int):
    def limit_collisions_per_address(db: DB):
        sql = f"""
    DELETE FROM collisions c
    USING (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY SUBSTR(key, 1, 42) ORDER BY RANDOM()) AS n
        FROM collisions
    ) grouped
    WHERE c.tx_write_hash = grouped.tx_write_hash
    AND c.tx_access_hash = grouped.tx_access_hash
    AND c.type = grouped.type
    AND c.key = grouped.key
    AND n > {limit}
    """
        with db._con.cursor() as cursor:
            cursor.execute("SELECT setseed(0)")
            cursor.execute(sql)  # type: ignore
        return db.remove_candidates_without_collision()

    return limit_collisions_per_address


def create_limit_collisions_per_code_hash(limit: int):
    def limit_collisions_per_code_hash(db: DB):
        sql = f"""
    DELETE FROM collisions c
    USING (
        SELECT tx_write_hash, tx_access_hash, type, key, ROW_NUMBER() OVER (PARTITION BY hash ORDER BY RANDOM()) AS n
        FROM collisions
        INNER JOIN skeletons ON SUBSTR(collisions.key, 1, 42) = skeletons.addr
    ) grouped
    WHERE c.tx_write_hash = grouped.tx_write_hash
    AND c.tx_access_hash = grouped.tx_access_hash
    AND c.type = grouped.type
    AND c.key = grouped.key
    AND n > {limit}
    """
        with db._con.cursor() as cursor:
            cursor.execute("SELECT setseed(0)")
            cursor.execute(sql)  # type: ignore
        return db.remove_candidates_without_collision()

    return limit_collisions_per_code_hash


def create_limit_collisions_per_code_family(limit=10):
    def limit_collisions_per_code_family(db: DB):
        sql = f"""
    DELETE FROM collisions c
    USING (
        SELECT tx_write_hash, tx_access_hash, type, key, ROW_NUMBER() OVER (PARTITION BY family ORDER BY RANDOM()) AS n
        FROM collisions
        INNER JOIN skeletons ON SUBSTR(collisions.key, 1, 42) = skeletons.addr
    ) grouped
    WHERE c.tx_write_hash = grouped.tx_write_hash
    AND c.tx_access_hash = grouped.tx_access_hash
    AND c.type = grouped.type
    AND c.key = grouped.key
    AND n > {limit}
    """
        with db._con.cursor() as cursor:
            cursor.execute("SELECT setseed(0)")
            cursor.execute(sql)  # type: ignore
        return db.remove_candidates_without_collision()

    return limit_collisions_per_code_family


def get_filters_except_duplicate_limits(
    window_size: int | None,
) -> list[tuple[str, Callable[[DB], int]]]:
    return [
        ("block_window", create_block_window_filter(window_size)),
        ("block_producers", filter_block_producers),
        ("nonces", filter_nonces),
        ("codes", filter_codes),
        ("indirect_dependencies_quick", filter_indirect_dependencies_quick),
        ("indirect_dependencies_recursive", filter_indirect_dependencies_recursive),
        ("same_sender", filter_same_sender),
        ("recipient_eth_transfer", filter_second_tx_ether_transfer),
    ]


def get_filters_up_to_indirect_dependencies(
    window_size: int | None,
) -> list[tuple[str, Callable[[DB], int]]]:
    return [
        ("block_window", create_block_window_filter(window_size)),
        ("block_producers", filter_block_producers),
        ("nonces", filter_nonces),
        ("codes", filter_codes),
    ]


def get_filters_duplicate_limits(limit: int) -> list[tuple[str, Callable[[DB], int]]]:
    return [
        ("limited_collisions_per_address", create_limit_collisions_per_address(limit)),
        (
            "limited_collisions_per_code_hash",
            create_limit_collisions_per_code_hash(limit),
        ),
        (
            "limited_collisions_per_code_family",
            create_limit_collisions_per_code_family(limit),
        ),
    ]
