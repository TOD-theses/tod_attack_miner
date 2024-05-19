"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser

from tod_attack_miner.analysis.analyzer import get_collisions
from tod_attack_miner.db.db import DB
from tod_attack_miner.fetcher.fetcher import BlockRange, fetch_block_range
from tod_attack_miner.rpc.rpc import RPC


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")
    parser.add_argument("--archive-node-provider", default="http://localhost:8124/eth")
    parser.add_argument("--from-block", default=19895498)
    parser.add_argument("--to-block", default=19895498 + 100 - 1)
    args = parser.parse_args()

    block_range = BlockRange(args.from_block, args.to_block)
    rpc = RPC(args.archive_node_provider)
    db = DB()

    fetch_block_range(rpc, db, block_range)
    collision_transactions = get_collisions(db)
    print(f"Found {len(collision_transactions)} collisions")
