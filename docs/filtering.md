# Filtering

We filter the potential transaction pairs with following goals:

1. Remove potential attacks, that do not make sense (eg self-attacks)
2. Remove duplicated attacks, where the analysis outcome would (likely) be the same

## Non-attack filtering

### Self-attack

If both transactions are sent by the same actor (A_from == B_from).

### Ether-transfer

If the 2nd transaction is only an Ether transfer (B_call_stack has length 0 or smth like that).

We allow, that the first transaction is just an Ether transfer, as it could influence the second transaction if it accesses this balance (directly/indirectly).

### ...

## Deduplication

Some ideas:

- only trace some attacks per contract
- only trace some attacks per function call
- only trace some attacks per source-to-sink contract group
- same as above, but rather look at contract/function skeletons