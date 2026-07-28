<mdpyex>

# fmake

`fmake` is a Python-based firmware build and simulation helper focused on VHDL projects. It combines built-in commands for project generation and simulator execution with a lightweight user-program system so project-specific automation can live directly in normal Python files.

## Feature summary

- `fmake.program`: expose plain Python functions as custom `fmake` commands using the `@fmake.program` decorator.
- `make-simulation`: generate the build folder, dependency-driven project files, CSV/text I/O support files, and optional cocotb makefiles for a simulation target.
- `run-ghdl`: execute a generated simulation through GHDL by running the produced make-based flow in the entity build directory.
- `run-vivado`: run a simulation in the Vivado toolchain using `xelab` and `xsim`.
- `run-ise`: run a simulation in the ISE/ISim flow by building and executing the generated simulation executable.
- Additional built-in helpers cover implementation generation, testbench generation, register export, build-system generation, and related VHDL project utilities.

## Design

The project is designed around two layers:

1. Built-in `fmake` commands for common HDL workflows such as simulation setup, simulator execution, and project-file generation.
2. User-defined `fmake` programs for project-local automation, so teams can add custom commands without changing the package internals.

This makes it practical to use the same tool for both standard flows and repository-specific scripting.

## Simulator support

`fmake` is designed to support multiple simulator and vendor tool flows:

- ISE / ISim: used through `run-ise`.
- Vivado simulator: used through `run-vivado`.
- GHDL: used through `make-simulation` plus `run-ghdl`.

In typical use, `make-simulation` prepares the build artifacts for an entity and a follow-up run command executes the simulator for the selected backend.

## Custom commands

For project-specific automation, place Python files under the project directory and decorate functions with `@fmake.program`. Those functions become callable through the `fmake` CLI.

See [doc/fmake-program.md](/c:/Users/Richa/GitHub/fmake/doc/fmake-program.md) for details on how user programs are discovered and executed.

</mdpyex>
