# Plot & Prove

A build loop for coding agents, built on one rule:

> **Nobody marks their own homework.**

It exists because agents report work as finished when it isn't. Not by lying — by
running a harness, watching it go green, and calling that proof. This makes that
failure structurally hard.

---

## The two things you can use

**Start with the pair.** Two files, no setup, works with any coding agent.

| | What it does |
|---|---|
| **`/buildplan`** | Turns a rough ask into a spec a fresh session can execute blind — numbered requirements with a count, an output contract with no holes, a scope fence, and acceptance checks written **before** the build |
| **`/proofcheck`** | Audits any "it's done" claim. Classifies it HARNESS-PROVEN or LIVE-PROVEN, hunts the four ways a harness lies, and names the one real run that would settle it |

**Then the loop**, if you want the full thing: an audit squad, a planner, a gate,
branch builders in isolated worktrees, an independent prover, an integrator that
owns the seams, and an adopt station.

## Why three separate chats

The plan, the build and the audit each run in a **new session**. Only the
document travels.

That walk is the point. A session that plans something already knows what it
meant, so it cannot tell whether the spec was any good — it fills the gaps from
memory. A fresh session reading only the paperwork **is a test of the paperwork.**

## Install

Drop the files into your agent's skills and agents directories. For Claude Code:

```bash
git clone https://github.com/zaneburstin-debug/plot-and-prove
cd plot-and-prove
cp -r skills/*    ~/.claude/skills/
cp -r agents/*    ~/.claude/agents/
cp -r doctrine    ~/.claude/
```

**Requirements:** `git` (builders work in worktrees) and a coding agent that
supports skills and subagents. Nothing else. No API keys, no services, no
database.

## Quickstart

```bash
# once per repo — inspects it, runs every command it's about to record, writes .buildloop.md
/buildloop-init

# chat 1 — produces a build doc
/buildloop-plan  "what you want built"

# chat 2 (NEW CHAT) — executes it
/buildloop-build <path to the doc>

# chat 3 (NEW CHAT) — audits the result
/proofcheck <the build report>
```

Or just use the pair, anywhere, with no config at all:

```bash
/buildplan   "spec this out"
/proofcheck  "is this actually done?"
```

## The rules it enforces

1. **You may never write "done."** You write HARNESS-PROVEN (tests passed) or
   LIVE-PROVEN (the real thing ran, once, end to end).
2. **The requirement count is a checksum.** A truncated spec cannot survive it.
   One arrived cut at 512 characters, ending on a complete sentence so it looked
   whole; the build invented its own field names and validated its own invention.
3. **Validate the ruler before you measure.** If a check compares checksums, first
   prove the comparison is stable by running it twice unchanged. Otherwise
   ordinary nondeterminism is indistinguishable from the defect you're hunting.
4. **Prove which tree you executed.** An installed binary imports its own copy and
   will pass every check while containing none of your build.
5. **Everything new ships behind an off switch.**
6. **Anything irreversible stops and waits for a human.**
7. **Never relay a subagent's claim as verified.** Re-derive it, or attribute it
   and mark it unverified.
8. **The line ends at ADOPTED, not at built.** A ledger row tracks it, and it
   starts at `NO — owed`.

## What is actually proven, and what isn't

Written to this project's own standard, because a README that overclaims would be
the funniest possible way to fail.

**LIVE-PROVEN**

- `/buildplan` produced a working 15-requirement spec for a repo it had never
  seen, and caught that the problem description it was given was wrong.
- `/proofcheck` was given a build report containing three known errors, held
  back from it. It found all three, plus three more that a previous audit had
  missed. Zero false accusations.
- The full build station ran a 15-requirement build end to end: 15/15 landed,
  7 acceptance checks LIVE-PROVEN through a real installed binary.
- The integrator caught a bug at a seam that neither branch owner could see.
- `/buildloop-init` ran end to end and immediately found that 3 of 4 CI commands
  did not exist on the machine, and that the live run was executing a different
  source tree than the one under test.

- **`/proofcheck` passes its own eval suite.** Five cases: four with a real
  planted lie, one honest report that must come back clean. **4/4 caught, 0 false
  positives, 0 cross-attributions.** Three cases exceeded the answer key. See
  [`evals/`](evals/) — `./run.sh <case>` stages one in isolation.

**NOT PROVEN**

- **Evals cover `/proofcheck` only.** `/buildplan`, the gate, the builder, the
  integrator and the adopt station have no regression tests. Change those and you
  will not know if they got worse. This is now the biggest gap.
- **Python only.** Never run against another language's toolchain.
- **The adopt station has never produced a `YES` row.** It is new.
- **The vocabulary sheet is new and lightly used.** It has been generated for one
  repo and no build has yet been gated against it.
- **Small-N.** Two full loop runs, one repo, one eval sweep.

If you use it and it fails somewhere, that's a useful bug report and the project
would rather have it than a star.

## When not to use this

It costs several agents and roughly half an hour per build. That is absurd for a
typo and cheap for thirty requirements. **Use it for long builds** — work too big
to hold in one session, where the failure mode is finishing something nobody ever
switched on.

## Licence

MIT.
