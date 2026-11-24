import math
from loopmem.model import Lock, Scheduler, interval, strength, T0_DEFAULT, BETA

def test_first_multiplier_is_2_5():
    assert interval(2) / interval(1) > 2.4
    assert interval(2) / interval(1) < 2.6

def test_interval_grows():
    assert interval(1) < interval(2) < interval(5) < interval(9)

def test_recall_decays():
    l = Lock("x", c=1, t_last=0)
    assert l.recall(1) > l.recall(5) > l.recall(20)

def test_passes_increase_strength():
    l1, l2 = Lock("a", c=1), Lock("b", c=1)
    l2.passes(3, day=0)
    assert strength(l2.c) > strength(l1.c)

def test_evening_review_rescues_dying_locks():
    s = Scheduler()
    l = Lock("weak", c=1, t_last=0)
    day = int(interval(1)) + 3
    batch = s.evening_review([l], day, budget=10)
    assert l in batch and l.c == 2
