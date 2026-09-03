#!/usr/bin/env python3
"""results.tsv 를 변형별로 집계한다.  사용법: python3 summarize.py results.tsv"""
import re, sys, collections
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
agg = collections.defaultdict(lambda: {"n": 0, "score": 0, "turns": [], "cache_w": [], "cache_r": [], "tokens": []})
for label, line in rows:
    tool, var, _ = label.rsplit("-", 2)
    a = agg[(tool, var)]; a["n"] += 1
    a["score"] += int(re.search(r"score (\d)/5", line).group(1))
    for k in ("turns", "cache_w", "cache_r", "tokens"):
        m = re.search(rf"{k}=([\d,]+)", line)
        if m: a[k].append(int(m.group(1).replace(",", "")))
mean = lambda xs: f"{sum(xs)/len(xs):,.0f}" if xs else "-"
print(f"{'tool':7} {'var':4} {'score':>7} {'turns':>6} {'cache_w':>8} {'cache_r':>9} {'tokens':>8}")
for (tool, var), a in sorted(agg.items()):
    print(f"{tool:7} {var:4} {a['score']:>3}/{a['n']*5:<3} {mean(a['turns']):>6} {mean(a['cache_w']):>8} {mean(a['cache_r']):>9} {mean(a['tokens']):>8}")
