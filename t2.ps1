function load_python {
    param (
        [string] $Path
    )
    $code = python $Path | Out-String
    #$sb   = [ScriptBlock]::Create($code)
    #Invoke-Command -ScriptBlock $sb -NoNewScope
    . ([ScriptBlock]::Create($code))
}