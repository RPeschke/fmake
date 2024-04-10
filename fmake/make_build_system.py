from fmake.vhdl_programm_list import add_program
from fmake.generic_helper import  extract_cl_arguments, try_make_dir, save_file, constants
import argparse

import fmake.vhdl_csv_io as csv_io


def make_build_wrap(x):
    parser = argparse.ArgumentParser(description='Excel To CSV Converter')
    args = extract_cl_arguments(parser , x)
    
    build = constants.default_build_folder
    try_make_dir(build)
    save_file( build + "/fmake.txt",  "")
    save_file( build + "/.gitignore",  "*\n!.gitignore\n")
    save_file( build + "/vivado_path.txt",  "C:/Xilinx/Vivado/2021.2/settings64.bat")
    
    
    try_make_dir(build + "/vhdl_csv_io")
    
    save_file(build + "/vhdl_csv_io/ClockGenerator.vhd",  csv_io.ClockGenerator)
    save_file(build + "/vhdl_csv_io/CSV_UtilityPkg.vhd",  csv_io.CSV_UtilityPkg)
    save_file(build + "/vhdl_csv_io/e_csv_read_file.vhd",  csv_io.e_csv_read_file)
    save_file(build + "/vhdl_csv_io/e_csv_write_file.vhd",  csv_io.e_csv_write_file)
    save_file(build + "/vhdl_csv_io/type_conversions_helper.vhd",  csv_io.type_conversions_helper)
    save_file(build + "/vhdl_csv_io/csv_text_io_poll.vhd",  csv_io.csv_text_io_poll)
    
    
    
    
    
    
    
    
    
    

add_program("make-build", make_build_wrap)   