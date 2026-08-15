

from fmake.programm_list import add_program,get_list_of_programms


from fmake.user_program_runner import get_list_of_user_programs, get_program


import inspect
from fmake import get_project_directory  

import argparse

ps_header = ""

bash_template = '''
{prefix}{function_name}() {
  fmake --path {project_path}  {function_name} "$@"
}

_{prefix}{function_name}_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"

  if [[ $cur == -* ]]; then
    COMPREPLY=( $(compgen -W "{arguments}" -- "$cur") )
    return 0
  fi

  # No candidates -> trigger fallback (filenames) via -o bashdefault/default
  COMPREPLY=()
}

complete -F _{prefix}{function_name}_complete -o bashdefault -o default {function_name}

'''

def make_bash_bindings(x):
        #
    parser = argparse.ArgumentParser(description='make bash bindings')
    parser.add_argument('--prefix', type=str, default="")
    parser.add_argument(
        '--export-builtin-functions',            
        dest='export_builtin_functions',
        action='store_true',
        help='Export builtin functions to the generated bash bindings.'
    )
    args = parser.parse_args(x[2:])  # skip program name
    user_programs = get_list_of_user_programs(keyword="program")
    projectdir = get_project_directory()
    ret = "#usage:\n#source <(fmake make-bash)\n\n\n"

    if not args.export_builtin_functions:
        for row in user_programs:
            p = row["program_name"]
            fun  = get_program(p , keyword="program")
            sig = inspect.signature(fun)
            arguments = ["--" + sig.parameters[x].name for x in sig.parameters.keys()]

            arguments = "  ".join(arguments)

            ret += "\n\n" + bash_template.replace(
                "{function_name}", p
                ).replace(
                    "{project_path}", projectdir
                    ).replace(
                        "{prefix}", args.prefix
                        ).replace(
                            "{arguments}", arguments
                            )

    else:
            
        list_of_programs = get_list_of_programms()
        import os
        for p in list_of_programs:

            ret += "\n\n" + bash_template.replace("{function_name}", p).replace("{project_path}", projectdir).replace("{prefix}", args.prefix) 
            
            
    

            
    script = ps_header + ret
    print(script)

add_program("make-bash", make_bash_bindings)   