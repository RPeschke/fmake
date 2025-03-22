import sys
from fmake.vhdl_programm_list import get_function,  print_list_of_programs
from fmake import get_project_directory
from pathlib import Path
from fmake.user_program_runner import run_fmake_user_program
    
def main_vhdl_make():
    if len(sys.argv) < 2:
        print("not enough arguments")
        print("use one of these programms:")
        print_list_of_programs(printer= print)
        return 
    
    program = sys.argv[1]
    fun = get_function(program)
    
    if fun is None:
        try:
            status, user_programs = run_fmake_user_program(sys.argv)
            if status == False:
                print("unknown programm")
                print("Fmake Programs:")
                print_list_of_programs(printer= print)
                print("User programs:")
                for f,_,p in user_programs:
                    print("File: " + f + ", program: " + p)
                return
        except:
            
            print("unknown programm")
            print("Fmake Programs:")
            print_list_of_programs(printer= print)
            print("unable to load user programs")
            return
    
    fun(sys.argv)
    
    
    