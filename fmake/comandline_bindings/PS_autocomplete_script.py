
from fmake.programm_list import add_program


def PSautocomplete(argv):
    print('''
# Rund the script like this
# . ([ScriptBlock]::Create((fmake make-psautocomplete | Out-String))) 
Register-ArgumentCompleter -Native -CommandName fmake -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $matches = @(
        & fmake --autocompletePS `
            $cursorPosition `
            $commandAst.ToString() `
            $wordToComplete             
    )

    if ($matches -contains "__FMAKE_DEFAULT__") {
        return
    }

    foreach ($match in $matches) {

        if (-not $match) {
            continue
        }

        if ($match.StartsWith("__ERROR__")) {
            continue
        }

        [System.Management.Automation.CompletionResult]::new(
            $match,
            $match,
            'ParameterValue',
            $match
        )
    }
}
''')

add_program("make-psautocomplete", PSautocomplete)   