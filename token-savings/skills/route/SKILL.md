---
name: route
description: Plan a long, unattended task so quality does not drift. Interviews the user, writes acceptance criteria and a phase plan, then runs each phase as a subagent with a handoff file.
disable-model-invocation: true
---

# Route

Use at the start of a big task the user will leave running. Goal: fixed acceptance criteria, fresh context per phase, verification before moving on. The user is present now and will not be later, so settle everything now.

## 1. Small task? Stop.

If the task fits one short pass, say so in one line and just do it. Subagents reload static context, so splitting a small task costs more than it saves.

## 2. Look before asking

Read the repo for what you would otherwise ask: test, build and lint commands, CLAUDE.md, existing plans and shared progress files such as TODO.md. Never ask what you can read. If `.route/` already exists, resume from `plan.md` and the latest handoff instead of re-planning.

## 3. Interview

Ask one question at a time. Ask only what you could not find, and stop as soon as you can write the plan. Cover, in this order:

1. What does done look like? Prefer checkable statements over "works well". If part of the goal is exploratory and the user cannot state it up front, keep it as an open criterion (a direction, judged at the end) rather than forcing a rigid one.
2. How is each checkable statement verified? Prefer a command (tests, build). Otherwise name a reviewer subagent and its rubric. Open criteria are judged by the reviewer or by the user at the end, and phases may try options and record what was tried.
3. What stops the run? Failed verification twice, a missing decision, a scope boundary hit.
4. What must not change?

## 4. Shape the work

Work out the architecture from the task and the repo, then confirm it with the user, one question at a time.

1. **Sequential?** Which phases need the output of an earlier one? If there is a sequence, ask how context should pass between the steps: a handoff file (the default), an existing file or artifact the steps already share, or something else. Those phases run in order.
2. **Parallel?** Which pieces are independent: no shared files, no shared decisions? If there are any, ask where each piece writes its output and how the results are combined. Those pieces can run as concurrent subagents. Parallel runs multiply cost, so suggest this only when the pieces are large and truly independent.
3. **Several domains?** If the task is itself made of separate domains (for example finance, marketing and sales), give each domain its own agent with its own inputs, output and acceptance criteria. Sequence domains that feed each other, run the rest in parallel, then add a final phase that reconciles them.
4. **Extra domains?** Does the task touch areas the user did not mention, such as tests, docs, migrations, security or deployment? Suggest a specialist subagent for each domain, with its own acceptance criteria, and let the user accept, change or drop each one.

State the result as a short dependency list, for example: `A -> B`, `C and D in parallel -> E`.

## 5. Write the plan

Write `.route/plan.md`:

- **Goal**: two sentences.
- **Acceptance criteria**: checklist. Hard criteria say how they are verified. Open criteria are marked as such and say who judges them.
- **Out of scope**: what must not change.
- **Phases**: each with input, output, its check, its domain and what it depends on. Mark phases that run in parallel. A phase must be small enough to finish in one fresh context.
- **Stop conditions**: from the interview.

Show the plan and get one confirmation. Then run it.

## 6. Run each phase as a subagent

Each phase subagent:

1. Reads `.route/plan.md` and the previous `.route/handoff-N.md`. Nothing else is carried over.
2. Does only its phase.
3. Runs the phase check and the verification for the criteria it touches. If a check fails twice, stop and write the reason into the handoff. Do not continue on a broken base.
4. Writes `.route/handoff-N.md`: what was done, what changed, decisions and why, open issues, and the first step of the next phase.

The main session reads only the handoff, never the phase transcript. Parallel phases write separate handoffs, and the phase that depends on them reads all of them.

## 7. Finish

When all phases pass, check every acceptance criterion against the plan. Report each as met or not met with the evidence; judge open criteria and say who or what judged them. Do not report success on criteria you did not verify.
