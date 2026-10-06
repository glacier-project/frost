"""FMUs stepped together as one model: the engine of FrostFmu."""

import logging
from graphlib import CycleError, TopologicalSorter
from typing import Any

from fmpy.fmi1 import FMICallException
from fmpy.fmi2 import fmi2Discard
from fmpy.model_description import DefaultExperiment
import numpy as np

from loader import BUILD_LOCK, open_fmu

# Kind of an FMI 2.0 / 3.0 type; every other type is an integer (Integer,
# Int8 ... UInt64, Enumeration).
_KIND = {
    "Real": "float",
    "Float32": "float",
    "Float64": "float",
    "Boolean": "Boolean",
    "String": "String",
    "Binary": "Binary",
}


class FmuGroup:
    """FMUs on one model time, coupled output -> input.

    Variables are named "<member>.<variable>". Whenever every member sits on
    the same time, each connection copies its output into its input (Jacobi):
    the step from t uses the outputs every member had at t. The copies follow
    the feedthrough of the ModelStructure, upstream first, so a chain of
    direct feedthrough settles at the same instant. In an algebraic loop the
    connection listed first is the tear: with the "fixed_point" policy the
    exchange is repeated until the tear values settle (Gauss-Seidel, with
    relaxation); with "delay" the tear takes the value its output had at the
    previous communication point, its own start value at the first one.

    The members that can save their state (ahead) step first and may run
    ahead of LF; an early return of one of them stops all of them there. The
    others (lazy) step only in catch_up(), up to where the ahead ones stopped,
    and an early return just splits their step.

    Attributes:
        members (dict[str, FMU2Frost | FMU3Frost]):
            Member name -> initialized FMU, in Step Mode.
        variables (dict[str, tuple[str, ModelVariable]]):
            Dotted name -> (member, fmpy ModelVariable); no Clocks.
        connections (list[tuple[str, str]]):
            (output, input) dotted names.
        depends (dict[str, set[str]]):
            Dotted output -> dotted inputs of its member it depends on at the
            same instant; every input when the ModelStructure says nothing.
        order (list[tuple[str, str]]):
            Connections copied at the same instant, upstream first.
        tears (list[tuple[str, str]]):
            One connection per algebraic loop, where the loop is cut.
        policy (str):
            "fixed_point" or "delay".
        ahead (list[str]):
            Members that can save and restore their state.
        lazy (list[str]):
            Members that cannot.
        step_size (float | None):
            Smallest DefaultExperiment stepSize among the members.
        time (float):
            Model time the ahead members sit on.
        lazy_time (float):
            Model time the lazy members sit on; never past time.
        saved (dict[str, tuple[Any, float | None]]):
            Ahead member -> (FMU state, next_event_time) before the last step.
        saved_time (float | None):
            Time of the saved states.

    """

    def __init__(
        self,
        fmus: dict[str, str],
        connections: list[list[str]],
        start_values: dict[str, Any],
        tolerance: float | None,
        start_time: float | None,
        stop_time: float | None,
        logger: logging.Logger,
        *,
        dotted: bool = True,
        policy: str = "fixed_point",
        abs_tolerance: float = 1e-9,
        rel_tolerance: float = 1e-6,
        relaxation: float = 1.0,
        max_iterations: int = 100,
    ) -> None:
        """Open and initialize every member, then copy the connections.

        Args:
            fmus (dict[str, str]):
                Member name -> FMU archive path; names hold no ".".
            connections (list[list[str]]):
                [output, input] pairs of dotted names.
            start_values (dict[str, Any]):
                Values written in Initialization Mode, keyed by dotted name.
            tolerance (float | None):
                Relative tolerance; None takes each FMU DefaultExperiment.
            start_time (float | None):
                Model time the simulation starts at; None takes the earliest
                DefaultExperiment startTime, 0 when none declares one.
            stop_time (float | None):
                Model time the simulation stops at; None for no limit.
            logger (logging.Logger):
                Logger of the owning reactor.
            dotted (bool):
                False for a single member whose variables keep their own
                names, without "<member>.".
            policy (str):
                Algebraic loops: "fixed_point" or "delay".
            abs_tolerance, rel_tolerance (float):
                A tear has settled when |new - old| <= abs_tolerance +
                rel_tolerance * |new|; values that are not numbers must be
                equal.
            relaxation (float):
                In (0, 1]: the next tear value is old + relaxation * (new -
                old); numbers that are not floats are never relaxed.
            max_iterations (int):
                Iterations per exchange before the loop is reported as not
                converging.

        """
        if policy not in ("fixed_point", "delay"):
            raise ValueError(f"unknown algebraic loop policy {policy!r}")
        if not 0 < relaxation <= 1 or max_iterations < 1:
            raise ValueError(
                "relaxation must be in (0, 1], max_iterations >= 1"
            )
        self.policy, self.relaxation = policy, relaxation
        self.abs_tolerance, self.rel_tolerance = abs_tolerance, rel_tolerance
        self.max_iterations = max_iterations
        if not dotted and len(fmus) != 1:
            raise ValueError("names without '<member>.' need a single FMU")
        if bad := [name for name in fmus if "." in name]:
            raise ValueError(f"member names {bad} must not contain '.'")
        if dotted and (
            unknown := {n.split(".", 1)[0] for n in start_values} - set(fmus)
        ):
            raise KeyError(f"start_values name unknown members {unknown}")
        self.members = {}
        self.variables = {}
        self.depends = {}
        self._delay_history = {}
        self.connections = [tuple(pair) for pair in connections]
        self.ahead, self.lazy = [], []
        self.saved, self.saved_time = {}, None
        self.logger = logger
        try:
            with BUILD_LOCK:
                descriptions = {}
                for member, path in fmus.items():
                    self.members[member], descriptions[member] = open_fmu(
                        path, member
                    )
                experiments = {
                    member: description.defaultExperiment or DefaultExperiment()
                    for member, description in descriptions.items()
                }
                if start_time is None:
                    start_time = min(
                        (
                            float(e.startTime)
                            for e in experiments.values()
                            if e.startTime
                        ),
                        default=0.0,
                    )
                self.start_time = start_time
                self.time = self.lazy_time = start_time
                for member, fmu in self.members.items():
                    self._add_member(
                        member,
                        fmu,
                        descriptions[member],
                        f"{member}." if dotted else "",
                        start_values,
                        tolerance or experiments[member].tolerance,
                        stop_time,
                    )
            steps = [
                float(e.stepSize) for e in experiments.values() if e.stepSize
            ]
            if tolerance is None and not dotted:
                declared = next(iter(experiments.values())).tolerance
                tolerance = float(declared) if declared else None
            self.tolerance = tolerance
            self.step_size = min(steps, default=None)
            self._check_connections()
            self._plan()
            self._delay_start = {(s, d): self.read(d) for s, d in self.tears}
            self.exchange()
        except Exception:
            try:
                self.close(terminate=False)
            except Exception:
                self.logger.exception("cannot close the members")
            raise

    def _add_member(
        self,
        member: str,
        fmu: Any,
        description: Any,
        prefix: str,
        start_values: dict[str, Any],
        tolerance: Any,
        stop_time: float | None,
    ) -> None:
        """Initialize one opened member and register its variables.

        Args:
            member (str):
                Member name.
            fmu (FMU2Frost | FMU3Frost):
                The member, as open_fmu() returns it.
            description (ModelDescription):
                Its model description.
            prefix (str):
                "<member>." or "" before its variable names.
            start_values (dict[str, Any]):
                Values of the whole group, keyed by prefixed name.
            tolerance (float | str | None):
                Relative tolerance for this member.
            stop_time (float | None):
                Model time the simulation stops at.

        """
        can_save = description.coSimulation.canGetAndSetFMUstate
        (self.ahead if can_save else self.lazy).append(member)
        fmu.initialize(
            {
                name.removeprefix(prefix): value
                for name, value in start_values.items()
                if name.startswith(prefix)
            },
            None if tolerance is None else float(tolerance),
            self.start_time,
            stop_time,
        )
        variables = [v for v in description.modelVariables if v.type != "Clock"]
        self.variables.update((prefix + v.name, (member, v)) for v in variables)
        inputs = {prefix + v.name for v in variables if v.causality == "input"}
        self.depends.update(
            (prefix + v.name, inputs)
            for v in variables
            if v.causality == "output"
        )
        for unknown in description.outputs:
            if unknown.dependencies is not None:
                self.depends[prefix + unknown.variable.name] = {
                    prefix + v.name
                    for v in unknown.dependencies
                    if v.causality == "input"
                }

    def _check_connections(self) -> None:
        """Reject a connection that is not output -> input, or a double input.

        Raises:
            KeyError:
                A name is not a variable with the needed causality.
            ValueError:
                Two connections drive the same input, or the two ends differ
                in kind (float, integer, Boolean, String, Binary) or shape.

        """
        inputs = [dst for _, dst in self.connections]
        for src, dst in self.connections:
            for name, causality in ((src, "output"), (dst, "input")):
                if (
                    name not in self.variables
                    or self.variables[name][1].causality != causality
                ):
                    raise KeyError(f"{name!r} is not an {causality}")
            if inputs.count(dst) > 1:
                raise ValueError(f"{dst!r} is driven by several connections")
            out, inp = self.variables[src][1], self.variables[dst][1]
            if _KIND.get(out.type, "integer") != _KIND.get(inp.type, "integer"):
                raise ValueError(
                    f"{src!r} is {out.type} but {dst!r} is {inp.type}"
                )
            if tuple(out.shape or ()) != tuple(inp.shape or ()):
                raise ValueError(
                    f"{src!r} has shape {out.shape} but {dst!r} {inp.shape}"
                )

    def _plan(self) -> None:
        """Order the connections by feedthrough; tear one per algebraic loop.

        A connection follows every connection that writes an input its output
        depends on. In a loop the connection listed first is the tear: it no
        longer waits for the others, and a warning names the loop.
        """
        after = {
            (src, dst): {
                c for c in self.connections if c[1] in self.depends[src]
            }
            for src, dst in self.connections
        }
        self.tears = []
        while True:
            try:
                order = list(TopologicalSorter(after).static_order())
                break
            except CycleError as error:
                loop = error.args[1][:-1]
                chosen = min(loop, key=self.connections.index)
                self.logger.warning(
                    "algebraic loop "
                    + ", ".join(f"{src} -> {dst}" for src, dst in loop)
                    + f": torn at {chosen[0]} -> {chosen[1]}, "
                    + (
                        "solved by fixed-point iteration"
                        if self.policy == "fixed_point"
                        else "which takes the value of the previous "
                        "communication point"
                    )
                )
                self.tears.append(chosen)
                after[chosen] = set()
        self.order = [c for c in order if c not in self.tears]

    @property
    def inputs(self) -> list[str]:
        """Dotted names of the inputs that no connection drives."""
        driven = {dst for _, dst in self.connections}
        return [
            name
            for name, (_, v) in self.variables.items()
            if v.causality == "input" and name not in driven
        ]

    @property
    def outputs(self) -> list[str]:
        """Dotted names of every output."""
        return [
            name
            for name, (_, v) in self.variables.items()
            if v.causality == "output"
        ]

    @property
    def next_event_time(self) -> float | None:
        """Earliest time event a member announced after time, or None."""
        return min(
            (
                fmu.next_event_time
                for fmu in self.members.values()
                if fmu.next_event_time is not None
                and fmu.next_event_time > self.time
            ),
            default=None,
        )

    def read(self, name: str) -> Any:
        """Read one variable by dotted name.

        Args:
            name (str):
                "<member>.<variable>".

        Returns:
            Any:
                The value, as the member FMU returns it.

        """
        member, variable = self.variables[name]
        return self.members[member].read(variable)

    def write(self, name: str, value: Any) -> None:
        """Write one variable by dotted name.

        Args:
            name (str):
                "<member>.<variable>".
            value (Any):
                Value to write.

        """
        member, variable = self.variables[name]
        self.members[member].write(variable, value)

    def exchange(self) -> None:
        """Copy every connection output into its input at time.

        Without loops: once, upstream first. With "fixed_point" the copies are
        repeated, starting from the tear inputs as they are, until every tear
        settles. With "delay" the tears are written first, with the value
        their output had at the last communication point before time (their
        start value at the first). Exchanging again at the same time, as
        after a rollback, gives the same values.

        Raises:
            RuntimeError:
                A loop does not settle within max_iterations.

        """
        if self.policy == "delay" or not self.tears:
            self._exchange_delayed()
            return
        for _ in range(self.max_iterations):
            old = [self.read(dst) for _, dst in self.tears]
            for src, dst in self.order:
                self.write(dst, self.read(src))
            new = [self.read(src) for src, _ in self.tears]
            if all(map(self._settled, old, new)):
                return
            for (_, dst), a, b in zip(self.tears, old, new, strict=True):
                self.write(dst, self._relax(a, b))
        raise RuntimeError(
            f"algebraic loop torn at {self.tears} does not settle in "
            f"{self.max_iterations} iterations at {self.time}: last values "
            f"{old} -> {new}"
        )

    def _exchange_delayed(self) -> None:
        """Exchange with the tears delayed by one communication point."""
        past = max(
            (t for t in self._delay_history if t < self.time), default=None
        )
        previous = (
            self._delay_start if past is None else self._delay_history[past]
        )
        for src, dst in self.tears:
            self.write(dst, previous[src, dst])
        for src, dst in self.order:
            self.write(dst, self.read(src))
        self._delay_history = {
            **({past: previous} if past is not None else {}),
            self.time: {c: self.read(c[0]) for c in self.tears},
        }

    def _settled(self, old: Any, new: Any) -> bool:
        """Whether a tear moved within the tolerances.

        Args:
            old (Any):
                Tear input before the iteration.
            new (Any):
                Tear output after it.

        Returns:
            bool:
                Numbers and arrays within the tolerances; anything else equal.

        """
        if isinstance(new, bool) or not isinstance(
            new, (int, float, np.number, np.ndarray)
        ):
            return old == new
        return bool(
            np.allclose(
                new, old, rtol=self.rel_tolerance, atol=self.abs_tolerance
            )
        )

    def _relax(self, old: Any, new: Any) -> Any:
        """Next tear value: relaxed for floats, new for anything else.

        Args:
            old (Any):
                Tear input before the iteration.
            new (Any):
                Tear output after it.

        Returns:
            Any:
                old + relaxation * (new - old), or new.

        """
        is_float = isinstance(new, (float, np.floating)) or (
            isinstance(new, np.ndarray) and new.dtype.kind == "f"
        )
        return old + self.relaxation * (new - old) if is_float else new

    def step(self, to: float) -> bool:
        """Save the ahead members, then step them from time towards to.

        An early return at t makes t the new target: the members already past
        it are restored and stepped again, up to t. time becomes where they
        all stop. No exchange: the lazy members are still behind.

        Args:
            to (float):
                Model time to reach.

        Returns:
            bool:
                True while every ahead member can continue after the step
                that stands; a step undone by a restore does not count.

        """
        for member in self.ahead:
            fmu = self.members[member]
            if member in self.saved:
                fmu.freeFMUState(self.saved[member][0])
            self.saved[member] = (fmu.getFMUState(), fmu.next_event_time)
        self.saved_time = self.time
        at = dict.fromkeys(self.ahead, self.time)
        ok = dict.fromkeys(self.ahead, True)
        pending = list(self.ahead)
        while pending:
            member = pending.pop(0)
            reached, ok[member] = self._step_member(
                member, at[member], to, True
            )
            at[member] = reached
            if reached < to:
                to = reached
                for other in self.ahead:
                    if at[other] > to:
                        self._restore(other)
                        at[other] = self.time
                        if other not in pending:
                            pending.append(other)
        self.time = to
        return all(ok.values())

    def catch_up(self) -> bool:
        """Step the lazy members up to time, then exchange.

        Returns:
            bool:
                True while every lazy member can continue.

        """
        running = True
        for member in self.lazy:
            _, ok = self._step_member(member, self.lazy_time, self.time, False)
            running = running and ok
        self.lazy_time = self.time
        self.exchange()
        return running

    def rollback(self) -> bool:
        """Restore the ahead members to the states saved by the last step.

        As in FrostFmu, the time events they had announced are forgotten: a
        rollback comes before new inputs, which may move them.

        Returns:
            bool:
                True once restored; False when no state was saved.

        """
        if self.saved_time is None or not self.ahead:
            return False
        for member in self.ahead:
            self.members[member].setFMUState(self.saved[member][0])
        self.time = self.saved_time
        return True

    def _restore(self, member: str) -> None:
        """Restore one ahead member to its saved state, inputs unchanged.

        Its announced time event is restored too, since nothing moved it.

        Args:
            member (str):
                Ahead member name.

        """
        state, next_event_time = self.saved[member]
        fmu = self.members[member]
        fmu.setFMUState(state)
        fmu.next_event_time = next_event_time

    def _step_member(
        self,
        member: str,
        now: float,
        to: float,
        ahead: bool,
    ) -> tuple[float, bool]:
        """Step one member from now to to.

        Args:
            member (str):
                Member name.
            now (float):
                Model time it sits on.
            to (float):
                Model time to reach.
            ahead (bool):
                Stop at an early return and keep the state restorable;
                otherwise step on after it.

        Returns:
            tuple[float, bool]:
                Model time reached, and False once the member terminated or
                discarded its step.

        """
        fmu, stalls = self.members[member], 0
        while now < to:
            try:
                terminate, early = fmu.step(now, to - now, ahead)
            except FMICallException as error:
                if error.status != fmi2Discard:
                    raise
                self.logger.error(
                    f"{member} discarded the step from {now} to {to}"
                )
                return now, False
            stalls = stalls + 1 if early is not None and early <= now else 0
            if stalls > 3:
                raise RuntimeError(f"{member} makes no progress past {now}")
            now = to if early is None else early
            if terminate:
                self.logger.debug(f"{member} requested termination at {now}")
                return now, False
            if ahead:
                break
        return now, True

    def close(self, terminate: bool = True) -> None:
        """Free every member.

        Args:
            terminate (bool):
                Whether to terminate the members first.

        """
        errors = []
        for fmu in self.members.values():
            try:
                fmu.close(terminate)
            except Exception as error:
                errors.append(error)
        self.members = {}
        if errors:
            raise errors[0]
