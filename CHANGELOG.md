# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-08-19

### Added

- `FrostScheduler`, a scheduler reactor driven by `frost-planner`, with job
  scopes, task-to-`CompositeMethodNode` maps and completion-driven rescheduling.
- Simulation support: `Orchestrator`, `SimModel`, `SimulationInterface` and
  `FrostFmu` for co-simulation with FMUs.
- `MessageFilter` in the message protocol layer.
- Variable subscription support in `frost.py`.
- `CITATION.cff` with citation information for the project.

### Changed

- **Packaging**: Frost is consumed through the Lingua Franca package
  mechanism (`lf-packages/` or `LF_PACKAGES`) instead of Lingo. `Lingo.toml`
  has been removed; `lfc` resolves `<frost/...>` imports against `src/lib/`
  and never read that file. See the README for consumer instructions.
- **Reactor hierarchy**: `FrostLink` and `FrostNode` were refactored, and
  `FrostInterface` now registers senders by port index.
- Message construction moved to a message-builder integration, and bus
  response messages were reworked accordingly.

### Removed

- Neighbour discovery: reactors now resolve peers through `targets` only.

### Fixed

- Registration phase no longer depends on neighbours.
- `FrostScheduler` stops once all tasks complete and only recomputes the
  schedule on bus connection and after each task completion.
- `FrostDataModel` closes its connectors on shutdown.

### Breaking changes

- Consumers must migrate from Lingo to the LF package mechanism and update
  imports to `<frost/...>`.
- `FMUWrapper` was renamed to `FrostFMU`.
- Code relying on neighbour discovery must be updated to use `targets`.

## [1.0.0] - 2025-10-07

Initial release.

[1.1.0]: https://github.com/glacier-project/frost/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/glacier-project/frost/releases/tag/v1.0.0
