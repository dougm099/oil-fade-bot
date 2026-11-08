# Oil-Fade Bot

An intraday mean-reversion strategy that shorts crude-oil momentum spikes. When
USO spikes intraday on headline-driven buying, the bot fades the move: short
the spike, stop out if it keeps running, and always finish the day flat.

**Paper trading only.** There is no live-trading path in this codebase — the
broker layer hard-refuses any live configuration.

## Strategy (Model D2, frozen and preregistered)

- **Instrument:** USO only.
- **Arm:** only when the regular-session opening gap vs. prior close is ≤ **+0.5%**.
- **Entry:** short the first 5-minute close **≥ +1.5% above the session open**.
- **Stop:** **0.75%** above entry.
- **Exit:** cover at/around **15:55 ET** if the stop wasn't hit.
- **Risk:** 1% of equity per trade (~133% notional short on $100k — margin required).
- **Constraints:** max one trade per day, always flat overnight.

See [docs/prereg.md](docs/prereg.md) for the preregistration record.

## Layout

```
bot/oil_fade/strategy.py   pure strategy logic (signals only, no I/O)
bot/oil_fade/sim.py        event-driven backtest simulator with costs
bot/oil_fade/runner.py     market-hours Alpaca paper runner
bot/brokers/alpaca.py      Alpaca paper-API broker (refuses live configs)
scripts/run_oil_fade_bot.py   entrypoint: dry-run default, --live-paper to trade
scripts/sweep_oil_fade.py     parameter sweep (train/test split)
scripts/backtest_oil_fade.py  single-config backtest
scripts/analyze_fade_features.py  exploratory feature analysis
tests/                      pytest suite (11 tests)
```

The same `OilFadeStrategy` class drives both the simulator and the live runner,
so backtest results describe the paper bot exactly.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Alpaca PAPER keys
```

Run the test suite:

```bash
pytest -q
```

Dry run (signals logged, **no orders placed**):

```bash
python scripts/run_oil_fade_bot.py --once
```

Paper trading (real orders against the **Alpaca paper sandbox** only):

```bash
python scripts/run_oil_fade_bot.py --once --live-paper
```

For scheduled polling (e.g. every 5 minutes), use `--once --live-paper` and stay
silent unless a new `signal`/`fill`/`skip` row lands in
`results/datasets/oil_fade_paper.csv` or the script errors.

## Safety

- `Config.assert_paper_safe()` + runner refusal: any `LIVE_TRADING_ENABLED=true`
  config is rejected at startup.
- Kill-switch file (creates, flattens USO, stops).
- USO shortability check before entries.
- Daily-loss halt (3% of day-start equity).
- Broker reconciliation and persistent state across restarts.

## Evidence (from the sweep, honest caveats included)

- 80-configuration sweep over 60 USO trading days (40 train / 20 test).
- Frozen D2 was itself the #1 in-sample config and held on the test split
  (75% → 80% win rate, +44 → +71 bps/trade).
- Only 13 D2 trades; the gap filter was discovered on the same broad dataset,
  so in-sample numbers are selection-inflated; the test window includes an
  Iran-war volatility window; tuning found no justified improvement, so the
  parameters shipped frozen.
- Equity sim at corrected leveraged sizing: $100k → ~$108.9k (+8.9%),
  max drawdown ~−1.0%.

## License

MIT — see [LICENSE](LICENSE).
