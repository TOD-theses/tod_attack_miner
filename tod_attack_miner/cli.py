"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from tod_attack_miner.miner.miner import Miner
import matplotlib.pyplot as plt


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")
    parser.add_argument("--archive-node-provider", default="http://localhost:8124/eth")
    parser.add_argument("--from-block", default=19895498)
    parser.add_argument("--to-block", default=19895498 + 100 - 1)
    parser.add_argument("--database-path", type=Path, default="tod_attacks.db")
    args = parser.parse_args()

    miner = Miner(args.archive_node_provider, args.database_path)

    miner.fetch(int(args.from_block), int(args.to_block))

    db = miner.db
    print(f"Stored transactions: {db.count_prestates()}")
    storage_collisions = db.get_storage_collisions_tx_pairs()
    print(f"Tx pairs with storage collisions: {len(storage_collisions)}")
    print("first 10 collisions: ", storage_collisions[:10])
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
