import sys
from fmake.programm_list import get_function,  print_list_of_programs

from pathlib import Path
from fmake.user_program_runner import  parse_args_to_kwargs, print_user_program_table , get_list_of_user_programs, get_program
from fmake.generic_helper import set_project_directory
import inspect
import fmake

import traceback

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
        user_programs = get_list_of_user_programs(keyword="program")
        print("\n\nUser programs:")
        print_user_program_table(user_programs)
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
    fun = None
    try:
        fun = get_program(program, keyword="program")
    except:
        pass 

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
        except Exception as e:
            print(e)
            print("Call stack (project files only):")
            
            fmake_root = Path(fmake.__file__).resolve().parent
            tb_frames = traceback.extract_tb(e.__traceback__)
            filtered_frames = [
                frame
                for frame in tb_frames
                if not Path(frame.filename).resolve().is_relative_to(fmake_root)
            ]
            if filtered_frames:
                print("Traceback (most recent call last):")
                for frame in filtered_frames:
                    print(
                        f'  File "{frame.filename}", line {frame.lineno}, in {frame.name}'
                    )
                    if frame.line:
                        print(f"    {frame.line.strip()}")
            else:
                print("  No project-local frames found.")
            return True
    return False

def handle_unknown_program():

    print("unknown programm")
    print("\n\nFmake Programs:")
    print_list_of_programs(printer= print)
    print("\n\nUser programs:")
    user_programs = get_list_of_user_programs()
    print_user_program_table(user_programs)

    


def fmake_main():
    handle_path_argument()

    if  handle_not_enough_arguments():
        return
    
   
    


       
        
    if handle_builtin_programs():
        return
    

    if handle_user_programs():
        return
    
    
    handle_unknown_program()
    
    
    

