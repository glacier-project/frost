"""Expected commits of TestFrostFmu, one table per scenario.

Every entry is (LF time in ms, value of the watched output); the value is None
when a scenario watches no output and only checks the tags.
"""

INPUT = "Float64_continuous_input"

# Feedthrough, 100 ms step, with triggers: output == input from the very tag of
# each change.
ROLLBACK_EXPECTED = [
    (0, 0.0),
    (100, 0.0),
    (200, 0.0),
    # input -> 5 at 250 ms: rollback to 200, replay to 250, commit.
    (250, 5.0),
    # Second trigger at 250 ms: inputs written again, committed again.
    (250, 5.0),
    (300, 5.0),
    (400, 5.0),
    # Regular commit at 500 ms, before the change.
    (500, 5.0),
    # input -> 7 at 500 ms: rollback of the step ahead, commit.
    (500, 7.0),
    (600, 7.0),
    (700, 7.0),
    (800, 7.0),
    (900, 7.0),
    (1000, 7.0),
]

# Feedthrough, 1 s step: the trigger at 500 ms falls in the middle of the
# doStep 0 -> 1000 ms the FMU has already simulated.
HALF_STEP_EXPECTED = [(0, 0.0), (500, 5.0), (1000, 5.0)]

# Same changes as ROLLBACK_EXPECTED without triggers: each one only enters the
# step simulated at the next tick.
LATE_EXPECTED = [
    (0, 0.0),
    (100, 0.0),
    (200, 0.0),
    # The 250 ms change is not in the 200 -> 300 step, already simulated.
    (300, 0.0),
    (400, 5.0),
    (500, 5.0),
    # The 500 ms change is not in the 500 -> 600 step, already simulated.
    (600, 5.0),
    (700, 7.0),
    (800, 7.0),
    (900, 7.0),
    (1000, 7.0),
]

# BouncingBall FMI 2.0, 70 ms step, no outputs, cannot roll back: every 70 ms
# plus the trigger at 250 ms.
NO_STATE_EXPECTED = sorted(
    [(ms, None) for ms in range(0, 1001, 70)] + [(250, None)]
)

# BouncingBall FMI 3.0, 100 ms step, early return: the bounce at 453 ms and the
# zero crossing back at 454 ms become tags of their own. The value is where the
# ball goes: at 453 ms the event is settled, so the ball already rises.
EARLY_RETURN_EXPECTED = [
    (0, "still"),
    (100, "falling"),
    (200, "falling"),
    (300, "falling"),
    (400, "falling"),
    (453, "rising"),
    (454, "rising"),
    (500, "rising"),
    (600, "rising"),
    (700, "rising"),
    (800, "falling"),
    (900, "falling"),
    (1000, "falling"),
]


# EarlyReturnNoRollback (value = integral of rate), 500 ms step, cannot roll
# back, returns early every 250 ms: LF has already passed those instants, so
# they split the steps but get no tag. The trigger at 600 ms steps 500 -> 600
# with rate 1, then rate 2 holds: 0.6 + 2 * 0.4 at 1000 ms.
NO_ROLLBACK_EARLY_EXPECTED = [(0, 0.0), (500, 0.5), (600, 0.6), (1000, 1.4)]


def _controller_tags() -> list[int]:
    """Return the tags of TriggerEventFmu, in ms.

    Enabled at 5 model s, the controller cycles through phases of 2, 10 and 3
    model s; at 100 model s per LF s each model s is 10 ms. The 200 ms step
    tags come on top.

    Returns:
        list[int]:
            Sorted tags in ms, the trigger at 50 ms included.

    """
    events, t = [], 5.0
    for duration in [2, 10, 3] * 20:
        t += duration
        if t > 100:
            break
        events.append(round(t * 10))
    return sorted({0, 50, *events, *range(0, 1001, 200)})


# TrafficController, 20 model s step at 100 model s per LF s, so 200 ms tags.
# It starts disabled, with no phase change; the trigger at 50 ms enables it,
# and the phase changes it then makes at 7, 17, 20, 22, 32 ... model s must be
# tags at once, not wait for the next 200 ms tag.
TRIGGER_EVENT_EXPECTED = [(ms, None) for ms in _controller_tags()]

# TrafficController enabled from the start: the run ahead finds the phase
# change at 2 model s (20 ms). The trigger at 10 ms disables it, so that event
# no longer exists and the tick left at 20 ms must not commit.
STALE_TICK_EXPECTED = [(ms, None) for ms in (0, 10, 200, 400, 600, 800, 1000)]

# Feedthrough starting at 1e9 model s, where a float keeps only about 0.1 us:
# the tags stay exact, and the trigger at 250 ms is applied at 250 ms.
BIG_START_EXPECTED = [
    (0, 0.0),
    (100, 0.0),
    (200, 0.0),
    (250, 5.0),
    (300, 5.0),
    (400, 5.0),
    (500, 5.0),
    (600, 5.0),
    (700, 5.0),
    (800, 5.0),
    (900, 5.0),
    (1000, 5.0),
]

# TrafficController enabled from the start, with terminate_after 30 model s: the
# phase changes at 2, 12, 15, 17, 27 model s, then the FMU terminates at 30 and
# no tag follows.
TERMINATE_EXPECTED = [
    (ms, None) for ms in (0, 20, 120, 150, 170, 200, 270, 300)
]

# Feedthrough with start value 1.5 and YAML stop_time 0.35 s: nothing after the
# last step before 350 ms.
STOP_EXPECTED = [(0, 1.5), (100, 1.5), (200, 1.5), (300, 1.5)]
