# Plot & Prove

A build loop for coding agents, built on one rule:

> **Nobody marks their own homework.**

---

## The problem it solves

Your agent says it's done. The tests are green. The report is confident.

And it isn't done — because the tests replaced the real thing with a stub, or
called the function directly and skipped the broken part, or ran against a copy
of the code that doesn't contain the change. Nobody lied. A harness went green
and everyone called that proof.

Plot & Prove makes that structurally hard. It splits building from judging, puts
them in different sessions that cannot see each other, and refuses to let anyone
write the word "done."

## What you need

| | |
|---|---|
| **git** | builders work in isolated worktrees, so nothing touches your checkout |
| **a coding agent with skills + subagents** | built and tested on Claude Code |
| **that's it** | no API keys, no services, no database, no accounts, no network |

Optional: if you have [graphify](https://github.com/Graphify-Labs/graphify), the
audit stations use it to trace what reaches what. If you don't, they fall back to
grep and say so. It is an accelerant, never a dependency.

## Install

```bash
git clone https://github.com/zaneburstin-debug/plot-and-prove
cd plot-and-prove
cp -r skills/*    ~/.claude/skills/
cp -r agents/*    ~/.claude/agents/
cp -r doctrine    ~/.claude/
```

## How it works

Think of it as a factory with **three buildings**. You walk between them, and
**only the paperwork travels** — never the person, never their memory.

That walk is the whole design. A session that planned something already knows
what it meant, so it can't tell whether the spec was any good; it fills the gaps
from memory without noticing. **A fresh session reading only the paperwork is a
test of the paperwork.**

### Building 1 — the drawing office · `/buildloop-plan`

Nobody writes code here.

```
① SURVEY      three agents at once —
                the mapper    : where the code lives, what actually runs
                the spy       : what is running RIGHT NOW, not what the notes claim
                the detective : are these 4 problems, or 1 problem in 4 costumes?
              ⛔ stop if there is no real problem. Nothing to build.

② ARCHITECT   writes the order sheet. First asks "who does this job for a
              living?" then designs in that idiom.

②ᵇ GATE       reads it BEFORE anything is built. Can only reject you for
              breaking a written rule, never a preference. 3 rounds, then stop.
```

Out comes **the order sheet**: numbered requirements *with a count at the top*.
The count is a checksum — if a page falls off in transit, the next building
catches it.

### Building 2 — the shop floor · `/buildloop-build`

```
⓿ FLOOR CHECK  is the workshop clean? is the order complete, 1..N?
❶ READ IT BACK the foreman restates the whole order before touching a tool.
               ← YOUR catch point. Watch for a missing number (truncation),
                 a word you never wrote (invention), or files written before
                 the restatement (the gate didn't run — stop it).
❷ WORK ORDER   what's built first; what can run in parallel (only if the
               file sets don't overlap).
❸ BUILDERS     each in its own private worktree. They never check their own work.
❹ PROVER       gets the spec and the result — NOT the builders' reasoning.
               Re-runs every check itself.
❺ INTEGRATOR   looks only where two builders' work meets. That's where the bugs
               nobody can see live.
❻ LIVE RUN     run the real thing once, for real. Not a test rig.
❼ REPORT       including what failed. One line appended to the ledger.
❽ ADOPT        switch it on, use it as a stranger would, record it.
```

Every station writes its state to disk, so a build that spans days can be
resumed by someone who wasn't there.

### Building 3 — quality control · `/proofcheck`

```
0  read this project's own rulebook. What counts as "really tested" HERE?
1  force the claim into one box:
     HARNESS-PROVEN — the tests passed
     LIVE-PROVEN    — the real thing ran, end to end, once
   can't tell which? Then it's NEITHER. Go find out.
2  hunt the four lies:
     a fake part standing in for a real one
     a test that skipped the join it claims to fix
     IT RAN THE WRONG COPY of the code       ← the most common by far
     a canned answer from an outside service
3  for every check: "this goes RED if ___". No answer = a demo, not a proof.
4  did it PASS, or did something break and get waved through?
5  whole system, or one stage?
6  is the switch really on INSIDE the running process, or only in the file?
```

Out comes one word: **LIVE-PROVEN**, **HARNESS-PROVEN**, or **NOT PROVEN** — plus
the one real run that would settle it.

## Quickstart

```bash
# once per repo — inspects it, RUNS every command it's about to record,
# and writes .buildloop.md
/buildloop-init

/buildloop-plan  "what you want built"      # chat 1 -> a build doc
/buildloop-build path/to/that/doc           # chat 2, NEW CHAT
/proofcheck      the-build-report           # chat 3, NEW CHAT
```

Or skip the loop entirely and use the two standalone pieces, anywhere, with no
config at all:

```bash
/buildplan   "spec this out"          # a spec a fresh session can execute blind
/proofcheck  "is this actually done?" # audit any claim, from anyone, including you
```

**Start here if you're new.** The pair needs no setup and works on its own.

## The rules it enforces

1. **You may never write "done."** HARNESS-PROVEN or LIVE-PROVEN, every time.
2. **The requirement count is a checksum.** One spec arrived cut at 512
   characters, ending on a complete sentence so it looked whole. The build
   invented its own field names and then validated its own invention.
3. **Validate the ruler before you measure.** If a check compares checksums,
   first run it twice unchanged and prove it's stable — otherwise ordinary
   nondeterminism is indistinguishable from the defect you're hunting.
4. **Prove which tree you executed.** An installed binary imports its own copy
   and will pass every check while containing none of your build.
5. **Everything new ships behind an off switch.**
6. **Anything irreversible stops and waits for a human.**
7. **Never relay a subagent's claim as verified.** Re-derive it, or attribute it
   and mark it unverified.
8. **The line ends at ADOPTED, not at built.** A ledger row tracks it, starting
   at `NO — owed`.

## What is actually proven, and what isn't

Written to this project's own standard, because a README that overclaims would be
the funniest possible way to fail.

**LIVE-PROVEN**

- `/buildplan` produced a working 15-requirement spec for a repo it had never
  seen, and caught that the problem description it was given was wrong.
- `/proofcheck` was handed a build report containing three known errors, held
  back from it. It found all three, plus three more a previous audit had missed.
  Zero false accusations.
- The build station ran a 15-requirement build end to end: 15/15 landed, 7
  acceptance checks LIVE-PROVEN through a real installed binary.
- The integrator caught a bug at a seam neither branch owner could see.
- `/buildloop-init` ran end to end and immediately found that 3 of 4 CI commands
  did not exist on the machine, and that the live run was executing a different
  source tree than the one under test.
- **`/proofcheck` passes its own eval suite.** Five cases: four with a real
  planted lie, one honest report that must come back clean. **4/4 caught, 0 false
  positives, 0 cross-attributions.** See [`evals/`](evals/) — `./run.sh <case>`
  stages one in isolation.

**NOT PROVEN**

- **Evals cover `/proofcheck` only.** `/buildplan`, the gate, the builder, the
  integrator and the adopt station have no regression tests. This is the biggest
  gap.
- **Python only.** Never run against another language's toolchain.
- **`/buildloop-init` has completed exactly one run**, on one repo — and it's the
  mandatory first command, so it's the front door with the least mileage.
- **The adopt station has never produced a `YES` row.** It is new.
- **Small-N.** Two full loop runs, one repo, one eval sweep.

If you use it and it breaks, that's a more useful contribution than a star.

## When not to use this

It costs several agents and roughly half an hour per build. Absurd for a typo,
cheap for thirty requirements. **Use it for long builds** — work too big to hold
in one session, where the real failure mode is finishing something and never
switching it on.

## Licence

MIT.
