import sys
from fmake.vhdl_programm_list import get_function,  print_list_of_programs

    
    
def main_vhdl_make():
    if len(sys.argv) < 2:
        print("not enough arguments")
        print("use one of these programms:")
        print_list_of_programs(printer= print)
        return 
    
    program = sys.argv[1]
    fun = get_function(program)
    if fun is None:
        print("unknown programm")
        print_list_of_programs(printer= print)
        return
    
    fun(sys.argv)
    
    
    