
from fmake.programm_list import add_program

bash_autocomplete = r"""
_fmake_completion()
{
    local current="${COMP_WORDS[COMP_CWORD]}"

    local matches
    mapfile -t matches < <(
        fmake --autocompleteBash \
            "$COMP_POINT" \
            "$COMP_LINE" \
            "$current"
    )

    COMPREPLY=()

    for match in "${matches[@]}"; do
        case "$match" in
            __FMAKE_DEFAULT__)
                return 0
                ;;
            __ERROR__*)
                continue
                ;;
            *)
                COMPREPLY+=("$match")
                ;;
        esac
    done
}

complete -F _fmake_completion -o bashdefault -o default fmake
"""

def BASHautocomplete(argv):
    print(bash_autocomplete )


add_program("make-bashautocomplete", BASHautocomplete)   