# TOD attack miner

[![codecov](https://codecov.io/gh/TOD-theses/tod_attack_miner/branch/main/graph/badge.svg?token=tod_attack_miner_token_here)](https://codecov.io/gh/TOD-theses/tod_attack_miner)
[![CI](https://github.com/TOD-theses/tod_attack_miner/actions/workflows/main.yml/badge.svg)](https://github.com/TOD-theses/tod_attack_miner/actions/workflows/main.yml)

See https://tod-theses.github.io/tod_attack_miner/.

# TODO

Staged filtering:
- stats mode: for all collisions, each stage checks this collision and potentially stores a label (eg SAME_SENDER)
- run mode: for all remaining, unlabelled, collisions, each stage checks this collision and potentially stores a label

The filter implementations can be the same for both modes, only the execution differs. The run mode will be more performant. The stats mode could be nice for analysis and statistics in the paper.

## Install

See [CONTRIBUTING.md](CONTRIBUTING.md) for installation instructions.

We also use a postgres database, which you can run with eg `docker run --rm --name miner_postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres`

## Usage

After installing and creating the database, you can run it as following:

```bash
$ python -m tod_attack_miner --help
#or
$ tod_attack_miner --help
```