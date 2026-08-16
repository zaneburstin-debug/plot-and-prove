---
# .buildloop.md — written by /buildloop-init. Every "← " is the file a value was read from.
# Fields you leave empty make an agent ASK. Fields you guess make an agent run the
# wrong thing and report the result as real. Leave it empty rather than guess.

repo: <absolute path>
trunk: <origin/main>                # ← git symbolic-ref refs/remotes/origin/HEAD
                                    #   Detect this. A loop comparing against the
                                    #   wrong trunk reports phantom commits.
language: <detected>                # ← the manifest file it came from

# 🔴 PROVENANCE — the loop reads this block and refuses to run without it.
# `by: buildloop-init` may ONLY be written by an init run that actually EXECUTED
# every command in `commands:` below and recorded the real result. A config that
# was hand-written, copied from another repo, or assembled from an example is
# `by: hand`, and the loop will refuse until init has run.
generated:
  by: buildloop-init                # buildloop-init | hand
  date: <YYYY-MM-DD>
  preflight:                        # each line = a command that was RUN, not assumed
    install:  <ok | FAILED: <output> | skipped: <why>>
    test:     <ok: <n passed, m failed> | FAILED: <output> | skipped: <why>>
    lint:     <ok | FAILED: <output> | absent: <tool not installed>>
    live_run: <ok: "<real output>", exit 0 | FAILED: <output>>
  # If a preflight line is FAILED or absent, that is not a blocker — it is a fact
  # every build report must carry. An unrunnable check is UNRUN, never passed.

exclude:                            # ← the repo's own declared non-source dirs
  - <dir>/

do_not_edit:
  - path: <lockfile>
    owner: <who or what owns it>
    reason: <how it is regenerated instead>

rubrics:                            # what the gate may BLOCK on. A named clause in
  - path: <doc>                     # one of these files is the only blocking violation.
    checks: <what this document governs>

docs_dir: ./build-docs

commands:
  install: <>                       # ← CI workflow
  test: <>                          # ← CI workflow
  lint: <>                          # ← CI workflow
  typecheck: ""                     # empty on purpose if CI has none.
                                    #   An invented command is worse than a missing one.

  # 🔴 THE ONE REAL RUN. Not the test command.
  # It must invoke what a USER touches: the installed binary, the deployed route,
  # the built artifact — NOT the source tree through a dev tool.
  # `uv run`/`npm run`/`poetry run` reach the source tree via a tool that may not
  # exist where the code actually runs. Prefer the installed entry point.
  # A library's live run imports the INSTALLED package, not the source directory.
  live_run: >
    <command> && test -s <the artifact it must produce> && <assert the content>

runtime:
  enabled: <true|false>             # false for a CLI/library with nothing deployed.
                                    #   true forces bl-runtime to invent a process
                                    #   just to have something to report.

progress_hook: ""                   # optional: a command run after each requirement
graph: auto
---

# <project name>

## What this project is

<Two or three sentences. What it does, who runs it, and the one promise it makes
that must never break.>

## The gate's project questions

<This is this repo's north star. The gate blocks on these. Write the questions
whose wrong answer would be unacceptable here — not generic ones.>

1. **What READS this back, and when?**
2. <a question specific to this project's core promise>
3. **Flag name? Default OFF? Flag-off byte-identical — asserted, not assumed?**
4. <what happens to data/artifacts written by the previous version?>
5. **Blast radius if wrong. Reversible? The one live run?**

## Vocabulary

<This project's own words for its own concepts. Every entry cites where it came
from. `MEASURED` = defined or used at that file:line. `INFERRED` = worked out
from context — a lead, never a definition, and the gate may not block on it.

Used by /buildplan (write in these words, do not invent synonyms), by the gate
(a design naming a concept that is in neither this table nor the code graph is
inventing), and by /proofcheck Step 0.>

| term | what this project means by it | grade | source |
|---|---|---|---|
| `<term>` | `<one line>` | MEASURED | `<file>:<line>` |

## Known traps

<Verbatim answers to init's three questions. This section cannot be detected and
it is the only part of this file that gets better with age.>

- <what looks like it works but does not>
- <what has no safety net>
- <what bites every newcomer>

## Ownership

<Who owns what. Anything owned by someone else is a PR proposal, never a direct edit.>
