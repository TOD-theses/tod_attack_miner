# TOD attack miner

[![codecov](https://codecov.io/gh/TOD-theses/tod_attack_miner/branch/main/graph/badge.svg?token=tod_attack_miner_token_here)](https://codecov.io/gh/TOD-theses/tod_attack_miner)
[![CI](https://github.com/TOD-theses/tod_attack_miner/actions/workflows/main.yml/badge.svg)](https://github.com/TOD-theses/tod_attack_miner/actions/workflows/main.yml)

See https://tod-theses.github.io/tod_attack_miner/.

# TODO

Check if the prestate tracer includes non-initialized state (eg if I load the balance of a non-existing account, or an SLOAD to a random key returning 0).
If this is the case, what does this imply for the TOD results? If $T_A$ sets some value and $T_B$ accesses it, it will be included if it is non-null?
(And what would this imply for the revm-replayer?)

## Install

See [CONTRIBUTING.md](CONTRIBUTING.md) for installation instructions.

## Usage

After installing it, you can run it as following:

```bash
$ python -m tod_attack_miner --help
#or
$ tod_attack_miner --help
```