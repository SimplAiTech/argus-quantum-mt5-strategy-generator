# Comparison kit: Argus Quantum engine vs the MetaTrader 5 Strategy Tester

This folder is the proof of accuracy, and a tool you can repeat on your own terminal.

Ten example strategies built by the Argus Quantum generator (market, stop, limit and reverse entries), the Expert Advisors the
program exports for them, the trades the Python engine makes, and the trades the MetaTrader 5 tester made (journals written by the
Expert Advisors themselves). `report.html` shows the result.

## Result (XAUUSD H1, 2024-01-01 to 2025-12-31, "1 minute OHLC", 0.1 lot)

| Measure | Result |
|---|---|
| Trades matched (same direction, open time within one H1 bar) | 885 of 885 (100 % for every one of the ten) |
| Profit, engine vs tester | within 3.3 USD on every strategy (largest: AQ_kit_02 1243.24 vs 1239.94) |
| Swap, engine vs tester | equal to 0.02 USD per strategy |
| Commission (separate column) | equal in total for all ten |

Same-trade identity is a statement about these ten strategies, this symbol and this broker's history. Different strategies can
use blocks that were not part of this set; verify your own strategy with the procedure below.

## What the engine does to match the tester
* Trades inside one bar follow the broker's 1-minute bars (open, then low/high in the order the tester uses, then close) instead of a guess
  from the candle shape.
* The spread of each 1-minute bar of the broker's history, not a fixed spread.
* Swap from the symbol's own rates (`symbol_info`): charged at the end of the server day, Wednesday x3, modes "points", "deposit
  currency" and "interest %" (other modes are reported in the task log and not charged).
* The daily trade break some brokers have (orders refused for the first minutes of the day while quotes already run): actions wait for
  the first tick after it, exactly as the exported Expert Advisor does. Set it per symbol in Data Hub ("Trade break").
* A position still open when the test ends is not a closed trade (as in the tester's deal list).

Without 1-minute data the engine works on the bars of the chosen timeframe, as before; the task log says which mode was used.

## Files
* `mq5/`, `ex5/` - the ten Expert Advisors (`InpLogTrades=true`: each writes its closed trades to `Common\Files\AQ_trades_<name>.csv`).
* `strategies/` - the strategy files in the Argus Quantum schema (read them with any XML viewer).
* `python_trades/` - trades of the engine; `mt5_t2/` - trades of the tester; `report.html` - the report;
  `run_info.json` - how the ten were chosen.
* `compare_trades.py` - matches the two sides.

## Repeat it in your own MetaTrader 5
1. Import XAUUSD in Data Hub (1-minute data are needed for the same-bar accuracy), or use your own symbol and set its trade break.
2. Copy `ex5\*.ex5` to `MQL5\Experts\AQ_kit\` (or compile `mq5\*.mq5` in MetaEditor).
3. Strategy Tester: symbol XAUUSD, H1, 2024.01.01 - 2025.12.31, model "1 minute OHLC", deposit 10000 USD, input parameters unchanged.
   The tester takes the spread of each minute from your broker's history, so a different broker gives a different (but equally
   reproducible) result.
4. Regenerate the engine side for your data (needs the 1-minute XAUUSD file and its spread file that Data Hub writes into `data/`;
   the shipped `python_trades/` were made with the author's broker history, which is not part of the package):
   `python tools/run_py_kit.py compare_kit/python_trades 5`, then
   `python compare_kit/compare_trades.py` (expects the journals in the terminal's `Common\Files`).

Not a forecast: these are back-tests on historical data.
