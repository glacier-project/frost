"""Open FMUs for FrostFmu and FmuGroup."""

import shutil
import threading

import fmpy
from fmpy.model_description import ModelDescription

from fmi2 import FMU2Frost
from fmi3 import FMU3Frost

# LF may build several FMUs in parallel at startup: libxml2 schema parsing is
# not thread-safe, and fmpy changes the process-wide working directory while it
# loads a library. Hold it while opening and initializing.
BUILD_LOCK = threading.Lock()


def open_fmu(
    path: str,
    name: str,
) -> tuple[FMU2Frost | FMU3Frost, ModelDescription]:
    """Extract the archive and instantiate its Co-Simulation interface.

    Args:
        path (str):
            FMU archive path.
        name (str):
            Instance name the FMU logs under.

    Returns:
        tuple[FMU2Frost | FMU3Frost, ModelDescription]:
            The instantiated FMU and its model description.

    """
    unzipdir = fmpy.extract(path)
    try:
        description = fmpy.read_model_description(unzipdir)
        if description.coSimulation is None:
            raise ValueError(f"{path} has no Co-Simulation interface")
        fmu_class = {"2.0": FMU2Frost, "3.0": FMU3Frost}.get(
            description.fmiVersion
        )
        if fmu_class is None:
            raise ValueError(
                f"{path} declares unsupported fmiVersion "
                f"{description.fmiVersion!r}"
            )
        return fmu_class(unzipdir, description, name), description
    except Exception:
        shutil.rmtree(unzipdir, ignore_errors=True)
        raise
