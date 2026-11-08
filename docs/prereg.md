# Preregistration: oil spike-fade forward test

**Registered:** 2026-09-28. **Analyst:** Doofy. **Status:** collecting.

## Background

Backtest battery (`results/oil_fade_backtest.md`, 60 days, 2026-07-06 → 2026-09-28):
fading small USO spikes (≥1.0%) and blind time-based fading both lose money.
Fading ≥1.5% spikes with a 0.75% stop (Model D) made +286 bps, but t-stat 0.59
(n=26) — not significant — and 100%+ of the profit came from 3 trades in the
Sep 21–28 Iran-war window. Thresholds were chosen post-hoc: the backtest is
hypothesis generation only.

## Hypotheses (frozen before forward data)

- **H1:** Model D has positive mean per-trade P&L on days with `tension_max ≥ 2`
  (geopolitical regime).
- **H0-null:** Model D has zero/negative mean per-trade P&L on days with
  `tension_max < 2` (no edge outside the war regime).

## Model D (frozen — no parameter changes during the window)

Short USO at the first 5m close ≥ +1.5% above the regular-session open;
stop-loss at +0.75% above entry (filled at stop); otherwise cover at the
session close. Costs 4 bps round trip. One trade per day max. Paper only.

## Test plan

- **Data:** `results/datasets/oil_spike_study.csv`, appended daily by cron
  `oil-spike-study` (~13:35 PT weekdays). Columns `d_triggered`, `d_pnl_bps`,
  `tension_max` are the test inputs.
- **Trigger to evaluate:** after **20 qualifying forward trades**
  (`d_triggered = 1`, dated after 2026-09-28).
- **Test:** one-sided t-test of mean `d_pnl_bps > 0` on the tension≥2 subset,
  α = 0.10 (exploratory sample size). Report the tension<2 subset descriptively.
- **Decision rule:**
  - H1 confirmed (p < 0.10, mean > 0) AND H0-null holds (no edge off-regime)
    → conditional edge confirmed; may propose a sized paper-trading phase.
  - Otherwise → retire the theory, keep the negative result on file.
- **Guardrails:** no threshold/stop/cost changes mid-window; no live trading
  regardless of outcome without the user's separate explicit authorization;
  the Sep 28 backtest rows are excluded from the forward sample.

## H2 (added 2026-09-28, from exploratory feature analysis — in-sample, must prove forward)

Exploratory analysis of the 60-day backtest's 26 Model D trades found the
P&L concentrated in the overnight-gap feature (known at the open, no lookahead):

- gap-down/flat days (gap ≤ +0.5%): 13 trades, mean **+58.0 bps**, 77% win rate, +753.9 bps total
- gap-up days (gap > +0.5%): 13 trades, mean **−36.0 bps**, −467.8 bps total

Mechanism guess: a +1.5% intraday rip after a gap-down open is a failed rally
(mean-reverts); the same rip after a gap-up open is momentum continuation
(don't fade it). Corroborating: spike-size corr with P&L was −0.55 (the
biggest spikes were the worst fades), VIX-change corr −0.46.

**Model D2 (frozen for the forward window):** identical to Model D, except
**no trade when the overnight gap (open vs prior close) exceeds +0.5%**.
Logged daily as `d2_triggered` / `d2_pnl_bps` in the same CSV.

- **Test:** same 20-trade evaluation; one-sided t-test of mean `d2_pnl_bps > 0`
  over ALL D2 forward trades (no tension subset — the gap filter is the regime),
  α = 0.10. Report D-vs-D2 divergence descriptively.
- **Status:** H2 is a hypothesis, not a finding. The in-sample gap split was
  found by looking at this data; forward trades decide.

## Prior (for the record)

Backtest point estimates: D overall mean +11.0 bps/trade (t=0.59);
D2 (gap-filtered) mean +58.0 bps/trade in-sample (n=13, t≈1.5 — inflated by
selection, do not trust); war-window subset (n=3) +102 bps/trade.
The forward test exists because n=3 proves nothing.
