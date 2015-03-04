dupespotter
===========

Workflow:

1. `./dupespotter.py "http://example.com/url1" "http://example.com/url2"`
2. If there is no diff, the pages are detected as dupes.  If there is a
   diff but the pages should be detected as dupes, tweak `dupespotter.py`
   to remove the randomized or timestamped elements.
3. `mkdir tests/TESTNAME`
4. `cp cache/HASHURL1* tests/TESTNAME/`
5. `cp cache/HASHURL2* tests/TESTNAME/`
6. `./run_tests.py`
   
   There should be no diffs listed for any of the tests.

7. `git add dupespotter.py tests`
8. `git commit`
