
from fmake.vhdl_programm_list import add_program,get_list_of_programms


from fmake.user_program_runner import get_list_of_user_programs, get_program


import inspect
from fmake import get_project_directory  
from fmake.generic_helper import try_load_file
import argparse



ps_header = ''' 
#. ([ScriptBlock]::Create( (fmake make-powershell --prefix "pre_"  | Out-String) ) ) # adds functions with prefix "pre_"
#. ([ScriptBlock]::Create( (fmake make-powershell  | Out-String) ) )                 # adds functions without prefix

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


'''

def ps1_script_for_function_from_arguments(function_name, arguments, project_path, Function_prefix=""):
    if len(arguments) == 0:
        ps_function = '''
            
function {Function_prefix}{function_name} {
                
    & fmake --path "{project_path}" {function_name} 
}
            '''.strip()
    else:
        ps_function = '''
       
function {Function_prefix}{function_name} {
    [CmdletBinding()]
    param (
        {arguments}
    )
    $cliArgs = Convert-BoundParametersToCliArgs -BoundParameters $PSBoundParameters
    & fmake --path "{project_path}" {function_name} @cliArgs
}
        '''.strip()

    

    ps_function = ps_function.replace("{Function_prefix}", Function_prefix)
    ps_function = ps_function.replace("{function_name}", function_name)
    ps_function = ps_function.replace("{arguments}", arguments)
    ps_function = ps_function.replace("{project_path}", project_path.replace("\\","/"))
    return ps_function

def ps1_script_for_function_from_function(function_name, fun, project_path, Function_prefix=""):
    sig = inspect.signature(fun)
    arguments = ["$" + sig.parameters[x].name for x in sig.parameters.keys()]

    arguments = ",".join(arguments)
    return ps1_script_for_function_from_arguments(function_name, arguments, project_path, Function_prefix=Function_prefix)
    

def make_powershell_bindings(x):
        #
    parser = argparse.ArgumentParser(description='make powershell bindings')
    parser.add_argument('--prefix', type=str, default="")
    parser.add_argument(
        '--export-builtin-functions',            
        dest='export_builtin_functions',
        action='store_true',
        help='Export builtin functions to the generated PowerShell bindings.'
    )
    args = parser.parse_args(x[2:])  # skip program namepython
    user_programs = get_list_of_user_programs(keyword="program")
    projectdir = get_project_directory()
    ret = ""

    if not args.export_builtin_functions:
        for f,_,p in user_programs:
            
            fun  = get_program(p, keyword="program")
            ret += "\n\n" + ps1_script_for_function_from_function(p, fun,  projectdir, Function_prefix=args.prefix)

    else:
            
        list_of_programs = get_list_of_programms()
        import os
        for p in list_of_programs:
            dummy_file = projectdir + "/jdsgbfjskfbkwehreuiaweyrutmp_help.txt"

            os.system(f"fmake --path {projectdir} {p} -h > {dummy_file} 2>&1")
            help =try_load_file(dummy_file)
            os.remove(dummy_file)
            if "usage:" not in help:
                continue    

            parameters = ["$" + x.split("]")[0].split(" ")[0]  for x in help.split("usage:")[1].split("\n")[0].split("--")[1:]]
            parameters = ",".join(parameters)
            ret += "\n\n" +  ps1_script_for_function_from_arguments(p, parameters, projectdir, Function_prefix=args.prefix)
    

            
    script = ps_header + ret
    print(script)

add_program("make-powershell", make_powershell_bindings)   