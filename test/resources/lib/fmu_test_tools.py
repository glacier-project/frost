"""Helpers shared by the FMU tests: aligned log lines, side-by-side comparisons and the story of an example."""

import logging


def ns(ms):
    """
    Convert milliseconds to the logical ns LF works with.

    Args:
        ms (float): Time in milliseconds.
    """
    return round(ms * 1_000_000)


def format_time(time_ns):
    """
    Format a logical time for the logs, in milliseconds.

    Args:
        time_ns (int): Logical time in ns.
    """
    ms = time_ns / 1e6
    return f"{ms:>9.0f} ms" if ms == int(ms) else f"{ms:>9.3f} ms"


def log_line(time_ns, kind, text):
    """
    Build one log line: time, event kind, description.

    Args:
        time_ns (int): Logical time in ns.
        kind (str): Short event kind, such as COMMIT or TRIGGER.
        text (str): What happened.
    """
    return f"{format_time(time_ns)} | {kind:<8} | {text}"


def show(value):
    """
    Format a value for the logs; floats keep 6 significant digits, the checks still compare the exact value.

    Args:
        value (Any): Value to show.
    """
    return f"{value:.6g}" if isinstance(value, float) else str(value)


def describe_trigger(now_ns, model_ns, restart_ns):
    """
    Say what a trigger has to do to bring the FMU to the current tag.

    Args:
        now_ns (int): Current LF tag in ns.
        model_ns (int): Tag the FMU sits on before the trigger.
        restart_ns (int | None): Tag of the state saved before the last step, where a rollback lands.
    """
    if model_ns > now_ns:
        replay = "" if restart_ns == now_ns else ", replayed up to now"
        return f"model was ahead at {model_ns // 1000000} ms: rolled back to {restart_ns // 1000000} ms{replay}"
    if model_ns < now_ns:
        return f"model was behind at {model_ns // 1000000} ms: stepped up to now"
    return "model already on this tag: inputs applied in place"


def describe_changes(previous, current):
    """
    Describe how a data-model snapshot differs from the previous one.

    Args:
        previous (dict | None): Previous snapshot, None for the first one.
        current (dict): Current snapshot, node path -> value.
    """
    if previous is None:
        return ", ".join(f"{key}={show(value)}" for key, value in current.items())
    changes = [f"{key} {show(previous[key])} -> {show(value)}" for key, value in current.items() if previous[key] != value]
    return ", ".join(changes) if changes else "no change"


def compare(logger, title, got, expected):
    """
    Log what a test recorded next to what it expected, one row per entry.

    Args:
        logger (logging.Logger): Logger of the reactor that runs the check.
        title (str): What is being compared.
        got (list): Recorded entries.
        expected (list): Expected entries.

    Returns:
        list[int]: Indexes of the rows that differ; empty when everything matches.
    """
    logger.info(f"=== {title}: {len(got)} recorded, {len(expected)} expected")
    mismatches = []
    for index in range(max(len(got), len(expected))):
        recorded = got[index] if index < len(got) else "(missing)"
        wanted = expected[index] if index < len(expected) else "(missing)"
        ok = index < len(got) and index < len(expected) and got[index] == expected[index]
        if not ok:
            mismatches.append(index)
        logger.info(f"    #{index:<3} got {str(recorded):<34} expected {str(wanted):<34} {'ok' if ok else '<-- MISMATCH'}")
    return mismatches


def story():
    """
    Return the logger that tells what happens in an example, one plain line per event.

    It has its own handler without the Frost prefix and does not propagate, so the reactors' own logs
    (set to WARNING in the example YAML) stay out of the way; set them to INFO or DEBUG for the internals.
    """
    logger = logging.getLogger("story")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(logging.INFO)
    return logger


def tell(time_ns, who, text):
    """
    Write one line of the story: LF time in seconds, who, what happened.

    Args:
        time_ns (int): LF logical time in ns.
        who (str): Who acts, such as "north light".
        text (str): What happened.
    """
    story().info(f"{time_ns / 1e9:>9.3f} s | {who:<16} | {text}")


def tell_header(title):
    """
    Open the story with a title and the column names.

    Args:
        title (str): What the example shows.
    """
    story().info(f"\n{title}\n{'LF time':>11} | {'who':<16} | what happened\n{'-' * 11}-+-{'-' * 16}-+-{'-' * 50}")


def how_the_input_was_applied(now_ns, model_ns):
    """
    Say in a few words how an input written at now reached the FMU.

    Args:
        now_ns (int): LF tag of the write, in ns.
        model_ns (int): Tag the FMU sat on when the input was written.
    """
    if model_ns > now_ns:
        return f"the FMU had simulated ahead to {model_ns / 1e9:g} s: rolled back"
    if model_ns < now_ns:
        return f"the FMU was at {model_ns / 1e9:g} s: stepped up to now"
    return "the FMU was on this tag"
