

# Vivado Projects with `pyFirmwareProject`

One of the primary use cases of `fmake` is building FPGA firmware projects. The `pyFirmwareProject` class provides a Python interface for describing a Vivado project and turns `fmake` into a Vivado build system.

A minimal project can be defined as an ordinary `fmake` program:

```python
import fmake


@fmake.program
def make_project():
    prj = fmake.pyFirmwareProject("pynq_readout")

    # Project configuration goes here

    prj.make_project()
```

Running:

```text
fmake make_project
```

creates a Vivado project with the default location:

```text
<project_root>/build/pynq_readout
```

The project description itself remains an ordinary Python function. It can therefore use normal Python control flow, functions, classes, environment variables, debugging tools, and IDE support.

## Vivado Installation

`pyFirmwareProject` uses Vivado's Tcl interface to create and configure the project. It therefore needs to know which Vivado installation should be used.

For example, the location can be obtained from an environment variable while providing a local default:

```python
import os

VIVADO_SETTINGS = os.environ.get(
    "VIVADO_SETTINGS",
    default="C:/Xilinx/Vivado/2022.2/settings64.bat"
)

prj.set_vivado_path(VIVADO_SETTINGS)
```

Since the project description is Python code, no special `fmake` mechanism is necessary for environment-dependent configuration.

For example, a build server can define:

```text
VIVADO_SETTINGS=C:/Xilinx/Vivado/2023.2/settings64.bat
```

while a developer can use a different installation without changing the project description.

## Adding Sources

VHDL and other project sources can be added using `add_sources()`:

```python
prj.add_sources([
    "src/pynq_readout_top.vhd",
    "src/axi4_lite_to_reg.vhd",
])
```

Paths are relative to the Python script containing the project definition by default.

Before the Vivado project is generated, `fmake` resolves these paths to absolute paths. If a specified source file does not exist, `fmake` reports an error rather than generating a project containing an invalid source reference.

This makes it possible to keep project descriptions portable:

```text
my_project/
├── build/
├── src/
│   ├── pynq_readout_top.vhd
│   └── axi4_lite_to_reg.vhd
└── make_project.py
```

The project definition only needs:

```python
prj.add_sources([
    "src/pynq_readout_top.vhd",
    "src/axi4_lite_to_reg.vhd",
])
```

regardless of the absolute location at which the repository is checked out.

## Selecting the Top-Level Entity

The synthesis top level is specified directly on the project:

```python
prj.top = "pynq_readout_top"
```

A basic project definition can therefore look like:

```python
import os
import fmake


@fmake.program
def make_project():
    prj = fmake.pyFirmwareProject("pynq_readout")

    vivado_settings = os.environ.get(
        "VIVADO_SETTINGS",
        default="C:/Xilinx/Vivado/2022.2/settings64.bat"
    )

    prj.set_vivado_path(vivado_settings)

    prj.add_sources([
        "src/pynq_readout_top.vhd",
        "src/axi4_lite_to_reg.vhd",
    ])

    prj.top = "pynq_readout_top"

    prj.make_project()
```

## Dependencies

Larger firmware projects rarely consist of a single set of source files. Designs normally depend on reusable components, board definitions, interfaces, constraints, simulation infrastructure, or generated files.

`pyFirmwareProject` provides `add_dependency()` for this purpose.

For example:

```python
prj.add_dependency("boards_pynq_z2")
prj.add_dependency("constraints_pynq_z2_base")

prj.add_dependency("registers_multi_cycle", cycles=3)
prj.add_dependency("fmake_csv_IO")
prj.add_dependency("axi4lite")
prj.add_dependency("axi4lite_to_register")
prj.add_dependency("axi_stream_32")
```

Dependencies use the same general discovery mechanism as `get_program()`. The corresponding implementation can therefore be located elsewhere in the project without requiring the main build script to know its file location.

Dependencies may also receive arguments:

```python
prj.add_dependency("registers_multi_cycle", cycles=3)
```

Named arguments are recommended because they make the resulting project description self-documenting and reduce ambiguity when a dependency gains additional parameters.

### Defining a Dependency

A dependency is implemented as an `fmake` target.

For example:

```python
import fmake


@fmake.target
def axi4lite_to_register(prj: fmake.pyFirmwareProject):
    prj.assert_depenency_exists("axi4lite")
    prj.assert_depenency_exists("registers_multi_cycle")

    prj.add_sources([
        "axi4lite_to_register/axi4lite_to_register.vhd",
    ])
```

When the project contains:

```python
prj.add_dependency("axi4lite_to_register")
```

`fmake` resolves the `axi4lite_to_register` target and calls it with the current `pyFirmwareProject` object.

The dependency can then modify the project directly.

This is an important difference from dependency systems based primarily on metadata files. A dependency does not have to describe its requirements in a separate format which is later interpreted by the build system. It receives the actual project object and uses the same API as the main project definition.

Because the argument can be explicitly typed:

```python
def axi4lite_to_register(prj: fmake.pyFirmwareProject):
```

the IDE knows exactly which object is being modified. Autocompletion, type checking, navigation, and other normal Python development features therefore remain available when writing dependencies.

### Dependency Requirements

A dependency may require that other dependencies have already been added.

For example:

```python
prj.assert_depenency_exists("axi4lite")
prj.assert_depenency_exists("registers_multi_cycle")
```

In this example, `axi4lite_to_register` requires both `axi4lite` and `registers_multi_cycle`.

It would also be possible for the target to call `add_dependency()` itself. However, this is not always desirable.

For example:

```python
prj.add_dependency("registers_multi_cycle", cycles=3)
```

contains a project-specific parameter. The appropriate value of `cycles` is a decision belonging to the project using the dependency rather than necessarily to `axi4lite_to_register`.

The project can therefore make that decision explicitly:

```python
prj.add_dependency("registers_multi_cycle", cycles=3)
prj.add_dependency("axi4lite")
prj.add_dependency("axi4lite_to_register")
```

and `axi4lite_to_register` only verifies that its requirements have been satisfied.

Dependencies are processed in the order in which they appear in the Python project description. The build sequence is therefore directly visible to the user rather than being implicitly determined by a hidden dependency resolver.

## More Complex Dependencies

A target is not limited to adding HDL source files. It has access to the complete `pyFirmwareProject` object and can perform arbitrary Python operations while configuring the project.

For example, the `registers_multi_cycle` dependency performs several different operations:

```python
@fmake.target
def registers_multi_cycle(prj, cycles=3):

    directory = f"{prj.get_project_path()}/gen/registers_multi_cycle/"
    os.makedirs(directory, exist_ok=True)

    fmake.save_file(
        f"{directory}/post_synth_constraints.tcl",
        make_post_synth_constraints(cycles)
    )

    prj.add_custom_code(make_custom_code(directory))

    p = fmake.make_simulation_query_interface("register_poll_tb")

    prj.add_sources([
        "registers_multi_cycle.vhd",
        "sim/register_reciever_example.vhd",
        "sim/register_sender_example.vhd",
    ])

    prj.add_sources_sim([
        "sim/register_tb_tb_csv.vhd",
        "sim/register_tb.vhd",
        "sim/register_tb_IO_pgk.vhd",
        "sim2/register_poll_tb.vhd",
    ])

    prj.add_sources_sim(
        [
            p["query_pkl"]
        ],
        base=fmake.get_project_directory()
    )
```

This example demonstrates several capabilities that are useful for more complicated Vivado projects.

### Generated Build Files

Some dependencies need to generate files as part of project creation.

The multicycle-register dependency first creates a directory inside the generated project data:

```python
directory = f"{prj.get_project_path()}/gen/registers_multi_cycle/"
os.makedirs(directory, exist_ok=True)
```

It then generates a Tcl file:

```python
fmake.save_file(
    f"{directory}/post_synth_constraints.tcl",
    make_post_synth_constraints(cycles)
)
```

The generated Tcl depends on the `cycles` argument supplied by the user:

```python
prj.add_dependency("registers_multi_cycle", cycles=3)
```

The generated project is therefore based directly on the configuration supplied to the dependency.

### Custom Vivado Tcl

Some project behavior cannot be represented simply by adding HDL or constraint files.

The multicycle-register implementation requires custom Tcl to insert additional constraint handling into the Vivado build process.

The target can add this directly:

```python
prj.add_custom_code(
    make_custom_code(directory)
)
```

`pyFirmwareProject` incorporates this code into the Tcl used to construct and configure the Vivado project.

This provides an escape mechanism for Vivado functionality that is not directly represented by the higher-level `pyFirmwareProject` API.

The build description can therefore use convenient Python methods for normal operations while still retaining access to Vivado's Tcl interface when specialized behavior is required.

### Synthesis and Simulation Sources

Files intended for the normal design sources can be added with:

```python
prj.add_sources([
    "registers_multi_cycle.vhd",
    "sim/register_reciever_example.vhd",
    "sim/register_sender_example.vhd",
])
```

Files intended specifically for simulation can instead be added with:

```python
prj.add_sources_sim([
    "sim/register_tb_tb_csv.vhd",
    "sim/register_tb.vhd",
    "sim/register_tb_IO_pgk.vhd",
    "sim2/register_poll_tb.vhd",
])
```

This allows a dependency to provide both its synthesizable implementation and the infrastructure required to simulate or test it.

### Controlling the Base Path

Source paths are normally interpreted relative to the script in which they are specified.

This behavior can be overridden using the `base` argument.

For example:

```python
prj.add_sources_sim(
    [
        p["query_pkl"]
    ],
    base=fmake.get_project_directory()
)
```

Here, `make_simulation_query_interface()` returns a generated file whose path is relative to the project root rather than to the dependency script.

The `base` argument therefore explicitly changes the reference directory used to resolve the supplied paths.

This makes it possible to combine files originating from different locations without introducing assumptions about the absolute location of the repository.

### Build Logic Remains Python

The central design principle behind `pyFirmwareProject` is that the project description remains executable Python.

A dependency can:

```python
prj.add_sources(...)
prj.add_sources_sim(...)
prj.add_dependency(...)
prj.assert_depenency_exists(...)
prj.add_custom_code(...)
```

but it can also use ordinary Python:

```python
if condition:
    ...

for source in sources:
    ...

value = os.environ.get("SOME_VARIABLE")

with open(...) as file:
    ...
```

There is no separate build-description language between the project author and the `pyFirmwareProject` API.

The execution order is also the order written in the project script:

```python
prj.add_dependency("registers_multi_cycle", cycles=3)
prj.add_dependency("axi4lite")
prj.add_dependency("axi4lite_to_register")
```

The user can therefore follow the build process directly through the Python code and, when necessary, place breakpoints in the project definition or dependency implementation and inspect the project state using a standard Python debugger.

For straightforward dependencies this may amount to little more than adding a VHDL file. More complicated dependencies can generate files, configure simulation sources, insert Tcl into the Vivado flow, inspect other dependencies, or perform arbitrary project-specific setup while using the same interface.

