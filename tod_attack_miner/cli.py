"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser, BooleanOptionalAction
from importlib.metadata import version
import json

import psycopg

from tod_attack_miner.db.db import DB
from tod_attack_miner.db.filters import (
    get_filters_duplicate_limits,
    get_filters_except_duplicate_limits,
)
from tod_attack_miner.miner.miner import Miner

from tod_attack_miner.rpc.rpc import RPC


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + version("tod_attack_miner")
    )
    parser.add_argument("--archive-node-provider", default="http://localhost:8124/eth")
    parser.add_argument("--from-block", default=19895500)
    parser.add_argument("--to-block", default=19895500 + 100 - 1)
    parser.add_argument(
        "--window-size",
        type=int,
        default=None,
        help="If passed, filter TOD candidates that are {window-size} or more blocks apart",
    )
    parser.add_argument("--postgres-user", type=str, default="postgres")
    parser.add_argument("--postgres-password", type=str, default="password")
    parser.add_argument("--postgres-host", type=str, default="localhost")
    parser.add_argument("--postgres-port", type=int, default=5432)
    parser.add_argument(
        "--stats-only",
        action=BooleanOptionalAction,
        help="Skip data fetching and processing and only output stats",
    )
    args = parser.parse_args()

    with psycopg.connect(
        f"user={args.postgres_user} password={args.postgres_password} host={args.postgres_host} port={args.postgres_port}"
    ) as conn:
        miner = Miner(RPC(args.archive_node_provider), DB(conn))

        if args.stats_only:
            print(json.dumps(miner.get_stats()))
        else:
            miner.fetch(int(args.from_block), int(args.to_block))
            miner.compute_skelcodes()
            miner.find_collisions()
            miner.filter_candidates(
                get_filters_except_duplicate_limits(25)
                + get_filters_duplicate_limits(10)
            )
            print(f"Found {miner.count_candidates()} candidates")
            print(json.dumps(miner.get_stats()))
