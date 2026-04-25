import argparse
import os
import shutil 
import platform

from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint, try_remove_file , save_file , load_file 
from fmake.generic_helper import extract_cl_arguments, cl_add_entity , cl_add_OutputCSV, cl_add_gui , cl_add_run_infinitly, constants




def run_ghdl_wrap(x):
    parser = argparse.ArgumentParser(description='run_ghdl simulation')
    cl_add_entity(parser)
    args = extract_cl_arguments(parser, x)
    build_path = constants.default_build_folder+"/" +args.entity+"/"
    
    cmd = "cd " + build_path + " && make " 
    vprint(2)("command: " + cmd) 
    os.system( cmd )

add_program("run-ghdl", run_ghdl_wrap )