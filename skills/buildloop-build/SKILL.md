---
name: buildloop-build
description: Execute an approved build design end to end — read-back gate, branch builders in isolated git worktrees, an independent prover that never saw the build reasoning, an integrator that owns the seams, and an adopt station that turns a finished build into a used one. Resumable across sessions via a run-state file, and every build appends a line to the ledger so unadopted work stays visible instead of going dark. Station ③, the counterpart to /buildloop-plan. Use when the user says "/buildloop-build", "build this doc", "run the build team", "resume the build", or pastes an approved build design into a fresh chat.
---

# /buildloop-build — the build team, one command

Station ③. `/buildloop-plan` produced the doc; this executes it.

```
   doc from /buildloop-plan
        │
   ⓿ GROUND ── doc incomplete ──▶ STOP, ask
        │
   ❶ READ-BACK ◄── the human's catch point. No agent. No files written.
        │
   ❷ ORDER ── the DOC decides serial vs parallel, never ambition
        │
   ❸ BUILD ──── bl-builder × branches, each in its own worktree
        │
   ❹ PROVE ──── bl-prover, never saw the build reasoning
        │
   ❺ INTEGRATE  bl-integrator owns the seams nobody was assigned
        │
   ❻ LIVE RUN ─ the one real run the doc names
        │
   ❼ REPORT ──▶ station ④ /proofcheck, in a chat that never saw this one
        │        …and one line appended to <docs_dir>/LEDGER.md
        │
   ❽ ADOPT ──── switch it on, use it N times as a stranger, record it.
                Most builds STAGE this and leave the ledger row "NO — owed".
                A build that is never adopted is a build that did not happen.
```

**Every station writes its result to `<docs_dir>/runs/RUN-<doc-slug>.md`.** That
file is what lets a long build resume in a session that never saw this one.

**You are the orchestrator, not the builder.** You hold the doc, split it, spawn
the team, and report. Resist writing the code yourself — your context fills with
1,000 lines of design plus 50 requirements of implementation, and the last
requirement gets built by an exhausted session.

---

## ⓿ Step 0 — Ground the config, the tree and the doc, out loud

Read `.buildloop.md` at the repo root. If it's missing, run `/buildloop-init`
first.

### 🔴 The config must be GENERATED. Check before anything else.

```bash
grep -A2 '^generated:' <repo>/.buildloop.md
```

`by: buildloop-init` plus a `preflight:` block → continue. `by: hand`, or no
`generated:` block → **STOP and run `/buildloop-init`.** A hand-written config
declares commands nobody has executed; you would then run acceptance checks
through a tool that isn't installed, or a live run that exercises a stale copy of
the code, and report both as green.

If the user overrides explicitly, **every report this session must carry**:

```
⚠️ CONFIG UNVERIFIED — no command in .buildloop.md has ever been executed.
```

Then read the `preflight:` block. **Any command marked `FAILED` or `absent` is
UNRUN for the whole session** — it may never be reported as passed, and the final
report must name it as an open gap. Then:

```bash
git -C <repo from the doc's scope fence> branch --show-current
git -C <repo> rev-list --left-right --count <trunk>...HEAD
git -C <repo> status --porcelain | wc -l
git -C <repo> worktree list
```

**Stop and tell the user if:** the tree is dirty with someone else's work, or the
branch is far behind trunk.

Then check the doc itself:

| Check | Fail means |
|---|---|
| `SPEC — N numbered requirements` line present | not a `/buildplan` doc — do not build it |
| Requirements 1…N all present, none skipped | **truncation.** Ask for a re-send in pieces — never re-explain |
| `OUTPUT CONTRACT`, `SCOPE FENCE`, `ACCEPTANCE CHECKS`, `PROOF PLAN` all present | an ungated doc. Send it back to `/buildloop-plan` |
| A flag is named and ships OFF | no reversibility. Stop |

**A missing requirement number is the single highest-value thing you will catch
all session.** A spec once arrived truncated at 512 characters, ending on a
complete sentence so it looked whole; the build invented its own field names and
then validated its own invention.

### 🔴 Step 0c — Resume, or start clean. Check before you spawn anything.

A long build outlives the chat it started in. Sessions die, contexts fill,
machines sleep. Without state on disk, a crash at station ❺ throws away three
agents and forty minutes, and the restart quietly re-runs work that was already
correct.

```bash
ls <docs_dir>/runs/RUN-<doc-slug>.md 2>/dev/null
```

| Found | Do |
|---|---|
| nothing | fresh build — create the file at the end of Step 1 |
| a file whose last station is ❼ or ❽ | **this build is finished.** Do not rebuild it. Say what it says and stop |
| a file mid-flight | **resume from the next station**, do not restart |

**Before resuming, re-verify the world still matches the file** — the worktree
still exists at the recorded sha, the shared checkout is still clean, and the
fenced files still hash to their recorded values. State on disk is a claim about
the past; the tree is the fact. If they disagree, say so and start clean.

### Write the run state after EVERY station

One file per build at `<docs_dir>/runs/RUN-<doc-slug>.md`, appended to as you go.
It is the resume state and the audit trail in one:

```
DOC:        <path>            STARTED: <date>
BRANCH:     <branch> @ <sha>
WORKTREES:  <branch> → <path>
BASELINES:  <artifact> = <md5>   (captured at check 0, BEFORE any edit)
FENCE:      <file> = <md5> before

STATION ❶ read-back   DONE <time> — 15/15 restated
STATION ❷ order       DONE <time> — 1 branch, serial (TOUCH sets overlap)
STATION ❸ build       DONE <time> — 14/14 landed, commit <sha>
STATION ❹ prove       DONE <time> — 7 checks pass, G split
STATION ❺ integrate   ...
```

The cost is one small write per station. The thing it buys is that a long build
becomes restartable by someone who is not you, in a session that never saw this
one — which is the same property the whole loop is built on.

---

## ❶ Step 1 — The read-back gate. You do this, not an agent.

Before any file is written, before any agent is spawned, output:

1. **Every numbered requirement, restated in your own words, with the count.**
2. **The output contract** — every field name and type.
3. **The acceptance checks you will run.**

This must be *your* restatement, in the orchestrating session, because it proves
**the doc survived the context boundary.** Delegating it proves only that an
agent can read.

Then tell the user what to look for:

| What they see | What it means |
|---|---|
| a requirement number missing | truncation — re-send in pieces, don't re-explain |
| a field name they never wrote | invention — there's a hole in the spec |
| a requirement whose meaning shifted | drift — tighten it before building |
| files written before the restatement | the gate didn't run — stop it |

If the config sets `progress_hook`, fire it here at step 0 so the bar exists from
the first minute.

---

## ❷ Step 2 — Let the doc decide the order. Not your ambition.

These docs group requirements into **branches or phases** with a declared order —
*"BRANCH A — do first, blocks everything."* That grouping is the work-breakdown
structure; use it, don't invent your own.

Two branches may run **in parallel only if both are true:**

1. The doc declares no dependency between them, **and**
2. Their `TOUCH` file sets are **disjoint** — verify by intersecting the scope
   fence lists yourself.

Otherwise, **serial.** Parallel builders on overlapping files is not a speed
optimisation; it is the reproduction of the defect this loop exists to prevent:

> *Many authors, no integrator. Six parallel sessions on one live checkout. The
> worst bug in that system was a defect at the seam between two steps, where each
> step's owner only repaired their own file — a structural mirror of the process
> that produced it.*

Show the plan before you spawn:

```
BRANCH A — reqs 1–12   — serial, blocks B/C/D
BRANCH B — reqs 13–26  ─┐ parallel: TOUCH sets disjoint (verified)
BRANCH C — reqs 27–41  ─┘
BRANCH D — reqs 42–50  — serial after B and C (shares api/handlers.py)
ONE-WAY DOORS: req 19, req 33 — these stop for the human
```

**One-way doors stop and ask.** The doc lists what's irreversible-if-wrong.
Doctrine 6 is law: back up before prod, and the irreversible stuff is the owner's
gate. Never flip a capability flag, delete data, restart a service or push to a
shared trunk on your own authority — **stage it and hand over the one command.**

---

## ❸ Step 3 — Spawn the branch builders

One `bl-builder` per branch. Give each: **its requirements verbatim**, the full
output contract, the full scope fence, the `WHAT YOU DON'T KNOW` block, the
config, and its worktree path. **Never paraphrase requirements into a brief** —
hand over the doc's own words.

Parallel branches go in **one message** so they run concurrently. Each takes its
own worktree; never the shared checkout.

If `progress_hook` is set, every builder fires it as it completes each
requirement. That bar is the only view into a background build — a bar that never
moves reads as a dead agent, which is exactly what a stalled builder is.

---

## ❹ Step 4 — Prove it, from a context that never built it

Spawn `bl-prover` with the **build doc and the builders' reports** — never the
builders' reasoning. **Independence is the product.** A session that just built
something is the worst possible auditor of it; this is the harness-proven problem
applied to sessions instead of tests.

The prover takes the acceptance checks **from the doc**, not from the build.
Checks written after a build are graded against that build, so they can only pass.

**Do not let a passing count stand in for evidence.** Ask what the hardest single
check actually exercised.

---

## ❺ Step 5 — Integrate. This station is not optional.

Spawn `bl-integrator` with every branch report. It builds the seam map, merges in
the doc's declared order, and hunts the six defects no single branch owner can see.

**Run it even when there was only one branch.** Its whole-build run and its
config-reaches-the-process check are things no builder did, regardless of how
many branches there were.

---

## ❻ Step 6 — The one live run

The doc's proof plan names it. The config's `commands.live_run` holds it.

Run it. Real entry point, real stages, real dependencies, real process. **One real
run outranks 300 unit checks** — it is the only thing that exercises the seams,
the cwd, the env, the singletons and the latency at the same time.

If `commands.live_run` is empty, **say so in the report as an open gap.** Do not
substitute the test command for it and do not quietly call the result LIVE-PROVEN.

If the run costs money or mutates prod: **label the boundary loudly, name the
exact gap, and put the run first in the next session.** That is never a reason to
accept harness-only.

---

## ❼ Step 7 — Report, and write the ledger line

```
BUILD REPORT — <doc title>
Requirements:  <n>/<N> landed · <k> deferred (numbered, with why)
Proof:         <k> LIVE-PROVEN · <h> HARNESS-PROVEN · <u> UNPROVEN
The live run:  <ran / owed — the exact run>
Scope fence:   MUST NOT CHANGE re-verified — PASS | FAIL (<file>)
Flags:         <name> — OFF in file / OFF in process (verified separately)
Seams:         <what the integrator found>
Branch:        <branch> @ <sha> — NOT pushed, NOT merged to trunk
Human's calls: <one-way doors reached, conflicts the doc didn't decide>
ADOPTION:      OWED — <the exact command that switches it on>
MISSES:        <what didn't work — with the output>

Next: /proofcheck this report in a chat that never saw this one.
```

**Report faithfully, including the misses.** Say "it didn't work" with the output.
No false victories, no bare "done," no bare "proven."

### Then append one line to `<docs_dir>/LEDGER.md`

A build that exists only in a chat transcript is a build nobody can find next
month. Create the file if it does not exist, with this header:

```
| date | doc | branch@sha | reqs | proof | live run | ADOPTED |
|---|---|---|---|---|---|---|
| 2026-08-15 | graph-contract | bl/graph-contract@27c373f | 14/15 | 7L 8H 0U | ran | **NO — owed** |
```

`ADOPTED` starts **NO — owed** for every build that ships behind a flag, and it
stays that way until station ⑧ changes it. **That column is the point of the
file.** A ledger where most rows say `NO` is not an embarrassment — it is the
first honest measurement of the gap between building and shipping, and you cannot
close a gap you are not counting.

---

## ❽ Step 8 — ADOPT. The station that makes the build real.

Requirements landing is not the finish line. A flag that ships OFF and is never
turned on is a build that did not happen, and it is the single most common way
this loop's output dies.

**Adoption is three things, in order:**

1. **Switch it on** — flip the flag, deploy, merge, or whatever "on" means here.
2. **Use it for real, N times, as a stranger would.** Not the fixture. Real input
   you did not choose to make the code look good. One good result is not a win;
   look for 3–5 before you believe it.
3. **Write down what happened**, and update the `ADOPTED` column.

**Every step of that is a one-way door, so none of it is yours to do alone.**
Flipping a capability flag, deploying, merging to a shared trunk, restarting a
service — the doc's own SCOPE FENCE says these stop for the human. So station ⑧
runs in exactly one of two modes:

| Mode | When | What you do |
|---|---|---|
| **RUN IT** | the human explicitly says to, in this session | do all three, then update the ledger row to `YES — <date>, <n> real uses` |
| **STAGE IT** | every other time, which is most of the time | print the exact commands, leave the row `NO — owed`, and say what the first real use should be |

Staging is not a failure state. **An owed adoption that is written down is
strictly better than an adoption that silently never happens** — which is the
current default and the reason a ledger exists at all.

### What "used it for real" means

Pick the input the code was **not** written against. If this is a
multi-tenant feature, act as a customer who does not exist yet — the bug that only
fires for customer #2 is invisible to customer #1, and no fixture will show it to
you. If it is a user-facing change, drive the real surface, not a component
harness. Then record the result in the ledger row, including the boring answer:
"used 4×, no problems" is a finding.

If adoption reveals a defect, that is a **new build**, not a repair round on this
one. Write it up and stop. Do not reopen a closed build from its adoption run.

---

## Hard rules for the orchestrating session

- **Never mark your own homework.** The prover and the integrator exist because
  you cannot audit what you just coordinated.
- **Never relay a subagent's claim as verified.** You are told not to audit your
  own work; you are equally not allowed to launder someone else's. A finding from
  a builder, prover or integrator that reaches your report **carries their
  authority, not yours** — either re-derive it yourself, or attribute it in the
  report as "the integrator found" and mark it unverified. Three false statements
  once survived four agents and a full audit precisely because each was inherited
  and none was re-checked.
- **Never adopt on your own authority.** Flipping a flag, deploying, merging to a
  shared trunk or restarting a service is station ⑧ and it belongs to the human.
  Stage it and hand over the one command.
- **Never skip the ledger line**, even when the news is bad. Especially then — an
  unadopted build that nobody wrote down is how 29 builds went dark.
- **Never renumber, merge or split the doc's requirements.** The count is a checksum.
- **Never fill a hole in the spec quietly.** A missing field name, threshold or
  format is a **finding for the human** — the same hole that made a build invent
  its own contract.
- **Never build on the shared checkout.** Worktrees, always.
- **Never edit anything in the config's `do_not_edit` list** — that is a PR
  proposal to its owner.
- **Never print a secret's value**, in any agent brief or any command. Key names
  only (`grep -oE '^[A-Za-z_]+=' .env | tr -d =`), `md5sum` to compare, `grep -c`
  to count. **Redact on the KEY, never the value** — subagents inherit
  instructions, not caution.
- **Never write bare "proven" or "✅ done"** — HARNESS-PROVEN or LIVE-PROVEN, every time.
- Exclude every path in the config's `exclude` list from every search.
- **Stop at done.** If a requirement turns out to be unnecessary, that's a
  finding. Don't manufacture motion.

## The bounds — so the build station terminates

1. **A deferred requirement is reported, not retried forever.** Two failed
   attempts on one requirement → stop, report it numbered with the reason, move on.
2. **Repair rounds cap at 3.** Prover finds bugs → builder repairs → re-prove. At
   round 3, report what's green and what isn't. Do not open a fourth.
3. Only a failure of an acceptance check **from this doc** is blocking.
   Everything else is backlog, not another round.

## Related

- `/buildloop-plan` — stations ① ② ②ᵇ, produces the doc this consumes
- `/buildplan` — the document format, including the read-back gate
- `/proofcheck` — station ④, run it on this report in a fresh chat
- `doctrine/BUILDING-DOCTRINE.md` — the law all three agents are held to
