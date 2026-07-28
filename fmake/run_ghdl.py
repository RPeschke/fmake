import argparse
import os


from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint
from fmake.generic_helper import extract_cl_arguments, cl_add_entity,  constants




def run_ghdl_wrap(x):
    parser = argparse.ArgumentParser(description='run_ghdl simulation')
    cl_add_entity(parser)
    args = extract_cl_arguments(parser, x)
    build_path = constants.default_build_folder+"/" +args.entity+"/"
    
    cmd = "cd " + build_path + " && make " 
    vprint(2)("command: " + cmd) 
    os.system( cmd )

add_program("run-ghdl", run_ghdl_wrap )