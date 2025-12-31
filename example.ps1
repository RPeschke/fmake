
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

function Invoke-AlphaTool {
    [CmdletBinding()]
    param(
        [string]   $InputPath,
        [string]   $Mode,
        [int]      $Count,
        [switch]   $DryRun,
        [string[]] $Tags,
        [hashtable]$Config
    )

    $python = "python"
    $script = "alpha_tool.py"

    $cliArgs = Convert-BoundParametersToCliArgs -BoundParameters $PSBoundParameters
    & $python $script @cliArgs
}
