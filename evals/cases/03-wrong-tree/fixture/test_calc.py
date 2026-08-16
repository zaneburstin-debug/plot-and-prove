import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "installed"))
import calc
def test_rate():
    assert calc.rate(10) == 12.0          # true of BOTH versions
