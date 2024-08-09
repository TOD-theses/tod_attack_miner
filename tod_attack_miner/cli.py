"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser, BooleanOptionalAction
import csv
from importlib.metadata import version
import json
from pathlib import Path

import psycopg

from tod_attack_miner.db.db import DB
from tod_attack_miner.db.filters import (
    get_filters_duplicate_limits,
    get_filters_except_duplicate_limits,
    get_filters_up_to_indirect_dependencies,
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
    parser.add_argument("--to-block", default=19895504)
    parser.add_argument(
        "--window-size",
        type=int,
        default=None,
        help="If passed, filter TOD candidates that are {window-size} or more blocks apart",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Delete data from previous runs before starting to mine",
    )
    parser.add_argument(
        "--evaluate-candidates-csv",
        type=Path,
        help="If passed, evaluate up to which filter candidates exist",
    )
    parser.add_argument(
        "--evaluation-result-csv",
        type=Path,
        default=Path("evaluations.csv"),
        help="Path, where evaluation results should be stored",
    )
    parser.add_argument(
        "--extract-indirect-dependencies",
        action="store_true",
        help="When evaluating candidates, stop before the indirect dependencies filter and output indirect dependency paths",
    )
    parser.add_argument("--postgres-user", type=str, default="postgres")
    parser.add_argument("--postgres-password", type=str, default="password")
    parser.add_argument("--postgres-host", type=str, default="localhost")
    parser.add_argument("--postgres-port", type=int, default=5432)
    parser.add_argument(
        "--quick-stats", action="store_true", help="Only output performant stats"
    )
    parser.add_argument(
        "--stats-only",
        action=BooleanOptionalAction,
        help="Skip data fetching and processing and only output stats",
    )
    args = parser.parse_args()
    evaluate_candidates_csv: Path | None = args.evaluate_candidates_csv
    evaluation_results_csv: Path = args.evaluation_result_csv
    extract_indirect_dependencies: bool = args.extract_indirect_dependencies

    with psycopg.connect(
        f"user={args.postgres_user} password={args.postgres_password} host={args.postgres_host} port={args.postgres_port}"
    ) as conn:
        miner = Miner(RPC(args.archive_node_provider), DB(conn))

        if args.stats_only:
            print(json.dumps(miner.get_stats(args.quick_stats)))
        elif evaluate_candidates_csv:
            if args.reset_db:
                miner.reset_db()
            with open(evaluate_candidates_csv, newline="") as csv_file, open(
                evaluation_results_csv, "w"
            ) as results_csv_file:
                csv_reader = csv.DictReader(csv_file)
                candidates = [(c["tx_a"], c["tx_b"]) for c in csv_reader]
                miner.fetch(int(args.from_block), int(args.to_block))
                miner.find_collisions()
                if extract_indirect_dependencies:
                    filters = get_filters_up_to_indirect_dependencies(25)
                    results = miner.get_indirect_dependencies(filters, candidates, 1)
                    csv_writer = csv.writer(results_csv_file)
                    csv_writer.writerow(("tx_a", "tx_b", "dependency_path"))
                    csv_writer.writerows(results)
                else:
                    filters = get_filters_except_duplicate_limits(
                        25
                    ) + get_filters_duplicate_limits(10)
                    results = miner.evaluate_candidates(filters, candidates)

                    csv_writer = csv.DictWriter(
                        results_csv_file, ["tx_a", "tx_b", "filtered_by"]
                    )
                    csv_writer.writeheader()
                    rows = [
                        {
                            "tx_a": c["tx_a"],
                            "tx_b": c["tx_b"],
                            "filtered_by": c["filter"] or "",
                        }
                        for c in results
                    ]
                    csv_writer.writerows(rows)
                print(f"Saved results to {evaluation_results_csv}")

        else:
            if args.reset_db:
                miner.reset_db()
            miner.fetch(int(args.from_block), int(args.to_block))
            miner.compute_skelcodes()
            miner.find_collisions()
            miner.filter_candidates(
                get_filters_except_duplicate_limits(25)
                + get_filters_duplicate_limits(10)
            )
            print(f"Found {miner.count_candidates()} candidates")
            print(json.dumps(miner.get_stats(args.quick_stats)))
