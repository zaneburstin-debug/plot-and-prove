---
name: buildloop-plan
description: Run the whole planning team on one ask — an audit squad fans out to map ground truth and collapse symptoms into real defects, a planner writes the build design through the lens of the profession that owns the problem, and a gate reviews it against this repo's own laws before any code exists. Loops until approved. Produces a build doc to paste into a fresh build session. Use when the user says "/buildloop-plan", "plan this build", "run the team", or hands over a problem that needs a build doc.
---

# /buildloop-plan — the planning team, one command

Stations ① ② ②ᵇ. Everything up to the moment a doc is handed to a fresh build chat.

```
① AUDIT (3 agents, parallel)  →  ② PLANNER  →  ②ᵇ GATE  ──reject──┐
                                      ▲                            │
                                      └────── rewrite ─────────────┘
                                          APPROVE → doc for the build chat
```

**Everything in this skill is read-only except the build doc itself.** No agent
here edits source, switches branches, restarts a service, or flips a flag.

---

## Step 0 — Load the config, ground the tree, out loud

Read `.buildloop.md` at the repo root. **If it does not exist, run
`/buildloop-init` first** — every agent below depends on it, and a loop running
without it is a loop guessing at this repo.

### 🔴 Step 0a — the config must be GENERATED, not hand-written. Check this first.

```bash
grep -A2 '^generated:' <repo>/.buildloop.md
```

| What you find | Do |
|---|---|
| `by: buildloop-init` + a `preflight:` block | continue |
| `by: hand`, or no `generated:` block at all | **STOP. Run `/buildloop-init` first.** |

**Why this is a hard stop.** A hand-written config declares commands nobody has
ever executed. The loop then plans a proof around them, the build reports them as
green, and the first time anyone checks, the linter was never installed and the
live run was exercising a stale copy of the code. That is not hypothetical — a
config carrying `uv run …` on a machine with no `uv` produced exactly that, and
the failure surfaced only because someone poked at it by hand mid-build.

The user may override by saying so explicitly. If they do, **every downstream
report must carry this line**, and you must repeat it in the handoff:

```
⚠️ CONFIG UNVERIFIED — .buildloop.md was hand-written. No command in it has been
   executed. Any check built on commands.test / lint / live_run is UNPROVEN until
   /buildloop-init runs.
```

Also read the `preflight:` block and carry any `FAILED` or `absent` line into the
plan. A check the planner writes against an absent tool is a check that can only
ever be UNRUN — the doc should say so before the build discovers it.

Then report these four lines. If the tree is wrong, every agent downstream is wrong.

```bash
git -C <repo> branch --show-current
git -C <repo> rev-list --left-right --count <trunk>...HEAD
git -C <repo> status --porcelain | wc -l
git -C <repo> worktree list
```

**Stop and tell the user if:** the branch is far behind trunk (rubric documents
go missing and the gate silently weakens), or the tree is dirty with someone
else's work. *Do not build on top of a tree that holds work you did not author.*

### Step 0b — the knowledge graph, if this repo has one

The audit squad may read a lot of code. Grep answers *"where does this string
appear"*; a code graph answers *"what reaches this, and what does this reach"* —
which is the actual question at station ①.

Only if `graph: auto` in the config **and** `graphify` is installed:

```bash
ls <repo>/graphify-out/graph.json 2>/dev/null
```

| State | Do |
|---|---|
| `graph.json` exists, repo unchanged since | use it as-is |
| `graph.json` exists, commits since | `graphify update <repo>` (incremental, no LLM) |
| No `graph.json` | the two commands below, then continue |

```bash
graphify extract <repo> --code-only --no-cluster
graphify cluster-only <repo> --no-label --no-viz
```

**🔴 Use `extract --code-only`.** The bare form runs an LLM-backed extraction over
prose — API spend you don't need. `--code-only` is local AST parsing: no key, no
cost. `--no-label` skips LLM community naming; `Community 212` is all an agent needs.

**Put the config's `exclude` paths into `.graphifyignore` at the repo root**
before building, or vendored copies get indexed and every symbol appears twice.

**🔴 Read the provenance tag on every edge.** It maps onto this loop's evidence grades:

| graphify tag | Evidence grade | Means |
|---|---|---|
| `EXTRACTED` | MEASURED | parsed from source — a real import/call/definition |
| `INFERRED` | INFERRED | the tool's guess from naming or proximity |
| `AMBIGUOUS` | HYPOTHESIS | it could not resolve the reference |

**An `INFERRED` edge is not evidence.** It is a lead to confirm by reading the
file. A defect graded MEASURED on the strength of an inferred edge is precisely
the failure this loop exists to prevent.

If the graph build fails or the tool isn't installed, **say so in one line and
carry on with grep.** The graph is an accelerant, never a dependency.

### If the ask is a wish

No symptom, no observed behaviour, just a want? Ask **one batched round** of
questions now. Not later, not one at a time.

---

## Step 1 — Fan out the audit squad (parallel, one message)

Spawn `bl-scout` and `bl-runtime` in a **single message** so they run
concurrently. Give each the ask verbatim, the config, and what you learned in Step 0.

| Agent | Brief it to return | Graph move |
|---|---|---|
| `bl-scout` | where the relevant code lives, the live call path, whether it's reachable, and what was already tried (git log + prior build docs) | `graphify explain "<module>"` for the neighbourhood; `graphify query "what calls X"` for reachability. **Grep confirms what the graph suggests** — the graph narrows, the file proves |
| `bl-runtime` | what is ACTUALLY running — deployed version, config file vs the running process env, service uptime vs config mtime | none — the graph describes the checkout, not the running process. **Never let a graph edge stand in for a runtime fact** |
| `bl-rootcause` | *after* the other two: collapse the symptoms into the smallest set of real defects | `graphify path "<symptom A site>" "<symptom B site>"` on **every pair**. A short path through a shared node is the strongest available signal that two symptoms are one defect |

`bl-rootcause` needs the other two reports as input — spawn scout + runtime
together, then rootcause with both reports pasted in.

**The `path` call is the highest-value graph move in this loop.** "Four red
findings turned out to be one bug" is a graph-connectivity question. If two
symptom sites converge on a common ancestor, name that ancestor as the candidate
defect and go read it. If they share no path, that is real evidence they are
genuinely separate — just as useful, and much harder to establish by grep.

**Skip `bl-runtime` if** `runtime.enabled: false` in the config, or the ask
provably cannot touch runtime behaviour. **Say you skipped it and why** — never
skip silently.

### The audit summary the user sees

Before moving on, show a short block. This is their read-back, and it's where
they catch a squad that misunderstood the ask:

```
SYMPTOMS: <n>   →   DEFECTS: <m>
  DEFECT A — <name>   [MEASURED|INFERRED|HYPOTHESIS]   file:line
  DEFECT B — ...
DO NOT BUILD: <symptoms that were downstream of a defect above>
COULD NOT VERIFY: <gaps>
```

If `m` is 0, **stop.** There is nothing to build. Say so — that's a finding, not
a failure, and Doctrine 12 says stop at done.

---

## Step 2 — bl-planner writes the build design

Hand it: the ask, all audit reports, the config, and the Step 0 tree state.

Its first move is to **name the discipline** — what kind of problem this is, who
solves it for a living, how they approach it — and design in that idiom. Its
output follows `/buildplan` and must include the `## Integration` section
pre-answering the gate's questions.

**Two graph moves before it designs anything:**

1. **`graphify query "what already handles <the thing>"`** — repos routinely pay
   to build something they already had. **The cheapest design is discovering the
   code exists.**
2. **`graphify explain "<every module the design will touch>"`** — the degree
   count *is* the blast radius. A change to a node with 40 edges is not the same
   size of change as one with 3, and `## Integration` should say which it is.

**Do not let it proceed if the audit found only HYPOTHESIS-grade defects.** Send
it back for the one measurement that would confirm. Building against a guess is
how four consecutive wrong diagnoses happened.

---

## Step 3 — bl-gate rules on the doc

Hand it the build doc **and** the audit reports — it needs to check the design
addresses the *defects*, not the symptoms.

It returns `APPROVED`, `APPROVED WITH CONSTRAINTS`, or `REJECTED` with three-line
named violations: which requirement, which document clause, and the constraint
the rewrite must satisfy.

**One near-free check that catches invention:** for every module, function,
table or endpoint the design claims it will touch, confirm the thing is real.

```bash
graphify explain "<name the design references>"     # or: grep -rn "<name>" <repo>
```

**A design that names something with no node in the graph and no hit in the
source is a red flag** — either the design invented it, or the graph is stale.
The gate must say which it concluded rather than guessing. This is the
document-stage twin of the build chat's read-back gate: it catches a spec
describing a system that does not exist, before code is written against it.

**On rejection:** hand the violations back to `bl-planner` for a rewrite. Never
rewrite it yourself, and never let the gate rewrite it — a gate-lens rewrite
produces something aligned and amateur.

### The bounds — enforce them, the gate can't do it alone

1. **Severity floor.** Only a violation of a *named clause* in a rubric document
   from the config is blocking. Preferences go in non-blocking notes.
2. **Round cap: 3.** At round 3, ship what's green, backlog the rest, say so.
   Do not open a fourth round.

Show a one-line round tracker each pass:
`Round 2/3 — 1 blocking violation remaining (ARCHITECTURE.md §4).`

---

## Step 4 — Hand off

Write the approved doc to the config's `docs_dir`:

```
<docs_dir>/BUILD-<YYYY-MM-DD>-<subject-slug>.md
```

Never create `... 2.md`. A revision supersedes; set a `supersedes:` line and move
the old one to `<docs_dir>/archive/`.

Then report, in this shape:

```
✅ APPROVED after <n> round(s)
   <docs_dir>/BUILD-2026-08-14-<subject>.md

In a FRESH chat:   /buildloop-build <full path>

WHY A FRESH CHAT: this session planned it, so it is a compromised reviewer of it.
The context boundary is the product, not a formality.

WHAT THE BUILD CHAT MUST DO FIRST — the read-back gate.
Watch for:
  a requirement number missing        → truncation. Re-send in pieces, don't re-explain.
  a field name you never wrote        → invention. There's a hole in the spec.
  a requirement whose meaning shifted → drift. Tighten it.
  it writes files before restating    → the gate didn't run. Stop it.

Proof kind promised: HARNESS-PROVEN | LIVE-PROVEN
The build ends with station ❽ — a fresh agent audits its own report before
anything can be adopted.
The one live run that closes it: <the run>

Still yours to decide: <anything the gate flagged as needing a human call>
```

---

## Hard rules for the orchestrating session

- **Never build anything in this session.** This skill plans. Building happens in
  a chat the user opens themselves — **the context boundary IS the product.**
- **Never skip the gate**, even when the doc looks obviously fine. The cheapest
  rejection in the loop is the one before any code exists.
- **Never let the gate rewrite**, and never rewrite the planner's doc yourself.
  Named violations go back to the planner; it rewrites in its own idiom.
- **Report faithfully.** If the audit found nothing, say so. If the gate is still
  unhappy at round 3, say what's shipping and what's being backlogged.
- Exclude every path in the config's `exclude` list from every search.
- Never propose a direct edit to anything in the config's `do_not_edit` list —
  that is a PR proposal to its owner.

## Related

- `/buildloop-init` — writes the `.buildloop.md` this reads
- `/buildplan` — the document format this team produces
- `/buildloop-build` — station ③, executes this doc in a fresh chat
- `/proofcheck` — the build's station ❽ runs it automatically on its own report;
  run it yourself on anything else that claims to be done
- `doctrine/BUILDING-DOCTRINE.md` — the law all five agents are held to
