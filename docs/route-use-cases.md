# /route use cases

Each case names a task, what `/route` should ask or decide, and the expected outcome. They double as manual test cases: run the task, compare with "Expected".

A "small" task here means one full feature in an existing system, no research needed. That is already too big for one pass, so it is routed, not just done.

## Routing

### 1. Single feature, sequential lifecycle
- **Task:** add a feature to an existing app, from idea to production: ideation, code, tests, PR, deploy.
- **Expected:** each step needs the previous one's output, so it is sequential. Asks how context passes (default: a handoff file). Plan: `ideation -> code -> test -> PR -> deploy`, one subagent per phase, each reading the previous `handoff-N.md`.

### 2. Independent parallel work
- **Task:** research the same question on three different sites and compare.
- **Expected:** the three lookups share no files or decisions. Asks where each writes its output and how results are combined. Plan: `A, B and C in parallel -> D (compare)`. Parallel is suggested because the pieces are large and independent.

### 3. Looks parallel, is not
- **Task:** update two services that both edit the same shared config file.
- **Expected:** finds the shared file, rejects parallel, runs them in sequence. States why.

### 4. Mixed shape
- **Task:** build an API endpoint and its client in parallel, then write integration tests that need both.
- **Expected:** plan `A and B in parallel -> C`. C reads both handoffs.

### 5. Separate domains with their own agents
- **Task:** prepare a quarterly plan covering finance, marketing and sales.
- **Expected:** treats each domain as its own agent with its own inputs, output and acceptance criteria, then a final phase that reconciles them. Domains that depend on each other (sales targets feed the finance budget) are sequenced, the rest run in parallel.
- **Skill gap:** step 4.3 only suggests extra specialists (tests, docs, security) around a task. It does not cover a task that is made of several domains.

## Verification

### 6. Reads the repo before asking
- **Task:** fix a failing test suite in a repo that has a test command and a `TODO.md` tracking progress.
- **Expected:** finds the test command and does not ask how to verify. Offers `TODO.md` as the context channel instead of a new handoff file. Asks only what the repo could not answer.

### 7. Not verifiable by command
- **Task:** rewrite a long document for a new audience.
- **Expected:** no test command exists, so it names a reviewer subagent and a rubric for it, and checks each phase against that rubric.

### 8. Exploratory goal
- **Task:** redesign a landing page; the user knows the direction but not the result.
- **Expected:** does not force every goal into a checkable statement. Splits criteria into hard ones (checkable: builds, loads, accessibility) and open ones (direction, judged by the reviewer or by the user at the end). Phases can try options and record what was tried.
- **Skill gap:** step 3.1 says "push for checkable statements". It needs a way to leave room for exploration.

## Stopping and finishing

### 9. Check fails twice
- **Task:** a four-phase task (for example case 1) where phase 2 (code) fails its own check twice.
- **Expected:** stops, writes the failure reason into `handoff-2.md`, and does not start phase 3.

### 10. Missing decision
- **Task:** a phase needs a choice the plan did not settle, for example which library to use.
- **Expected:** does not pick one silently. Hits a stop condition from the interview, stops, and records the open question in the handoff.

### 11. Criterion not met at the end
- **Task:** all phases finish but one hard criterion could not be verified.
- **Expected:** final report lists that criterion as not met, with the reason. It does not report overall success.

### 12. Interrupted run
- **Task:** the session ends after phase 2 of 4.
- **Expected:** a new session resumes from `plan.md` and the latest handoff, so all state is in files. The skill does not say this explicitly yet.
- **Later:** [ai-memory](https://github.com/akitaonrails/ai-memory) could hold the state instead of `.route/` files. For now handoffs stay in `.route/handoff-N.md`.

## Not covered yet
- Voting (several agents answer the same question, majority wins). Rare in practice.
- Cost cap or token budget as a stop condition.
- Re-planning when a phase shows the plan was wrong.
- Resume is now in the skill (step 2) and passes case 12, but only with a bare `/route`; resuming mid-phase after a crash is untested.

## Test run: planning stage (cases 1–8)
Harness: `tests/route/run.py CASE...` builds a scratch repo, runs `/route` headless with canned interview answers, stops after `plan.md`. Tokens/cost per case are in `tests/route/results/summary.tsv`. Eight cases cost about $1.19 total (about 17k output tokens, 0.12–0.32 USD each).

| Case | Plan shape | Result |
|---|---|---|
| 1 | 4 sequential phases (design, code, tests, PR+deploy) | pass |
| 2 | `A, B, C in parallel -> D -> E` | pass |
| 3 | sequential, shared `config/shared.json` named as the reason | pass |
| 4 | `1 -> 2 -> 3` sequential, expected endpoint and client in parallel | fail (arguably defensible: the client depends on the endpoint contract) |
| 5 | `A and B in parallel -> C -> D`, domains as separate agents | pass |
| 6 | sequential, test command taken from CLAUDE.md | pass |
| 7 | `A -> B` with reviewer rubric | pass |
| 8 | `A -> B -> C`; open vs hard criteria not yet checked | needs review |

Limits: canned answers mean the interview itself (one question at a time, not asking what the repo answers) is not tested. The fixture's deliberately failing test pushes cases 1, 3 and 4 toward planning around it. Cases 9–12 (execution) are not run yet.

## Test run: execution (cases 9–12)
Harness runs the full plan headless (`exec: full`), or phases 1–2 and then a fresh bare `/route` session (`exec: resume`).

| Case | What happened | Result |
|---|---|---|
| 9 | Phase 2 check failed twice (repo has no `tests/__init__.py`, and `test_empty` fails on purpose). Wrote `handoff-2.md` marked STOPPED with the reason and the decision needed. Phases 3–4 never started. | pass |
| 10 | Stopped in phase 1, before any code. `handoff-1.md` holds the open question (which caching approach) with options. | pass |
| 11 | Criterion (a) met, (b) staging returns 200 reported as not met, no overall success claimed. | pass |
| 12 | After phase 2, a fresh `/route` with no task read `plan.md` and the handoffs and ran phases 3 and 4. First attempt was invalid: the harness note "only phases 1–2" leaked into `plan.md`, so the harness now forbids that. | pass |

Cost: cases 9–11 about $0.12–0.15 each; case 12 about $0.71 because it spans two sessions. Whole suite (cases 1–12) about $2.3.
