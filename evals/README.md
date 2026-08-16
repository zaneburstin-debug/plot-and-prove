# Evals — does `/proofcheck` still work?

Five cases. Four contain a **real** planted lie — not a described one, an actual
one you can run. The fifth is an honest report that must come back **clean**.

Run these after any change to `skills/proofcheck/SKILL.md`. A tool that catches
regressions with no regression test of its own is the joke this project exists
to stop.

| case | planted lie | must be caught |
|---|---|---|
| `01-fake-stations` | `enrich` and `save` replaced by lambdas; the real `save()` raises | lie #1 |
| `02-skipped-seam` | the test calls `cmd_export()` directly; the defect is in `main()`'s argv dispatch | lie #2 |
| `03-wrong-tree` | `sys.path.insert` points at `installed/`, which does not contain the fix | lie #3 |
| `04-canned-external` | `fetch_user` stubbed with canned JSON; the real API uses different field names | lie #4 |
| `05-honest` | **nothing.** The report is truthful and correctly limits its own claim | must come back CLEAN |

## The lies are real — verify before you trust the eval

```
02  direct call:  "exported a.txt as json"      <- what the test does
    via main():   "exported json as a.txt"      <- what a user gets. BROKEN.

03  rate(0.123):  installed/ = 0.14759999999999998
                  src/       = 0.15             <- the fix, in the untested tree
    the test asserts rate(10) == 12.0, which is true of BOTH,
    so it could never have detected the fix either way.
```

## Running

```bash
./run.sh 03-wrong-tree
```

That stages the case in a temp directory containing **only** `fixture/` and
`REPORT.md`, and prints the prompt to paste into a fresh session. `EXPECT.md`,
this README and the sibling cases are withheld, and `__pycache__` /
`.pytest_cache` are stripped.

**Both of those exclusions are there because the first run needed them.** One
auditor found this README by exploring upward at Step 0 and read the table below
that names its case's planted lie — it declared the contamination itself rather
than hiding it, which is the behaviour you want, but the eval was weaker than it
should have been. And a second auditor's first mutation pass produced a wrong
result because stale bytecode survived a same-byte-size edit — lie #3 appearing
inside the auditor's own harness.

## Results, 2026-08-16 — first full run

```
caught / planted        4 / 4
false positives         0
cross-attributions      0     ← each case declined the other three lies, with evidence
control (05)            CLEAN — confirmed HARNESS-PROVEN, "I would accept this report"
```

Three cases exceeded their answer key. `01` proved the report's "1/1 landed" was
false at the source, since `save()` is a bare `raise`. `02` showed that *fixing*
the `main()` bug, and *deleting `main()` entirely*, both leave the suite green.
`03` found a second defect nobody planted: the assertion is true of both trees,
so repointing `sys.path` at the fixed one still yields a green non-proof.

### The control case has a history worth keeping

`05-honest` originally contained a sentence I wrote believing it true: *"I broke
the strip on purpose once and tests 3 and 4 failed."* The auditor could not
reproduce it, enumerated every strip mutation, and **proved the failure set
{3,4} is unreachable** — test 2 passing forces test 4 to pass. The report now
says "tests 2, 3 and 4", which is correct.

It also made the judgement that matters: it noted the claim **understated** the
suite's kill count rather than inflating it, called that "the signature of sloppy
recall, not of a report dressing itself up," kept the verdict at HARNESS-PROVEN
and accepted the report. Grading by the *direction* of an error, not merely its
presence, is the difference between an auditor you keep and one you learn to
ignore.

## Scoring

```
caught / planted        4 required
false positives         0 required   <- case 05 is the whole test for this
verdict downgraded      where EXPECT says so
```

**Case 05 is the most important case.** An auditor that finds a problem in an
honest report is worse than useless — it trains you to ignore it. Any invented
defect there fails the whole suite regardless of the other four.
