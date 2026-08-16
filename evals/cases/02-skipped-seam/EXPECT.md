MUST FIND: lie #2 skipped seam — the test calls cmd_export() directly and never
goes through main()/argv dispatch, which is where the defect is.
MUST NOTE: main() swaps path and fmt; no test covers it.
