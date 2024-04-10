import argparse
import os
import shutil 
import platform

from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint, try_remove_file , save_file , load_file 
from fmake.generic_helper import extract_cl_arguments, cl_add_entity , cl_add_OutputCSV, cl_add_gui , cl_add_run_infinitly, constants

from fmake.Convert2CSV import Convert2CSV , Convert2CSV_add_CL_args



def make_tcl_file(entity_name, intermediate_csv,tcl_file, do_quit = "" , run_infinitly = False):
    onerror = '{' +'resume}'
    clock_speed_file= constants.default_build_folder +"/" +entity_name+"/"+"clock_speed.txt"
    clock_speed=int(load_file(clock_speed_file))
    line_count=0
    try:
        line_count =  load_file(intermediate_csv, lambda x : len(x.readlines()) )
    except:
        vprint(1)("File not found: " , intermediate_csv)
    runtime= "run all" if run_infinitly else "run "+ str( clock_speed * max(line_count , 1)  )+ " ns"
    save_file(tcl_file, 
"""onerror {resume} 
wave add /
{runtime} 
{do_quit}
""".format(
        resume = onerror,
        runtime  = str(runtime),
        do_quit= do_quit
    ))

    
def run_in_bash(cmd):
    if  platform.system() == "Windows":
        cmd = 'bash -i -c "' + cmd + '"' 
    return cmd

def run_ise(entity_name, input_xls, Sheet, ouput_csv, drop,ise_path, Run_with_gui = False ,run_infinitly = False ):
    ise_path = load_file( ise_path  ).strip()
    build_path = constants.default_build_folder+"/" +entity_name+"/"
    intermediate_csv = build_path + entity_name+ ".csv"
    programm_name = entity_name+".exe"
    project_name = entity_name+".prj"
    tclbatchfile = "isim.cmd"
    outFile_full_path= build_path + entity_name +"_out.csv"
    tcl_do_quit = "" if Run_with_gui else "quit -f;"
    cmd_arg_gui = " -gui &" if Run_with_gui else ""
    
    
    
    if input_xls!= "":
        try_remove_file(intermediate_csv)
        Convert2CSV( input_xls, Sheet,intermediate_csv, drop )
    
    cmd = run_in_bash("pkill -f " +programm_name)   
    vprint(2)("command: " + cmd) 
    os.system(cmd )
    
    def build_program():
        if  Run_with_gui:
            return
        try_remove_file(build_path + programm_name )
        cmd = "source " + ise_path + " && cd " + build_path + " && " + "fuse -intstyle ise -incremental -lib secureip -o " + programm_name+ " -prj "+ project_name + "  work." + entity_name
        cmd = run_in_bash(cmd)
        vprint(2)("command: " + cmd)
        os.system(cmd)
    
    
    build_program()
    
    def run_program():
        make_tcl_file( entity_name , intermediate_csv, build_path+tclbatchfile, do_quit = tcl_do_quit , run_infinitly = run_infinitly )
        cmd = "source " +  ise_path + " && cd "+ build_path+ " && ./" + programm_name + " -intstyle ise -tclbatch " +tclbatchfile + cmd_arg_gui
        cmd = run_in_bash(cmd)
        vprint(2)("command: " + cmd)
        os.system(cmd )
        
    run_program()
    
    if ouput_csv!="":
        vprint(2)("copy file: " + outFile_full_path +" --> "+ ouput_csv )
        shutil.copy(outFile_full_path, ouput_csv)
    

    
    
def run_ise_wrap(x):
    parser = argparse.ArgumentParser(description='run_ise_wrap')
    cl_add_entity(parser)
    cl_add_OutputCSV(parser)
    cl_add_gui(parser=parser)
    cl_add_run_infinitly(parser=parser)
    parser.add_argument('--ise_path', help='Path to the vivado settings64.bat file',default= constants.default_build_folder + "/ise_path.txt")

    Convert2CSV_add_CL_args(parser)
    
    args = extract_cl_arguments(parser, x)
    
    run_ise(entity_name=args.entity, input_xls=args.InputXLS, Sheet=args.SheetXLS, ouput_csv=args.OutputCSV, drop = args.Drop , Run_with_gui= args.run_with_gui, ise_path = args.ise_path, run_infinitly = args.run_infinitly)
    
add_program("run-ise", run_ise_wrap )