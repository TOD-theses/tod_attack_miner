"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser
from typing import Any

from tod_attack_miner.db.db import DB
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC
import matplotlib.pyplot as plt


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")
    parser.add_argument("--archive-node-provider", default="http://localhost:8124/eth")
    parser.add_argument("--from-block", default=19895498)
    parser.add_argument("--to-block", default=19895498 + 100 - 1)
    parser.add_argument("--database-path", default="tod_attacks.db")
    args = parser.parse_args()

    block_range = BlockRange(args.from_block, args.to_block)
    rpc = RPC(args.archive_node_provider)
    db = DB(args.database_path)

    if False:
        fetch_block_range(rpc, db, block_range)

    print(f"Stored transactions: {db.count_prestates()}")
    storage_collisions = db.get_storage_collisions_tx_pairs()
    print(f"Tx pairs with storage collisions: {len(storage_collisions)}")
    print(storage_collisions[:10])
    unique_transaction_hashes = set(collision[0] for collision in storage_collisions)
    print(
        f"Unique transactions with storage collisions: {len(unique_transaction_hashes)}"
    )

    plot(db.get_storage_collisions_contract_addresses())


def plot(values: list[tuple[Any, Any]]):
    fig, ax = plt.subplots()
    counts = list(count for _, count in values)
    ax.pie(counts)
    plt.show()
