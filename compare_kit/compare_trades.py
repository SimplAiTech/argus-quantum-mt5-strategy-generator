r"""Compares trades of the Python engine (python_trades/<name>.csv) with the trades of the MetaTrader 5 tester
(AQ_trades_<name>.csv written by the Expert Advisor into the terminal's Common\Files folder).
Usage:
  python compare_trades.py                      # all kit strategies; MT5 files are searched in %APPDATA%\MetaQuotes\Terminal\Common\Files
  python compare_trades.py AQ_kit_03 [mt5.csv]  # one strategy
A trade matches when the side is the same and the open times differ by at most --tol minutes (default 60 = one H1 bar)."""
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
FMT = "%Y.%m.%d %H:%M"


def load(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            rows.append((int(r["side"]), datetime.strptime(r["open_time"], FMT), datetime.strptime(r["close_time"], FMT),
                         float(r["open_price"]), float(r["close_price"]), float(r["profit"])))
    return sorted(rows, key=lambda x: x[1])


def compare(py, mt, tol_min):
    used = [False] * len(mt)
    matched = []
    j0 = 0
    for p in py:
        best, bd = None, None
        for j in range(j0, len(mt)):
            if (mt[j][1] - p[1]).total_seconds() / 60 > tol_min:
                break
            if used[j] or mt[j][0] != p[0]:
                continue
            d = abs((mt[j][1] - p[1]).total_seconds()) / 60
            if d <= tol_min and (bd is None or d < bd):
                best, bd = j, d
        if best is not None:
            used[best] = True
            matched.append((p, mt[best]))
        while j0 < len(mt) and (p[1] - mt[j0][1]).total_seconds() / 60 > tol_min:
            j0 += 1
    return matched, [m for m, u in zip(mt, used) if not u]


def report(name, py_csv, mt_csv, tol):
    py, mt = load(py_csv), load(mt_csv)
    matched, only_mt = compare(py, mt, tol)
    only_py = len(py) - len(matched)
    dop = [abs(a[3] - b[3]) for a, b in matched]
    dcl = [abs(a[4] - b[4]) for a, b in matched]
    same_close = sum(1 for a, b in matched if abs((a[2] - b[2]).total_seconds()) / 60 <= tol)
    print(f"{name}: python {len(py)} trades, MT5 {len(mt)}; matched {len(matched)} ({100 * len(matched) / max(len(py), 1):.1f}%), "
          f"only python {only_py}, only MT5 {len(only_mt)}")
    if matched:
        print(f"   open price: mean |diff| {sum(dop) / len(dop):.3f}, max {max(dop):.3f}; close price: mean {sum(dcl) / len(dcl):.3f}, "
              f"max {max(dcl):.3f}; same close time {same_close}/{len(matched)}")
    print(f"   net profit: python {sum(x[5] for x in py):.2f}, MT5 {sum(x[5] for x in mt):.2f}")
    return len(py), len(matched)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tol = 60
    if "--tol" in sys.argv:
        tol = int(sys.argv[sys.argv.index("--tol") + 1])
        args = [a for a in args if a != str(tol)]
    common = Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal" / "Common" / "Files"
    names = [args[0]] if args else sorted(p.stem for p in (HERE / "python_trades").glob("*.csv"))
    tot = ok = 0
    for n in names:
        mt = Path(args[1]) if len(args) > 1 else common / f"AQ_trades_{n}.csv"
        if not mt.exists():
            print(f"{n}: no MT5 file {mt}")
            continue
        a, b = report(n, HERE / "python_trades" / f"{n}.csv", mt, tol)
        tot += a
        ok += b
    if tot:
        print(f"TOTAL: matched {ok} of {tot} Python trades ({100 * ok / tot:.1f}%)")


if __name__ == "__main__":
    main()
