# PowerShell and Bash Bindings

`fmake` includes two built-in commands that generate shell wrapper functions:

- `make-powershell`
- `make-bash`

These commands do not directly execute a firmware flow. Instead, they print shell code that you can load into your current terminal session so `fmake` commands become easier to call as native shell functions.

## What problem they solve

Without bindings, you invoke commands like this:

```powershell
fmake --path C:\work\project my_program --input data.csv
```

or in Bash:

```bash
fmake --path /work/project my_program --input data.csv
```

The generated bindings wrap that call into shell functions tied to the current project path, so you can call the program by name directly.

## PowerShell bindings

Generate the script text with:

```powershell
fmake make-powershell
```

Load the generated functions into the current PowerShell session with:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell | Out-String)))
```

You can also add a prefix to avoid name collisions:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell --prefix "fm_" | Out-String)))
```

After that, a user program like `hello` becomes callable as a PowerShell function such as `hello` or `fm_hello`.

## How the PowerShell wrapper works

The PowerShell generator creates:

- a helper called `Convert-BoundParametersToCliArgs`
- one PowerShell function per exported `fmake` command

For functions with parameters, the generated wrapper uses PowerShell named parameters, collects `$PSBoundParameters`, converts them to `--name value` pairs, and calls:

```powershell
fmake --path "<project-path>" <program-name> @cliArgs
```

For functions without parameters, it emits a simpler wrapper that just runs the `fmake` command directly.

## Bash bindings

Generate the script text with:

```bash
fmake make-bash
```

Load it into the current shell with:

```bash
source <(fmake make-bash)
```

You can also apply a prefix:

```bash
source <(fmake make-bash --prefix fm_)
```

After loading, a user program such as `hello` becomes a shell function like `hello` or `fm_hello`.

## How the Bash wrapper works

The Bash generator creates:

- one shell function per exported `fmake` command
- one completion function per exported command

Each generated function forwards all arguments to:

```bash
fmake --path <project-path> <program-name> "$@"
```

The generated completion function suggests `--parameter` names for user programs based on the Python function signature. If no option matches, completion falls back to normal Bash filename completion.

## What gets exported

By default, both generators export discovered user programs, not the built-in `fmake` commands.

That means functions created with `@fmake.program` are the primary target of these bindings.

## Exporting built-in commands

Both generators support:

```text
--export-builtin-functions
```

When this flag is used:

- `make-powershell` exports built-in `fmake` commands by probing their help output and deriving parameter names from the usage line.
- `make-bash` exports built-in command wrappers as shell functions.

Example:

```powershell
fmake make-powershell --export-builtin-functions
```

```bash
fmake make-bash --export-builtin-functions
```

## Relationship to `fmake.program`

The shell bindings rely on the same user-program discovery path as the rest of `fmake`. In practice, that means:

- user programs must live in Python files under the project directory
- they must be decorated with `@fmake.program`
- the wrappers call `fmake --path <project-path> ...` so the generated functions stay anchored to the project where the bindings were created

See [doc/fmake-program.md](/c:/Users/Richa/GitHub/fmake/doc/fmake-program.md) for the underlying user-program model.

## Practical examples

PowerShell:

```powershell
. ([ScriptBlock]::Create((fmake make-powershell --prefix "proj_" | Out-String)))
proj_hello -name Alice
```

Bash:

```bash
source <(fmake make-bash --prefix proj_)
proj_hello --name Alice
```

## Limitations and behavior notes

- The bindings are generated for the current project path at generation time.
- The Bash generator forwards raw CLI arguments and does not translate shell named parameters the way PowerShell does.
- PowerShell parameter generation for user programs is based on the discovered Python function signature.
- Built-in PowerShell parameter export depends on parsing each built-in command's `-h` output.
- The wrappers are session-local unless you save the generated output into your shell profile yourself.

## Summary

Use `make-powershell` and `make-bash` when you want a more natural shell experience on top of `fmake`. They generate lightweight wrappers around `fmake --path <project> ...`, making custom and built-in commands easier to invoke repeatedly in the same project.