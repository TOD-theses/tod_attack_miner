from collections import defaultdict
from tod_attack_miner.db.db import DB


def get_collisions(db: DB) -> set[frozenset[str]]:
    # maps state key to set of (block_num, tx_hash, accessed value)
    stats: dict[tuple[str, ...], list[tuple[int, str, str]]] = defaultdict(list)

    for block_number, prestate in db.get_all_prestates():
        tx_hash = prestate["txHash"]
        for addr, account_state in prestate["result"].items():
            if (code := account_state.get("code")) is not None:
                stats[(addr, "code")].append((block_number, tx_hash, code))
            if (balance := account_state.get("balance")) is not None:
                stats[(addr, "balance")].append((block_number, tx_hash, balance))
            if (nonce := account_state.get("nonce")) is not None:
                stats[(addr, "nonce")].append((block_number, tx_hash, str(nonce)))
            if (storage := account_state.get("storage")) is not None:
                for storage_key, storage_val in storage.items():
                    stats[(addr, "storage", storage_key)].append(
                        (block_number, tx_hash, storage_val)
                    )

    tx_hash_to_from: dict[str, str] = {}
    for block in db.get_all_blocks():
        for tx in block["transactions"]:
            tx_hash_to_from[tx["hash"]] = tx["from"]

    collisions: set[frozenset[str]] = set()
    all_transactions = set()

    for key, entries in stats.items():
        tx_hashes = frozenset(tx_hash for _, tx_hash, _ in entries)
        unique_froms = set(tx_hash_to_from[tx_hash] for tx_hash in tx_hashes)
        unique_values = set(value for _, _, value in entries)
        all_transactions.update(tx_hashes)
        if len(unique_values) > 1 and len(unique_froms) > 1 and key[1] == "storage":
            collisions.add(tx_hashes)

    return collisions
