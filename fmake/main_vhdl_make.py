import sys
from fmake.vhdl_programm_list import get_function,  print_list_of_programs
from fmake import get_project_directory
from pathlib import Path
from fmake.user_program_runner import run_fmake_user_program,parse_args_to_kwargs
from fmake.generic_helper import set_project_directory
    
def main_vhdl_make():


    if len(sys.argv) > 1 and sys.argv[1] == "--path":
        if len(sys.argv) < 3:
            print("not enough arguments for --path")
            return 
        p = Path(sys.argv[2])
        if not p.is_dir():
            print("given path is not a directory")
            return 
        set_project_directory(str(p.resolve()))

        sys.argv = [sys.argv[0]] + sys.argv[3:]

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
        ret = fun(*args, **kwargs)
        if ret is not None:
            print(str(ret))
        return

    print("unknown programm")
    print("\n\nFmake Programs:")
    print_list_of_programs(printer= print)
    print("\n\nUser programs:")
    for f,_,p in user_programs:
        print("File: " + f + ", program: " + p)
    

    
    
    
    
    