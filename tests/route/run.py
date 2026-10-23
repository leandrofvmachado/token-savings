#!/usr/bin/env python3
"""Run /route cases headless and log token use.
usage: run.py CASE [CASE...]   results -> results/<case>/ and results/summary.tsv
Cases without "exec" stop after plan.md. "full" runs the whole plan. "resume" runs phases 1-2, then a fresh session resumes."""
import json, subprocess, sys, tempfile, pathlib, shutil
here = pathlib.Path(__file__).parent
cases = json.load(open(here / "cases.json"))
out = here / "results"; out.mkdir(exist_ok=True)
summary = out / "summary.tsv"
if not summary.exists():
    summary.write_text("case\tinput\toutput\tcache_read\tcache_create\tcost_usd\tturns\tsecs\tplan\n")
# Load only the route skill: --plugin-dir does not resolve the bundle's caveman/ponytail dependencies.
plugin = pathlib.Path(tempfile.mkdtemp(prefix="route-plugin-"))
(plugin / ".claude-plugin").mkdir()
(plugin / ".claude-plugin/plugin.json").write_text('{"name": "route-test", "version": "0.0.0", "description": "route skill under test"}')
(plugin / "skills").mkdir()
(plugin / "skills/route").symlink_to(here.parent.parent / "token-savings/skills/route")

def claude(prompt, cwd, budget):
    r = subprocess.run(["claude", "-p", prompt, "--plugin-dir", str(plugin), "--output-format", "json",
                        "--permission-mode", "acceptEdits", "--allowedTools", "Bash",
                        "--max-budget-usd", str(budget)], cwd=cwd, capture_output=True, text=True)
    try: return json.loads(r.stdout), r.stdout
    except Exception: return None, r.stdout or r.stderr

STOP = "Write .route/plan.md, show the plan, then STOP. Do not execute any phase."
FULL = "Write .route/plan.md and then run the whole plan per the skill, then give the final report. Do not ask me to confirm the plan."
PART = "Write .route/plan.md and run ONLY phases 1 and 2, then stop without a final report. This limit is a harness detail: do NOT write it into plan.md or any handoff."

for c in sys.argv[1:]:
    t = cases[c]; mode = t.get("exec")
    work = pathlib.Path(tempfile.mkdtemp(prefix=f"route-{c}-"))
    subprocess.run([str(here / "fixture.sh"), str(work)], check=True)
    tail = {"full": FULL, "resume": PART}.get(mode, STOP)
    prompt = (f"/route {t['task']}\n\nTEST HARNESS: I cannot answer interactively. When you would ask me a question, "
              f"use these answers instead and do not ask: {t['answers']}\n{tail}")
    d = out / c; d.mkdir(exist_ok=True)
    runs = [claude(prompt, work, 1.5 if not mode else 4)]
    if mode == "resume":
        runs.append(claude("/route", work, 3))   # fresh session, no task: should resume from .route/
    ok = [r for r, _ in runs if r]
    (d / "raw.json").write_text("\n".join(raw for _, raw in runs))
    (d / "answer.md").write_text("\n\n--- session ---\n\n".join(r.get("result", "") for r in ok))
    if ok:
        s = lambda k: sum(r["usage"].get(k, 0) for r in ok)
        row = [c, s("input_tokens"), s("output_tokens"), s("cache_read_input_tokens"), s("cache_creation_input_tokens"),
               round(sum(r["total_cost_usd"] for r in ok), 4), sum(r["num_turns"] for r in ok),
               round(sum(r["duration_ms"] for r in ok) / 1000), (work / ".route/plan.md").exists()]
    else:
        row = [c, "ERR", runs[0][1][:60], "", "", "", "", "", ""]
    if (work / ".route").exists(): shutil.copytree(work / ".route", d / "route", dirs_exist_ok=True)
    (d / "git-status.txt").write_text(subprocess.run(["git", "status", "--short"], cwd=work, capture_output=True, text=True).stdout)
    with open(summary, "a") as f: f.write("\t".join(map(str, row)) + "\n")
    print("\t".join(map(str, row)))
