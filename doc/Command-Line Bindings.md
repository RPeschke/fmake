
# Command-Line Bindings

In addition to calling programs directly through:

```text
fmake <program> [arguments]
```

`fmake` can generate bindings for the user's shell. These bindings expose project programs as native shell functions while retaining information such as their arguments and project location.

## PowerShell

All programs of the current project can be exported as PowerShell functions with:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell | Out-String)))
```

After running this command, the project's `fmake` programs can be called like ordinary PowerShell functions.

For example, consider the following program:

```python
import fmake


@fmake.program
def example1(t1, t2="world"):
    return t1 + " " + t2
```

After importing the PowerShell bindings, it can be called directly:

```powershell
example1 -t1 hello
```

which produces:

```text
hello world
```

Arguments can also be specified explicitly:

```powershell
example1 -t1 hello -t2 Richard
```

producing:

```text
hello Richard
```

The generated PowerShell function is aware of the arguments defined by the Python function. Consequently, standard PowerShell functionality such as parameter-name completion and argument suggestions remains available.

### Missing Arguments

Required and optional arguments are determined from the Python function signature.

In the previous example:

```python
def example1(t1, t2="world"):
```

`t1` is required, while `t2` has the default value `"world"`.

Calling the function without the required argument:

```powershell
example1
```

therefore results in an error such as:

```text
Error when calling user program:
example1() missing 1 required positional argument: 't1'
Function example1 takes the following arguments:
  t1
  t2 (default='world')
```

There is no separate PowerShell definition of which arguments a program accepts. The Python function remains the definition of the program interface.

## Adding a Prefix

For larger environments, it can be useful to make it immediately visible that a function belongs to a particular project.

A common prefix can be added when generating the bindings:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell --prefix "pre_" | Out-String)))
```

For example, instead of:

```powershell
example1 -t1 hello
```

the exported function is then called as:

```powershell
pre_example1 -t1 hello
```

This can also help prevent name collisions between project programs and existing PowerShell commands or functions exported by another project.

A project-specific prefix can therefore be used, for example:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell --prefix "readout_" | Out-String)))
```

resulting in commands such as:

```text
readout_make_project
readout_make_simulation
readout_program_fpga
```

while the corresponding Python program names remain unchanged.

## How the PowerShell Binding Works

The generated bindings are ordinary PowerShell functions.

Conceptually, a generated function for `example1` looks like:

```powershell
function example1 {
    [CmdletBinding()]
    param (
        $t1,
        $t2
    )

    $cliArgs = Convert-BoundParametersToCliArgs `
        -BoundParameters $PSBoundParameters

    & fmake --path "<path to root>" example1 @cliArgs
}
```

The generated function collects the parameters supplied through PowerShell and converts them into arguments for the `fmake` command-line interface.

The important part is that the generated command contains an explicit project path:

```powershell
fmake --path "<path to root>" example1 ...
```

The binding is therefore associated with the project from which it was generated.

For example, after exporting the functions while working in:

```text
C:/projects/pynq_readout/
```

the user can change to an unrelated directory:

```powershell
cd C:/some/other/directory
```

and still call:

```powershell
example1 -t1 hello
```

The generated function continues to execute the program belonging to the original `pynq_readout` project.

This makes the exported functions independent of the current working directory and gives them predictable project context.

## Why Generate Functions Instead of Aliases?

The PowerShell integration deliberately generates real PowerShell functions rather than simple command aliases.

This preserves useful shell behavior:

```text
Python @fmake.program
        |
        | function signature
        v
Generated PowerShell function
        |
        | PowerShell parameters
        v
fmake --path <project-root> <program> <arguments>
        |
        v
Python program
```

The Python function remains the source of truth for the program interface, while the generated PowerShell function provides a convenient shell-native interface to it.

As a result, project commands can be used much like ordinary PowerShell commands without maintaining a separate PowerShell implementation of each command.


## Bash

`fmake` provides a similar binding mechanism for Bash.

All programs in the current project can be exported as Bash functions with:

```bash
source <(fmake make-bash)
```

After sourcing the generated definitions, `fmake` programs can be called like ordinary Bash functions.

For example, the Python program:

```python
import fmake


@fmake.program
def example1(t1, t2="world"):
    return t1 + " " + t2
```

can be called directly from Bash:

```bash
example1 --t1 hello
```

producing:

```text
hello world
```

As with the PowerShell bindings, the generated functions remain associated with the project from which they were created. They can therefore be called after changing to a different working directory.

### Adding a Prefix

A common prefix can be added to all generated Bash functions:

```bash
source <(fmake make-bash --prefix pre_)
```

The previous example would then be available as:

```bash
pre_example1 --t1 hello
```

This is useful for identifying commands belonging to a particular project and for avoiding name collisions with existing shell commands or functions from other projects.

## How the Bash Binding Works

The generated bindings are ordinary Bash functions.

For example, `example1` generates a function similar to:

```bash
example1() {
  fmake --path "<path to root>" example1 "$@"
}
```

As with the PowerShell bindings, the project root is embedded into the generated function using the `--path` argument.

The command:

```bash
example1 --t1 hello
```

therefore ultimately executes something equivalent to:

```bash
fmake --path "<path to root>" example1 --t1 hello
```

The use of:

```bash
"$@"
```

forwards the arguments supplied to the Bash function to `fmake`.

Since the project path is fixed when the bindings are generated, the function can be called from any working directory while still referring to the correct project.

## Bash Completion

`fmake` also generates basic Bash completion functions based on the arguments of the corresponding Python program.

For `example1`, a generated binding can look like:

```bash
example1() {
  fmake --path "<path to root>" example1 "$@"
}

_example1_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"

  if [[ $cur == -* ]]; then
    COMPREPLY=( $(compgen -W "--t1 --t2" -- "$cur") )
    return 0
  fi

  # No candidates -> trigger fallback to normal Bash completion.
  COMPREPLY=()
}

complete -F _example1_complete -o bashdefault -o default example1
```

The completion function knows that the Python program:

```python
def example1(t1, t2="world"):
```

accepts the arguments:

```text
--t1
--t2
```

Typing:

```bash
example1 --<TAB>
```

can therefore suggest the available arguments.

The completion is intentionally lightweight. If `fmake` has no specific completion candidate, the generated function falls back to Bash's normal completion behavior through:

```bash
-o bashdefault -o default
```

This makes exported `fmake` programs behave naturally in an interactive Bash shell without requiring a separately maintained completion definition for every project command.

## Shell Bindings

Both the PowerShell and Bash integrations follow the same general principle:

```text
@fmake.program
      |
      v
fmake inspects the program
      |
      +--------------------+
      |                    |
      v                    v
PowerShell function    Bash function
      |                    |
      +---------+----------+
                |
                v
 fmake --path <project-root> <program> ...
                |
                v
          Python program
```

The Python program remains the definition of the command and its arguments. The generated shell bindings provide a native interface for the shell being used.

For PowerShell this includes generated PowerShell parameters. For Bash, `fmake` generates Bash functions together with basic argument completion.

In both cases, the generated function contains the project root explicitly. The resulting commands therefore behave consistently regardless of the user's current working directory.
