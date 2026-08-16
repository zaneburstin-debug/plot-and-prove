---
name: proofcheck
description: Audit any claimed proof, test run, or "done" report before accepting it, in any repo. Grounds itself in the project's own docs and config, classifies the claim HARNESS-PROVEN vs LIVE-PROVEN, hunts the four ways a harness lies, checks absence assertions and fail-open success reports, and names the one real run that would close the gap. Use when someone says "/proofcheck", "is this really proven", "verify this", "check the proof", "did this actually run" — or whenever a session (including you) is about to report something as done.
---

# /proofcheck — audit a proof before you believe it

It exists because a session once reported **"358 checks green"** on work where the
build had never once run. Every one was a harness check. That is a bucket wearing
a lab coat.

**Run this on your own work too, not just on other sessions' claims.**

Works on any repo, with or without a build doc. It needs no setup — Step 0 reads
whatever the project already has.

---

## Step 0 — Ground yourself in THIS project. Two minutes, and it decides everything.

You cannot judge whether something is "really run" until you know what a real run
*is here*. Find out from the repo, never from assumption.

```bash
cd <repo root>
# 1. the loop's own config, if this repo has one
sed -n '/^---/,/^---/p' .buildloop.md 2>/dev/null
# 2. the project's own laws. Names VARY — hunt the shape, not just the usual names.
find . -maxdepth 3 -not -path '*/.*' \( -iname 'AGENTS.md' -o -iname 'CLAUDE.md' \
  -o -iname 'ARCHITECTURE.md' -o -iname 'SECURITY.md' -o -iname 'CONTRIBUTING.md' \
  -o -iname 'README.md' -o -iname '*DOCTRINE*.md' -o -iname '*NORTH*STAR*.md' \
  -o -iname '*WORK*ETHIC*.md' -o -iname '*CHARTER*.md' -o -iname '*PRINCIPLES*.md' \
  -o -iname '*RULES*.md' \) 2>/dev/null | grep -vE 'node_modules|vendor|snapshot'
# 3. what CI believes the commands are
find .github/workflows .gitlab-ci.yml Makefile justfile -maxdepth 1 2>/dev/null
```

**If the standard names find nothing, the project has laws under names you did not
guess.** List the repo's top-level and second-level `.md` files and ask which are
binding — do not conclude the project has no rules. One real repo keeps its two
binding documents under a working-practices name and a nested product-charter
name; a fixed list of the usual names returns **zero** there, and would have
reported "no rubrics" on a project that has two and enforces both.

**Check the tree is current before you trust anything you read from it.**

```bash
git rev-list --left-right --count <trunk>...HEAD
git log -1 --format=%cd --date=short          # and the same for the trunk
```

A checkout far behind its trunk describes code nobody is running. Say how far
behind it is in your verdict, or every fact you extract has a silent expiry date
on it.

Extract and write down these five, with the file each came from:

| What | Where it usually lives | If you cannot find it |
|---|---|---|
| **What a real run is** | `.buildloop.md` `commands.live_run` | **Say so.** Without it nothing can be LIVE-PROVEN, and that is your headline finding. |
| **What may block** | `.buildloop.md` `rubrics:`, else `AGENTS.md` / `CLAUDE.md` / `ARCHITECTURE.md` | Only a *named clause* blocks. Preferences are notes. |
| **This project's known traps** | `.buildloop.md` `## Known traps` | Ask, or read the last few commits for what keeps breaking. |
| **Is anything actually running** | `.buildloop.md` `runtime.enabled` | If nothing is deployed, Step 6 is short — say that rather than inventing a process. |
| **The acceptance checks** | the build doc, if one exists | Without a doc you run the generic six below. Say the audit is generic. |

**If a build doc exists, it outranks everything.** Grade against *its* acceptance
checks, and only those — checks written after a build are graded against that
build, so they can only pass. Confirm the doc's requirement count matches what
was delivered; a switched denominator is the cheapest lie to tell and the easiest
to catch.

---

## Step 1 — Classify it. Say the word.

| | Means |
|---|---|
| **HARNESS-PROVEN** | Tests, suites, checks. Evidence the HARNESS works. |
| **LIVE-PROVEN** | One real end-to-end run: real entry point, real stages, real dependencies, real process, real money. |

"I ran the tests" is HARNESS-PROVEN. "All suites pass" is HARNESS-PROVEN.
If you cannot tell which it is, it is **neither** — go find out.

A number of passing checks is never evidence of a working system. It is evidence
of a working harness.

## Step 2 — Hunt the four lies

Read the actual proof. For each, answer yes/no **with the line that proves it**.

**1. Fake stations.** Are the real components replaced by stubs (`lambda job: {...}`,
a mock server, an in-memory double)? A stub proves the conveyor moves. It proves
nothing about what rides on it.
> *Seen:* a stub for `_gh_get` while the code called `search_repos` — a decoration
> that was never on the code path. The suite passed only because the real API
> happened to answer that minute.

**2. Direct calls that skip the seam.** Does the proof call the function straight,
bypassing the boundary it claims to fix — the router, the queue, the HTTP layer,
the CLI dispatch? Skipping it proves the function, not the fix.
> *Seen:* well-covered internals, **zero coverage on the routing path into them** —
> which is exactly where the worst bug lived.

**3. It ran a different tree than the one under test.** The highest-frequency lie,
and it has more shapes than people expect:
- `sys.path.insert(0, "/absolute/...")` pointing at the live tree from a worktree
- an **installed** package resolving to `site-packages` while the change sits in the source dir
- a container/image built before the change
- stale bytecode, a cached layer, a dev server that never reloaded
- cwd deciding the import, when the harness `cd`s somewhere between steps

**Never accept a live result without an execution assertion.** Make the proof print
the path/version/commit of what it actually executed — `python -c "import pkg; print(pkg.__file__)"`,
`node -p "require.resolve('pkg')"`, `<binary> --version`, `git rev-parse HEAD` — and
check it points at the tree under test.
> *Seen:* a "27 pass / 0 fail" regression check that measured untouched code.

**4. Canned external replies.** Does a fake return hardcoded JSON from a model, API,
database or queue? That proves the parser, never the dependency.
> *Seen:* a reviewer seat that sat **empty in 42% of sittings** passed every harness,
> and every no-show was logged as a pass.

Then state plainly what each lie leaves unproven.

## Step 3 — Can it fail?

For every meaningful check, finish this sentence:

    This goes RED if ______.

No sentence → it is a demonstration, not a proof. The strong version: **break it on
purpose once, watch it go red, put it back.**

Two traps:

- **Inert stubs.** Confirm the stub is actually on the code path, not merely present.
  A check whose result depends on who ran it, or on the network being up that
  minute, is measuring the weather.
- **Absence assertions.** "This file does not exist" is a claim about the future.
  When the feature that writes it is switched on, the check goes red *because the
  system did its job*. Either record why it must STAY absent, or assert contents
  instead. **Absence is a number too** — and before trusting any zero, prove the
  instrument could have seen a non-zero.

## Step 4 — Which path produced the success?

A guarded refusal and an unguarded success look identical from outside.

Ask: did this success come from the guarded path, or did something **fail open**
after a judged refusal?

> *Seen:* the review sat, the safety veto FIRED, the acceptance check failed, three
> repairs failed, nothing was built, rolled back — a **correct refusal**. Then the
> router read that verdict as an infrastructure hiccup and fell open to an
> unguarded path, which rebuilt the file with no review, no veto and no checks, and
> reported *"all 3 test suites pass. Nothing left to build."* The file it shipped
> was missing a required field entirely.

The distinction that fixes it: **"a stage RAISED"** (falling open is fine — nothing
was judged) vs **"the system JUDGED and said no"** (falling open deletes the answer).

## Step 5 — Whole build, or one stage?

Testing one stage and calling the build proven is the same error as testing one
file and calling the repo green.

- Name every stage the change touches.
- Name the paths **into** it, not just the stage itself.
- Then run it from the real entry point, through every stage, to the real output —
  the chain in `commands.live_run`, or the equivalent you established at Step 0.

## Step 6 — Environment reality check

If a flag or config is involved, list every process that must see it and how each
one gets it: shell · launcher · cron · systemd · LaunchAgent · container · CI
runner · serverless invocation · long-lived daemon. Then read the value from
**inside** each running process, not from the file.

> *Seen:* an alarm that had never fired — the flag was in the env file, the env
> file is carried by the LAUNCHER, and **cron carries nothing**. 73 runs, OFF every
> time.
> *Seen:* the process exec'd at 23:41; the flag was written at 02:26. Eleven keys
> sat in the file and were absent from the process. **The seam is TIME, not a call site.**

And when a liveness check says something is alive, ask what it would say about a
corpse. A checker that lists dead entries as alive turns every green into noise.

If `runtime.enabled` is false and nothing is deployed, say that — do not invent a
process in order to have something to report.

---

## Verdict format

Always end with this. Never soften it.

    VERDICT: HARNESS-PROVEN | LIVE-PROVEN | NOT PROVEN

    GROUNDED IN
      live run     <commands.live_run, or "NOT DEFINED — nothing can be LIVE-PROVEN">
      rubrics      <the files that may block>
      build doc    <path, or "none — generic audit">

    WHAT IS ACTUALLY PROVEN
      - …

    WHAT IS NOT
      - …

    LIES FOUND
      #1 fake stations      yes/no — <line>
      #2 skipped seam       yes/no — <line>
      #3 wrong tree ran     yes/no — <the execution assertion, or its absence>
      #4 canned externals   yes/no — <line>

    THE ONE RUN THAT WOULD CLOSE IT
      <real entry point> → <stages> → <what to look at>
      Cost / risk: <money? mutates prod? then label the gap and schedule it>

---

## Rules

- Report faithfully. If it is not proven, say **NOT PROVEN** in those words.
- Never write bare "done", bare "proven", or a bare tick.
- Finding that a proof is weak is a **success**, not a failure — say it plainly and
  move on without ceremony.
- **Do not manufacture findings to look rigorous.** "I checked these six things and
  they hold" is a valid result. An auditor that always finds something is as
  useless as one that never does.
- A command that is not installed is **UNRUN**, never passed. Say which.
- If the honest answer is "this cannot be run live without spending money or
  touching prod", state the exact boundary and put the real run at the top of the
  next session.
- Related: `/buildplan` (the other half — the spec that makes proof gradeable),
  `/buildloop-init` (writes the `.buildloop.md` Step 0 reads).
