import psycopg
import psycopg.sql
from tod_attack_miner.db.db import DB


def filter_same_sender(db: DB):
    sql = """
DELETE FROM candidates
USING transactions a, transactions b
WHERE a.sender = b.sender
    AND candidates.tx_access_hash = a.hash
    AND candidates.tx_write_hash = b.hash
"""
    with db._con.cursor() as cursor:
        cursor.execute(sql)
        deleted = cursor.rowcount
    db._con.commit()
    return deleted


def filter_second_tx_ether_transfer(db: DB):
    sql = """
DELETE FROM candidates
WHERE NOT EXISTS (
    SELECT 1
    FROM accesses
    WHERE candidates.tx_access_hash = accesses.tx_hash
      AND accesses.type = 'code'
)
"""
    with db._con.cursor() as cursor:
        cursor.execute(sql)
        deleted = cursor.rowcount
    db._con.commit()
    return deleted


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
    db._con.commit()
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
    return deleted
