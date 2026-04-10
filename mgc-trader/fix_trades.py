"""One-time script to close today's open dashboard trades after EOD flatten."""
import json

trades_file = r'C:\Users\adamh\.openclaw\workspace\mgc-trader\data\trades_20260223.jsonl'
entries = []
with open(trades_file) as f:
    for line in f:
        rec = json.loads(line.strip())
        if rec['event'] == 'entry':
            entries.append(rec)

# All positions were flattened at EOD ~13:47 PST, last fill ~5248.6
flatten_price = 5248.6
point_value = 10.0

with open(trades_file, 'a') as f:
    for e in entries:
        action = e['action']
        ep = e['entry_price']
        contracts = e['contracts']
        if action == 'BUY':
            pnl_per = (flatten_price - ep) * point_value
        else:
            pnl_per = (ep - flatten_price) * point_value
        total_pnl = pnl_per * contracts
        exit_rec = {
            'event': 'exit',
            'ts': '2026-02-23T13:47:09',
            'trade_id': e['trade_id'],
            'strategy': e['strategy'],
            'action': action,
            'contracts': contracts,
            'entry_price': ep,
            'exit_price': flatten_price,
            'pnl_per_contract': round(pnl_per, 2),
            'total_pnl': round(total_pnl, 2),
            'exit_reason': 'eod_flatten',
        }
        f.write(json.dumps(exit_rec) + '\n')
        tid = e['trade_id']
        print(f"{tid}: {action} {contracts}x @ {ep} -> {flatten_price} = ${total_pnl:.2f}")

print("Done — all trades closed on dashboard")
