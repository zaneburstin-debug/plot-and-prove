# BUILD REPORT — slugify()

Requirements: 1/1 landed.
Proof: HARNESS-PROVEN — 4 unit tests call the real `slugify` function directly.
No stubs, no mocks, no path manipulation. The regex and the trailing `strip("-")`
are both load-bearing: I changed the substitution character on purpose once and
all four went red, and removing the final strip fails tests 2, 3 and 4.

NOT PROVEN: this has never run inside the CLI that will call it. commands.live_run
is not defined for this fixture, so nothing here is LIVE-PROVEN and I am not
claiming it is.

THE ONE RUN THAT WOULD CLOSE IT: invoke the real CLI with a title argument and
read the slug it writes to disk.
