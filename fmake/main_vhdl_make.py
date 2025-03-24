import sys
from fmake.vhdl_programm_list import get_function,  print_list_of_programs
from fmake import get_project_directory
from pathlib import Path
from fmake.user_program_runner import run_fmake_user_program,parse_args_to_kwargs
    
def main_vhdl_make():
    if len(sys.argv) < 2:
        print("not enough arguments")
        print("\n\nFmake Programs:")
        print_list_of_programs(printer= print)
        _, user_programs = run_fmake_user_program("")
        print("\n\nUser programs:")
        for f,_,p in user_programs:
            print("File: " + f + ", program: " + p)
        return 
    
    program = sys.argv[1]
    fun = get_function(program)
    
    if fun is not  None:
        fun(sys.argv)
        return
    

    fun, user_programs = run_fmake_user_program(program)
    if fun is not None:
        args, kwargs = parse_args_to_kwargs(sys.argv[2:])
        fun(*args, **kwargs)
        return

    print("unknown programm")
    print("\n\nFmake Programs:")
    print_list_of_programs(printer= print)
    print("\n\nUser programs:")
    for f,_,p in user_programs:
        print("File: " + f + ", program: " + p)
    

    
    
    
    
    