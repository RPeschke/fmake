import os
import time
from datetime import datetime
from fmake.vhdl_programm_list import add_program
import argparse
from fmake.generic_helper import  extract_cl_arguments, save_file

def generate_vhdl_package(package_name):
        now = datetime.now()
        vhdl_content = f"""
    library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;

    package {package_name} is
        type time_record is record
            year   : std_logic_vector(15 downto 0);
            month  : std_logic_vector( 7 downto 0);
            day    : std_logic_vector( 7 downto 0);
            hour   : std_logic_vector( 7 downto 0);
            minute : std_logic_vector( 7 downto 0);
        end record;

        constant current_time : time_record := (
            year   => x"{now.year:04d}",
            month  => x"{now.month:02d}",
            day    => x"{now.day:02d}",
            hour   => x"{now.hour:02d}",
            minute => x"{now.minute:02d}"
        );
    end package;
        """
        return vhdl_content

def make_ts(filename, package_name, RunInf):
    save_file(filename, generate_vhdl_package(package_name) )
    # Main loop to generate VHDL package files every 10 minutes
    while RunInf:
        time.sleep(600)  # Sleep for 600 seconds (10 minutes)
        save_file(filename, generate_vhdl_package(package_name) )



def make_ts_wrap(x):
    parser = argparse.ArgumentParser(description='Generates Record with time stamp')
    parser.add_argument('--file',  help='output VHDL file', required=True)
    parser.add_argument('--package',   help='name of the package generated in the VHDL file default: time_pkg',default='time_pkg')
    parser.add_argument('--inf', help='Run continuously (infinite) until terminate using ctrl-c', action='store_true')
    args = extract_cl_arguments(parser , x)
    make_ts(
        filename = args.file, 
        package_name = args.package, 
        RunInf = args.inf
    )



add_program("make-ts", make_ts_wrap)   