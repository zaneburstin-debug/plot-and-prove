---
name: buildplan
description: Turn a rough ask into a build plan a fresh session can execute end to end without coming back with questions. Produces numbered requirements with a count, an output contract with no holes, a scope fence, a WHAT YOU DON'T KNOW block, and acceptance checks written BEFORE the build — plus the read-back gate the build session must pass first. Use when someone says "/buildplan", "write the build plan", "plan this build", "spec this out", "hand this to another session", or is about to hand work to a second session.
---

# /buildplan — write a plan the next session can execute blind

It exists because a spec once arrived at a build session **truncated at 512
characters**, ending on a complete sentence so it looked whole. The build
invented its own field names, wrote the acceptance check against its own
invention, and shipped a file with a different contract than the one asked for.
The code was never the problem.

**Your output is a document someone can paste into a fresh session.** Not a
summary of one. Write the artifact.

---

## Step 0 — Refuse to plan a wish

Before writing anything, hunt the request for holes. A hole is anywhere the build
session would have to **invent** something:

- a field name, key, or column
- a threshold, timeout, limit, or retry count
- an output format
- the behaviour of an edge case
- what "done" means

**Rule of thumb: if two competent people would build different things from this
request, it is a wish, not a spec.** Fill every hole yourself, or ask exactly one
round of questions — batch them, don't drip.

If the repo has a `.buildloop.md`, read it now. Its `## Known traps`, `rubrics:`
and `commands:` are the inputs to Steps 4, 5 and 6, and they are project-specific
facts you would otherwise have to guess.

---

## Step 1 — Number the requirements and state the count

    SPEC — N numbered requirements. Confirm you received all N.
    1. ...
    2. ...

The count is a checksum. Truncation cannot survive it. Never write a spec as prose
paragraphs; a paragraph that loses its second half still reads fine.

Each requirement is one testable statement. If a requirement needs an "and", it is
probably two requirements.

**Say who owns each one.** Most are for the builder. Some are for the orchestrator
(a report block, a handoff step) and some are the human's call. A requirement whose
owner is unstated gets counted against the wrong denominator — a build reporting
"14/14" against a 15-requirement spec is the cheapest lie to tell by accident.

## Step 2 — The output contract

State the exact shape, with every field named and typed. The right altitude:

    Returns JSON with EXACTLY three keys and no others:
      missing  — list[str], keys in the file but not the process, sorted A-Z
      extra    — list[str], keys in the process but not the file, sorted A-Z
      in_sync  — list[str], keys in both WITH THE SAME VALUE, sorted A-Z
    A key present in both with different values goes in `missing`.
    Never print values — they are secrets.

That last line — **the ambiguous case named explicitly** — is the one that got lost
in the real incident. Enumerate every case the reader could resolve two ways, or
the build will resolve it for you and call that the spec.

## Step 3 — The scope fence

Half the job is the rooms you did not renovate. Every plan names both:

    TOUCH:        <exact files/functions>
    MUST NOT CHANGE (assert, do not assume):
      - <the load-bearing files> — md5/checksum before and after
      - <anything in the config's do_not_edit>
    FLAG:         <NAME>, ships OFF, additive and reversible

**Assert it, never assume it.** "Flag off is byte-identical" was assumed across one
repo for months and was wrong: two module objects wrapped one file, so a proof
popped a flag, the second import refilled it, and the proof tested flag-ON while
reporting flag-OFF.

**Then check the fence against your own acceptance checks.** If a check runs the
test suite and the suite writes into a directory the fence protects, the plan
contradicts itself and the build will breach its own fence on the first command.
That has happened — a fence protected an output directory while the plan's own
lint step wrote there.

## Step 4 — WHAT YOU DON'T KNOW

A fresh session is a brilliant contractor with total amnesia who has never seen the
house. Anything you leave out gets filled with a reasonable guess, and reasonable
guesses are how load-bearing things get deleted.

Always state, when relevant:

- **working directory**, and whether cwd changes which code gets imported
- **which environment / which host**, and whether the deployed one differs
- **which tools are NOT installed** — name them; a plan that calls a missing tool
  produces a check that can only ever be UNRUN
- **whether the entry point runs the source tree or an installed copy** — an
  installed binary resolving to `site-packages` will pass happily while containing
  none of the build
- what has **no safety net**
- what **looks dead but is imported**
- what **must not be deleted**

Take the project-specific half from `.buildloop.md` `## Known traps` verbatim rather
than inventing it, and say which ones you verified against live code — these are
point-in-time facts and a stale one is worse than a missing one.

## Step 5 — Acceptance checks, written NOW

3–5 pass/fail statements, concrete enough that the reader could run them
themselves. They go in the plan, **before any code exists**.

If you cannot write a check for a requirement, that requirement is still a wish —
go back to Step 0.

Checks written after the build are graded against that build, so they can only
pass. That is exactly how one blueprint invented a pair of field names and then
validated its own invention.

**Validate the ruler before the measurement.** If a check's instrument is a
comparison — a checksum, a diff, a count — the plan must first prove that
instrument is stable. Run the thing twice unchanged and assert the two results
match. Without that control, a failure caused by ordinary nondeterminism is
indistinguishable from the defect you are hunting, and a passing check proves
nothing about either.

## Step 6 — The proof plan (say which kind, up front)

State what will be HARNESS-PROVEN and what will be LIVE-PROVEN, and name the single
real end-to-end run that closes it:

    LIVE RUN: <real entry point a user actually touches> → <every stage> → ship

Take it from `.buildloop.md` `commands.live_run` if the repo has one. **Require the
run to assert which tree it executed** — a printed module path, version, or commit —
or it may be exercising a pre-build copy and reporting green.

If that run costs money or mutates prod, say so, label the gap loudly, and put the
run at the top of the next session. That is never a reason to accept harness-only.

## Step 7 — Emit the read-back gate

Every plan ENDS with this block, verbatim:

    ── READ-BACK GATE — do this before writing any code ──
    Before you touch a file, output:
      1. Each numbered requirement, restated in your own words, with the count.
      2. The output contract — every field name and type.
      3. The acceptance checks you will run.
    Write nothing until that restatement is on screen.

## Step 8 — Emit the progress block, if this repo has a hook

The build session is usually a background agent nobody is watching. Without a
progress signal you can only see that it is *alive*, not how far through the plan
it is.

**Read `progress_hook` from `.buildloop.md`.** If it is set, emit this block with
the command and `N` filled in. If it is empty, **omit the block entirely** — do not
invent a reporting command, and do not hardcode one the repo has never heard of.

    ── REPORT YOUR PROGRESS ──
    After you finish each numbered requirement, run exactly this, one line,
    no ceremony:

        <progress_hook> step <n> --of N --doc "<doc title>" --status "<what's next>"

    <n> is the requirement number you just COMPLETED — not the one you're
    starting. Run it with 0 at the top, right after the read-back gate.
    If you get blocked, re-run it at the same <n> with --status "BLOCKED: <why>".

Never let the build session invent its own step count. The bar is only worth
reading because `N` came from the spec, and a session that renumbers its own work
is reporting against a plan nobody wrote.

Then tell the reader what to look for when they diff it:

| What you see | What it means |
|---|---|
| a requirement number missing | truncation — re-SEND in pieces, don't re-explain |
| a field name you never wrote | invention — there is a hole in the spec |
| a requirement whose meaning shifted | drift — tighten that requirement |
| it starts writing files before restating | the gate did not run — stop it |
| "flag-off is byte-identical" with no checksum pair on screen | assumed, not asserted — reject |

---

## Output template

    SPEC — N numbered requirements. Confirm you received all N.
    1. …

    OUTPUT CONTRACT
    …

    SCOPE FENCE
    TOUCH: …
    MUST NOT CHANGE (assert): …
    FLAG: … (ships OFF)

    WHAT YOU DON'T KNOW
    …

    ACCEPTANCE CHECKS
    0. <the ruler control — run it before trusting any comparison check>
    A. …
    B. …

    PROOF PLAN
    HARNESS-PROVEN: …
    LIVE-PROVEN (the one real run, with its execution assertion): …

    ── READ-BACK GATE — do this before writing any code ──
    …

    ── REPORT YOUR PROGRESS ──   (only if progress_hook is set)
    …

---

## Rules

- Write the document, don't describe it.
- Plain English, no jargon. Speed to launch, minimum viable.
- Never bare "done" or "proven" anywhere in the plan.
- Never name a tool, path or command you have not confirmed exists in this repo.
- If the user pushes back and reaffirms, that is their call — build it their way
  and say so once.
- Related: `/buildloop-build` (the team that executes this doc), `/proofcheck`
  (the other half — the audit that grades against these checks),
  `/buildloop-init` (writes the `.buildloop.md` this reads).
