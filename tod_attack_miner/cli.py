"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser
from importlib.metadata import version
from typing import Any

import psycopg

from tod_attack_miner.db.db import DB
from tod_attack_miner.miner.miner import Miner
import matplotlib.pyplot as plt

from tod_attack_miner.rpc.rpc import RPC


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + version("tod_attack_miner")
    )
    parser.add_argument("--archive-node-provider", default="http://localhost:8124/eth")
    parser.add_argument("--from-block", default=19895500)
    parser.add_argument("--to-block", default=19895500 + 100 - 1)
    parser.add_argument("--postgres-user", type=str, default="postgres")
    parser.add_argument("--postgres-password", type=str, default="password")
    parser.add_argument("--postgres-host", type=str, default="localhost")
    parser.add_argument("--postgres-port", type=int, default=5432)
    args = parser.parse_args()

    with psycopg.connect(
        f"user={args.postgres_user} password={args.postgres_password} host={args.postgres_host} port={args.postgres_port}"
    ) as conn:
        miner = Miner(RPC(args.archive_node_provider), DB(conn))

        miner.fetch(int(args.from_block), int(args.to_block))
        miner.find_conflicts()
        print(miner.get_stats())

        # plot(db.get_storage_collisions_contract_addresses())


def plot(values: list[tuple[Any, Any]]):
    fig, ax = plt.subplots()
    counts = list(count for _, count in values)
    ax.pie(counts)
    plt.show()
