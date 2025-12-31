import sys
from fmake.vhdl_programm_list import get_function,  print_list_of_programs
from fmake import get_project_directory
from pathlib import Path
from fmake.user_program_runner import run_fmake_user_program,parse_args_to_kwargs
from fmake.generic_helper import set_project_directory
import inspect



def handle_path_argument():
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
    

def handle_not_enough_arguments():
    if len(sys.argv) < 2:
        print("not enough arguments")
        print("\n\nFmake Programs:")
        print_list_of_programs(printer= print)
        _, user_programs = run_fmake_user_program("")
        print("\n\nUser programs:")
        for f,_,p in user_programs:
            print("File: " + f + ", program: " + p)
        return True

    return False

def handle_builtin_programs():

    program = sys.argv[1]
    fun = get_function(program)
    
    if fun is not  None:
        fun(sys.argv)
        return True
    return False
    

def handle_user_programs():
    program = sys.argv[1]
    

    fun, user_programs = run_fmake_user_program(program)
    if fun is not None:
        args, kwargs = parse_args_to_kwargs(sys.argv[2:])
        try:
            ret = fun(*args, **kwargs)
            if ret is not None:
                print(str(ret))
            return True
        except TypeError as e:
            print("Error when calling user program:")
            print(e)
            sig = inspect.signature(fun)
            
            print("Function " + program + " takes the following arguments:")
            for p in sig.parameters.values():
                if p.default is inspect._empty:
                    print(f"  {p.name}")
                else:
                    print(f"  {p.name} (default={p.default!r})")
                    
            
            return True
        
    return False

def handle_unknown_program():

    print("unknown programm")
    print("\n\nFmake Programs:")
    print_list_of_programs(printer= print)
    print("\n\nUser programs:")
    fun, user_programs = run_fmake_user_program("")
    for f,_,p in user_programs:
        print("File: " + f + ", program: " + p)

    


def main_vhdl_make():
    handle_path_argument()

    if  handle_not_enough_arguments():
        return
    
   
    


       
        
    if handle_builtin_programs():
        return
    

    if handle_user_programs():
        return
    
    
    handle_unknown_program()
    
    
    
    
    