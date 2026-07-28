# fmake.program

The `fmake.program` feature lets you expose ordinary Python functions as runnable `fmake` commands.

At a high level, `fmake` scans Python files under the current project directory, finds functions decorated with `@fmake.program`, and makes those functions callable from the `fmake` command line or through `fmake.get_program(...)` inside Python.

## Basic usage

Create a Python file anywhere under the project directory and decorate a function:

```python
import fmake


@fmake.program
def hello(name="world"):
    print(f"hello {name}")
```

Then run it from the command line:

```powershell
fmake hello --name Alice
```

`fmake` forwards positional arguments as normal Python positional arguments and parses `--key value` pairs into keyword arguments.

## What the CLI does

The `fmake` console entry point is wired to `fmake.main_vhdl_make:main_vhdl_make`.

When you run:

```powershell
fmake <program-name> [args]
```

the CLI does this:

1. Checks whether `<program-name>` is a built-in `fmake` command.
2. If not, looks for a user program with the same name.
3. Imports the Python file that defines that program.
4. Calls the function with parsed positional and keyword arguments.
5. Prints the return value if the function returns something other than `None`.

If you run `fmake` without enough arguments, it prints the built-in program list and then a table of discovered user programs.

## How discovery works

User program discovery is implemented in [fmake/user_program_runner.py](/c:/Users/Richa/GitHub/fmake/fmake/user_program_runner.py).

`fmake` walks the current project directory recursively and inspects every `.py` file it finds. For each file, it searches the source text for functions that match this decorator pattern:

```python
@fmake.program
def my_program(...):
    ...
```

It also accepts the versioned form:

```python
@fmake.program(version=12.0)
def my_program(...):
    ...
```

The scan is text-based before import. Actual function loading happens only when a specific program is selected.

## Version support

The decorator accepts an optional `version` argument:

```python
@fmake.program(version=12.0)
def print_hello():
    print("hello world")
```

That version is stored in the discovery table and can be used with `fmake.get_program(...)`.

Example:

```python
import fmake


program = fmake.get_program("print_hello", file="ex3.py", version=12.0)
program()
```

Important detail: CLI dispatch via `fmake <name>` uses the first discovered matching name and does not perform version filtering. Version filtering is available through `fmake.get_program(...)`.

## Calling a program from Python

`fmake` re-exports `get_program` from `fmake.user_program_runner`, so you can load a user program directly:

```python
import fmake


hello = fmake.get_program("hello")
hello("Alice")
```

Supported lookup options:

- `Name`: program name to resolve.
- `file`: limit the match to a specific filename.
- `fullpath`: bypass discovery and load directly from an exact file path.
- `unique=True`: require that the name resolves to exactly one visible program.
- `version`: keep only matches whose stored version is greater than or equal to this value.
- `version_exact=True`: require the version to match exactly.

If multiple files define the same program name, `get_program(...)` attempts to narrow the match using the caller's subfolder before raising an ambiguity error.

## Runtime behavior of the decorator

The decorator itself is intentionally small. It wraps the function, prints a line like:

```text
running hello, version=None
```

and then calls the original function.

The wrapper also stores the version on `wrapper.version`.

## Project root and search scope

Discovery uses `fmake.get_project_directory()` as the root of the search.

From the command line, the root can be overridden with:

```powershell
fmake --path C:\path\to\project hello
```

After that, user-program lookup runs relative to the supplied directory.

## Argument passing

Argument parsing is simple:

- Plain values become positional arguments.
- `--name value` becomes the keyword argument `name="value"`.
- All values arrive as strings unless your function converts them.

Example:

```python
import fmake


@fmake.program
def add(x, y):
    return int(x) + int(y)
```

```powershell
fmake add 3 4
```

## Example files already in this repository

- [example.py](/c:/Users/Richa/GitHub/fmake/example.py) shows several `@fmake.program` functions.
- [ex3.py](/c:/Users/Richa/GitHub/fmake/ex3.py) shows a versioned program.
- [run1.py](/c:/Users/Richa/GitHub/fmake/run1.py) shows `fmake.get_program(...)` loading a versioned function directly.

## Practical constraints

- Discovery is based on source matching, so the function must appear with a recognizable `@fmake.program` decorator directly above the `def`.
- Programs are discovered only in `.py` files under the project directory.
- If two visible files define the same program name, CLI execution chooses the first discovered match, while `get_program(...)` can raise an ambiguity error.
- CLI keyword arguments use `--key value` form, not `--key=value` parsing in this implementation.

## Summary

Use `@fmake.program` when you want a plain Python function to become a lightweight `fmake` command. The feature is discovery-based, works across the project tree, supports optional version metadata, and can be used either from the `fmake` CLI or through `fmake.get_program(...)` in Python.