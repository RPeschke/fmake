
# fmake

`fmake` is a Python-based build and configuration system originally developed for FPGA firmware projects, with a particular focus on VHDL development in the AMD/Xilinx Vivado ecosystem.

It provides built-in commands for common firmware development tasks. For example, `make-simulation` creates a Vivado project for simulating a specified VHDL entity, which can subsequently be opened or executed using `run-vivado`.

In addition to these built-in commands, `fmake` allows projects to define their own **programs** and **targets**. These provide a simple mechanism for making Python functionality and configuration available throughout an entire project without requiring a separate configuration language or registration system.





## Programs and Targets

A **program** is an ordinary Python function decorated with `@fmake.program`.

Any decorated function contained within the project directory is automatically discoverable by `fmake` and can be accessed from anywhere in the project using:

```python
fmake.get_program("program_name")
```

Programs are also exposed through the command-line interface. For example, given:

```python
import fmake

@fmake.program
def hello(name):
    return f"Hello {name}"
```

the program can be executed from anywhere inside the project with:

```text
fmake hello Richard
```

If the function returns a value that can be converted to a string, the command-line interface prints that value.

A **target** behaves similarly to a program, but is intended only for use by other Python code. Targets are not exposed through the `fmake` command-line interface.

This distinction makes programs useful as project-wide commands and configuration providers, while targets can be used for internal functionality that should not become part of the project's command-line interface.

## Using Programs as Configuration

One important use of the program mechanism is configuration management.

Traditional configuration files such as JSON, YAML, TOML, or INI normally introduce a boundary between the configuration representation and the Python objects used by the application.

For example, suppose an application expects the following configuration:

```text
IP address
port
user
key
```

A conventional approach might define this information in JSON:

```json
{
    "ipaddress": "192.168.0.1",
    "port": 22,
    "user": "user",
    "key": "keyfile"
}
```

The application then needs code that reads this representation and translates it into whatever Python representation the rest of the program expects.

This creates two representations of essentially the same interface:

```text
configuration file
        |
        v
parser / translation layer
        |
        v
Python configuration object
```

The two representations have to remain synchronized. If the Python interface changes, the configuration format and its translation code may have to change as well.

The relationship is also not necessarily obvious to someone configuring a project. The available fields, their Python types, and the objects to which they eventually map may only be documented separately. IDE support and autocompletion for configuration files also depend on the chosen format and usually require an additional schema.

With `fmake`, the configuration can instead be Python code that directly constructs the object required by the application.

### Configuration Class

For example, the application can define its configuration normally:

```python
# my_config_class.py

class MyConfig:
    def __init__(self):
        self.ipaddress = None
        self.port = None
        self.user = None
        self.key = None
```

The project configuration can then provide an instance of that exact class:

```python
# my_config_script.py

import fmake
from my_config_class import MyConfig


@fmake.program
def my_config():
    ret = MyConfig()

    ret.ipaddress = "192.168.0.1"
    ret.port = 22
    ret.user = "user"
    ret.key = "keyfile"

    return ret
```

Another part of the project can retrieve the configuration directly:

```python
config = fmake.get_program("my_config")()

print(config.ipaddress)
print(config.port)
```

There is no intermediate representation:

```text
fmake program
     |
     v
MyConfig object
```

The configuration script and the consuming application use the **same Python class definition**.

This means that normal Python development tools continue to work when editing configuration. IDE autocompletion, type information, static analysis, navigation to definitions, and debugging are available without defining a separate configuration schema.

If the configuration interface changes, outdated configuration scripts are also much easier to identify. Depending on the change and the tooling being used, an incompatible configuration can result in an immediate IDE/type-checking error or a runtime error when the configuration is loaded rather than silently passing through an unrelated configuration format.

Because the configuration is ordinary Python, it is also not limited to static values. It can use any functionality available to Python. For example, values can be obtained from environment variables:

```python
import os
import fmake
from my_config_class import MyConfig


@fmake.program
def my_config():
    ret = MyConfig()

    ret.ipaddress = os.environ.get("DEVICE_IP", "192.168.0.1")
    ret.port = int(os.environ.get("DEVICE_PORT", "22"))
    ret.user = os.environ["DEVICE_USER"]
    ret.key = os.environ["DEVICE_KEY"]

    return ret
```

Configuration can therefore range from a few constant values to configuration assembled dynamically from the environment or other project information without requiring additional features in `fmake`.

### Security Considerations

An `fmake` configuration is **executable Python code**, not a passive data format.

Loading or executing an `fmake` program can execute arbitrary code contained in the corresponding Python script. An `fmake` configuration must therefore only be used when the configuration source is trusted.

In this respect, it has security considerations similar to mechanisms such as Python `pickle`: **do not execute configuration from an untrusted source.**

This is an intentional trade-off. `fmake` does not attempt to provide the isolation of JSON, TOML, or similar data-only formats. Instead, it allows configuration to use the same language, types, classes, tooling, and abstractions as the software that consumes it.


## Project Structure and Project Root

`fmake` operates relative to a **project root**. Programs and Targets are discovered recursively below this directory, and several of the built-in build functions assume a conventional project structure containing a `build` directory directly below the project root.

A project can be initialized from its root directory using:

```text
fmake make-build
```

This creates the build structure expected by `fmake`, including:

```text
my_project/
├── build/
│   └── fmake.txt
├── ...
```

When `fmake` is started, it determines the project root using the following mechanisms.

The most direct indication is an `fmake.txt` file located inside a `build` directory one level below the project root:

```text
<project-root>/build/fmake.txt
```

If this structure cannot be found, `fmake` searches for the first `.git` directory and uses the corresponding Git repository as the project.

Only actual `.git` directories are considered for this purpose. `.git` files, as used for example by some Git worktree configurations, are ignored.

If neither an `fmake.txt` project nor a `.git` directory can be found, `fmake` assumes that the current directory is the project root.

The project root can also be specified explicitly:

```text
fmake --path <my_project_root> <command>
```

For example:

```text
fmake --path C:\projects\my_fpga_project my_config
```

When `--path` is supplied, `fmake` uses the specified directory as the project root rather than relying on automatic project discovery.

All programs and targets below the resulting project root are available to `fmake`.

## Program and Target Discovery

Programs and targets do not have to be registered in a central file.

Instead, `fmake` searches the Python files below the project root for functions decorated with either:

```python
@fmake.program
```

or:

```python
@fmake.target
```

For example, a project might contain:

```text
my_project/
├── build/
│   └── fmake.txt
├── configuration/
│   ├── network.py
│   └── fpga.py
├── scripts/
│   └── programming.py
└── source/
```

A program defined anywhere below the project root can be retrieved from Python:

```python
program = fmake.get_program("my_program")
```

Programs can additionally be invoked directly from the command line:

```text
fmake my_program
```

Target use the same discovery mechanism but are intended for internal use by Python code and are therefore not exposed as command-line commands.

### Discovery Cache

Searching every Python file in a large project for every `get_program()` lookup would introduce unnecessary overhead. `fmake` therefore caches the locations at which programs and targets have previously been discovered.

When resolving a program or target, `fmake` first attempts to load it from the cached location.

Conceptually, the lookup behaves as follows:

```text
request program
      |
      v
try cached location
      |
      +---- success ----> execute
      |
      v
wait for project search
      |
      v
try discovered location
      |
      +---- success ----> execute
      |
      v
report error and stop
```

If loading from the cached location fails, `fmake` waits for the project search to finish and attempts the lookup again using the newly discovered information.

If the program or target still cannot be resolved or loaded successfully, execution is stopped and an error is reported.

This allows repeated calls to use the fast cached path while still allowing `fmake` to recover from stale cache information when files have been moved, renamed, added, or otherwise changed.

## Loading Python Files

Once the location of a program or target has been resolved, `fmake` loads the Python file containing the function using the standard Python import machinery.

The file is loaded in the context of the directory in which it is located. This makes it possible for project scripts to resolve imports relative to their own location in the same way they normally would when executed from that directory.

The loaded function is then made available to the caller through the `fmake` program/target interface.

Because these files are imported and executed as Python, the same security considerations described for configuration programs apply here: Python files discovered by `fmake` must be considered executable code.

## Resolving Name Collisions

In a small project, program and target names will usually be unique:

```python
@fmake.program
def print_hello():
    return "Hello"
```

and can simply be addressed as:

```text
fmake print_hello
```

For larger projects, however, requiring every program name to be globally unique would quickly become inconvenient.

Consider a project containing several configurations:

```text
my_project/
├── board_a/
│   └── configuration.py
├── board_b/
│   └── configuration.py
└── test/
    └── configuration.py
```

Each configuration may provide programs with the same names:

```python
@fmake.program
def get_device():
    ...


@fmake.program
def get_sources():
    ...


@fmake.program
def get_build_options():
    ...
```

Renaming every function to include the particular configuration would create unnecessary differences between otherwise structurally identical configuration files.

`fmake` therefore supports multiple mechanisms for resolving programs with identical names.

### Resolution Based on the Caller

When several matching programs or targets exist, `fmake` first uses the location of the caller to resolve the ambiguity.

A definition located in a subdirectory of the caller is preferred. This allows different parts of a large project to provide local implementations of programs or targets without requiring globally unique function names.

This is particularly useful for hierarchical projects in which a local configuration should override or specialize functionality for one part of the project.

### Selecting a Program by File Name

The caller can also explicitly restrict the lookup to a particular Python file by prefixing the program name with the file name.

For example, suppose the project contains several definitions of:

```python
@fmake.program
def print_hello():
    ...
```

and one of them is located in:

```text
configuration123.py
```

It can be selected explicitly with:

```text
fmake configuration123.print_hello
```

In this case, `fmake` searches specifically for a `print_hello` program defined in a file named:

```text
configuration123.py
```

The same principle applies when retrieving a program from Python.

This is especially useful when a project contains several configuration files with the same interface:

```text
configurations/
├── simulation.py
├── development.py
├── production.py
└── hardware_test.py
```

Each file can expose the same set of program names:

```python
@fmake.program
def network_config():
    ...


@fmake.program
def build_config():
    ...


@fmake.program
def device_config():
    ...
```

The desired configuration can then be selected through the file rather than by changing the interface:

```text
fmake simulation.build_config
fmake development.build_config
fmake production.build_config
```

This keeps the configuration interface consistent. The meaning of `build_config` remains the same everywhere; only the configuration provider changes.

### Further Disambiguation

File names are not the only mechanism available for resolving ambiguous programs and targets.

`fmake` can further restrict the lookup using information such as:

* the version of the program or target,
* the Python file name,
* the location of the file,
* or its full path.

This allows the simple form:

```text
fmake print_hello
```

to remain convenient for the normal case while still providing explicit control when a large project contains several valid implementations of the same program.

