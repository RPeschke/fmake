
function Convert-BoundParametersToCliArgs {
    [CmdletBinding()]
    param(
        # Usually pass $PSBoundParameters here
        [Parameter(Mandatory)]
        [hashtable] $BoundParameters
    )

    $args = @()

    foreach ($entry in $BoundParameters.GetEnumerator()) {
        $name  = $entry.Key
        $value = $entry.Value

        $args += "--" + [string]$name
        $args += [string]$value
    }

    return ,$args  # ensure array
}



function example {
    [CmdletBinding()]
    param (
        $test
    )
        $cliArgs = Convert-BoundParametersToCliArgs -BoundParameters $PSBoundParameters
    & fmake --path "C:/Users/Richa/GitHub/fmake" example @cliArgs
}