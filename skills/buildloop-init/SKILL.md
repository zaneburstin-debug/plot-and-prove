---
name: buildloop-init
description: Point buildloop at a repo. Inspects the codebase, works out its language, test/lint/live-run commands, what to exclude, what must not be edited, and the traps an agent would otherwise walk into — then writes .buildloop.md at the repo root. Use when the user says "/buildloop-init", "set up buildloop here", "point buildloop at this repo", or runs any buildloop command in a repo with no .buildloop.md.
---

# /buildloop-init — point the loop at this repo

Writes `.buildloop.md` at the repo root. Every other buildloop skill and agent
reads it first, so **this file is the entire portability story.** Take it
seriously; a lazy config produces a loop that guesses.

**You inspect and propose. The user confirms.** Do not write the file until you
have shown them the fields you could not determine.

---

## Step 1 — Find the repo root and refuse to guess

```bash
git rev-parse --show-toplevel
ls -a "$(git rev-parse --show-toplevel)" | head -40
```

If this is not a git repo, **stop.** The loop builds in worktrees; without git
there is nowhere safe to build. Say so and offer `git init`.

If `.buildloop.md` already exists, read it and ask whether to update or replace.
Never silently overwrite — the `## Known traps` section is hand-written knowledge
that no inspection can regenerate.

## Step 2 — Detect the mechanical fields

Work these out from the repo, in this order. Cite the file you got each from.

| Field | Where to look |
|---|---|
| `language` | `pyproject.toml` / `package.json` / `go.mod` / `Cargo.toml` / `Gemfile` / `pom.xml` |
| `trunk` | `git symbolic-ref refs/remotes/origin/HEAD`, falling back to `git branch -r` |
| `commands.install` | lockfile → the tool that owns it (`uv.lock`→`uv sync`, `package-lock.json`→`npm ci`, `pnpm-lock.yaml`→`pnpm i --frozen-lockfile`) |
| `commands.test` | the `scripts` block, `[tool.pytest]`, `Makefile`, CI workflow files |
| `commands.lint` / `typecheck` | same sources — CI workflows are the most reliable, they are what actually gates merges |
| `exclude` | `.gitignore`, plus any large directory of copies (see below) |

**Read the CI workflow files.** `.github/workflows/*.yml` states the commands
that actually gate this repo's merges, which beats anything in a README. Take
the install/test/lint commands from there verbatim — they are the ones that are
known to work.

**Enumerate with `git ls-files`, not `ls`.** A bare `ls a b c 2>/dev/null` over a
list of candidate manifests can come back empty even when one of them exists, and
you will conclude "no manifest" about a repo that has one. This happened while
writing this skill.

```bash
git ls-files | grep -E '^[^/]+\.(toml|json|mod|lock|cfg)$|^\.github/workflows/'
```

### The exclusion check — do this, it is cheap and it has burned people

Find directories that will make every search return duplicates:

```bash
git ls-files | sed 's|/.*||' | sort | uniq -c | sort -rn | head -15
find . -maxdepth 2 -type d -name 'node_modules' -o -maxdepth 2 -type d -name 'vendor' \
  -o -maxdepth 2 -type d -name '*snapshot*' -o -maxdepth 2 -type d -name '*backup*' 2>/dev/null
```

**Untracked-but-not-gitignored directories are the dangerous ones** — they are
invisible to `git ls-files` and fully visible to grep. One repo carried a
snapshot directory holding 1,411 source files against the repo's 409 real ones,
untracked and un-ignored, so every symbol appeared twice and agents reported dead
copies as live code. Check for it:

```bash
git status --porcelain --ignored=no | grep '^??' | head
```

## Step 3 — The one field you must not fake: `commands.live_run`

This is the difference between a loop that can say LIVE-PROVEN and one that can
only ever say HARNESS-PROVEN.

Ask yourself: **what does a user actually touch, and what is the smallest command
that runs that whole path for real?**

| Project shape | A real live run looks like |
|---|---|
| HTTP API | `curl` the real route on a locally-running server, with a real payload |
| CLI | invoke the installed binary on a real input file, check the exit code and output |
| Web app | start the dev server, drive one real user flow, read the network response |
| Library | a consumer script that imports the **installed** package (not the source tree) and calls it |
| Data pipeline | run one real record end to end through every stage |
| Worker / queue | enqueue one real job and read its result from the real store |

### 🔴 Run it once, here, before you write it down

**A `live_run` you have not executed is a guess.** Run it now and paste the
output into your report. Two things it catches immediately:

- **It doesn't work.** Wrong flag, wrong path, missing fixture. Better to find
  that now than in a build report three sessions from now.
- **It depends on the dev toolchain.** `uv run …`, `npm run …`, `poetry run …`
  invoke the *source tree* through a tool that may not exist where the code
  actually runs. **Prefer the installed entry point** — the binary on `PATH`, the
  built artifact, the deployed route. Writing this skill, `uv` was absent from a
  restricted shell where the installed binary was present; a live run that
  depended on `uv` would have been a harness check wearing a costume.

Then assert the output, not just the exit code. `&& test -s <the artifact>` or a
one-line check of a real field. **Confirm the field names you assert actually
exist** — an assertion against an invented key passes for the wrong reason or
fails for the wrong reason, and both waste a session.

**If you genuinely cannot name one, write `live_run: ""` and say so out loud.**
The loop will keep working and will label every result HARNESS-PROVEN and name
the missing run in every report. That is the honest outcome. Inventing a
plausible-looking `live_run` that is actually a test invocation is the single
worst thing you can do in this file — it turns the loop's headline claim into a lie.

## Step 4 — Rubrics: what may the gate block on?

The gate can only block on a **named clause in a named document.** Everything
else is a non-blocking preference. So find the documents that carry this repo's
actual laws:

```bash
ls CONTRIBUTING.md ARCHITECTURE.md docs/*.md .github/CONTRIBUTING.md 2>/dev/null
```

Always include the buildloop doctrine. Add any repo document that states rules
rather than describing structure — a layering rule, an ownership boundary, a "we
never do X" section. **A README that only describes the project is not a rubric;
listing it just gives the gate something to hallucinate clauses from.**

If there are no rubrics beyond the doctrine, say so plainly. The loop still runs;
the gate is simply narrower.

## Step 5 — Runtime: is there a running process at all?

Set `runtime.enabled: true` only if something is deployed and running. A library
or CLI has no runtime and the check should be off — an agent forced to check a
runtime that doesn't exist will invent one.

If there is one, fill in `process_manager`, `service`, `config_file` and
`config_prefix`. The agent needs `config_prefix` so it can compare config keys
**by name** without ever printing a value.

## Step 6 — Known traps: ask, don't infer

You cannot derive this section. Ask the user, in one batched round:

> Three questions, then I'll write the file:
> 1. What in this repo **looks dead but isn't** — something an agent would
>    reasonably delete or ignore that is actually load-bearing?
> 2. What has **no safety net** — a file, table or path where a mistake is not
>    recoverable from git?
> 3. What bites **every** newcomer here — the thing you always end up explaining?

Write their answers down verbatim. This section is the highest-value part of the
file and the only part that gets better with age.

## Step 6b — The vocabulary. Extract it; never invent it.

The loop knows how to *test* a project long before it knows how to *talk* about
one. That gap has a cost: the read-back gate asks the human to spot "a field name
you never wrote," which is a manual eyeball job every single time. **A vocabulary
sheet turns that into a lookup.**

Build it from the repo's own prose:

```bash
# the documents that define terms, not the ones that describe structure
git ls-files '*.md' | grep -viE 'translations/|CHANGELOG|LICENSE' | head -20
```

Read them and pull out the terms **this project uses for its own concepts** — the
nouns that appear in its docs, its CLI, its config keys and its error messages.
Not general programming words. The ones where a stranger would guess wrong.

**Every entry carries the file and line it came from.** A term you cannot cite is
a term you invented, and a glossary that quietly invents entries is the exact
disease this whole system exists to treat. Mark provenance honestly:

| grade | means | may the gate block on it |
|---|---|---|
| `MEASURED` | the term is defined or used in a cited file:line | yes |
| `INFERRED` | you worked it out from naming or context | **no** — it is a lead, not a definition |

If the repo has a knowledge graph (`graphify-out/graph.json` or similar), use it —
node labels are extracted from source with provenance already attached, which
beats reading prose and guessing. If it does not, read the docs and cite lines.

Write the result into `.buildloop.md` as a `## Vocabulary` section. Cap it at
roughly 20 terms: a glossary nobody reads is worse than none, and the long tail is
where the invented entries hide.

**Ask the user to correct it before you write.** You are proposing a vocabulary
for their project; they are the authority on what their words mean.

## Step 7 — Run every command, THEN write

### 🔴 Step 7a — the preflight. Run all four. Do not skip one because it "obviously works".

Before you write a single field, **execute every command you are about to record**
and keep the real output. Not `install` only. Not `live_run` only. All four.

```bash
<commands.install>     # then: echo "install exit=$?"
<commands.test>        # then: echo "test exit=$?"
<commands.lint>        # then: echo "lint exit=$?"
<commands.live_run>    # then: echo "live_run exit=$?"
```

A command that is not installed is **`absent`**, never `ok`. A command that fails
is **`FAILED`** with its output. Neither is a reason to stop — they are facts the
loop must carry, and a build report that says "lint passed" when the linter was
never installed is the exact lie this whole system exists to prevent.

**Three things this catches every time, and each one has already bitten:**

- **The tool isn't there.** `uv`, `poetry`, `bandit` — declared in CI, absent on
  this machine. The loop would run `uv run pytest` forever and report nothing.
- **The live run tests the wrong tree.** An installed binary imports its own
  copy from `site-packages`, not your source. It will pass happily while
  containing none of your build. **Assert which file it executes** —
  `python -c "import <pkg>; print(<pkg>.__file__)"` or the language's equivalent —
  and record that path.
- **A test suite that writes into the repo.** Run it twice and diff the tree. If
  the suite mutates tracked files, every future scope fence that protects them is
  a fence the loop itself will breach.

### Step 7b — show the gaps

```
DETECTED
  language        python            ← pyproject.toml:1
  trunk           origin/main       ← git symbolic-ref
  test            pytest -q         ← .github/workflows/ci.yml:31
  exclude         vendor/, dist/    ← .gitignore

PREFLIGHT — every command below was RUN just now
  install         ok
  test            ok: 3644 passed, 20 failed (pre-existing, recorded)
  lint            absent: bandit not installed
  live_run        ok: "5 nodes 7 edges", exit 0
                  executes: /usr/local/lib/python3.14/site-packages/pkg/__init__.py

COULD NOT DETERMINE — these become TODO in the file
  runtime         ← nothing deployed found

NEEDS YOU
  known traps     ← the 3 questions above
```

### Step 7c — write it, stamped

Write `.buildloop.md` from `templates/buildloop.config.md`. **Fill the `generated:`
block with what Step 7a actually produced**, and set `by: buildloop-init`.

**You may only write `by: buildloop-init` if you personally ran the preflight in
this session.** If you assembled the file any other way — copied an example,
adapted another repo's, wrote it from the user's description — write `by: hand`.
`/buildloop-plan` and `/buildloop-build` refuse to run against `by: hand`, and
that refusal is the point: it is what stops a loop from trusting commands nobody
has ever executed.

Then tell them:

```
✅ .buildloop.md written — <n> fields set, <m> TODO
   Preflight: <k> ok · <f> failed · <a> absent   (all recorded in the file)

Next:  /buildloop-plan <what you want built>

⚠️ <if live_run is empty>  This loop cannot say LIVE-PROVEN until
   commands.live_run is set. Every report will name that gap.
⚠️ <per absent/failed command>  <name> is <absent|failing>. Every build report
   will carry it as UNRUN — it will never be reported as passed.
```

**Add `.buildloop.md` to git**, not to `.gitignore`. It is a shared description
of the project, and the whole point is that the next person's loop reads the same
one. If it must hold anything private, put a path in it, never a value.

## Rules

- Never invent a command you did not find. An empty field makes an agent ask; a
  wrong field makes it run the wrong thing and report the result as real.
- Never write a secret, token or host password into this file. Paths and key
  names only.
- Never silently overwrite an existing `.buildloop.md`.
- Cite the file you detected each value from. The user should be able to check you.
