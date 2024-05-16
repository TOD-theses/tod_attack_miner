"""CLI interface for tod_attack_miner project."""

from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="Mine TOD transactions in Ethereum")

    args = parser.parse_args()
    print(args)
