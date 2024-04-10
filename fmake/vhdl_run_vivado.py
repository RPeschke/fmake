import os
import shutil

import pandas as pd
import argparse

from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint, try_remove_file , save_file , load_file 


from fmake.generic_helper import extract_cl_arguments, cl_add_entity ,cl_add_OutputCSV, cl_add_gui, constants

from fmake.Convert2CSV import Convert2CSV , Convert2CSV_add_CL_args 






def vivado_run(args):
    vivado_path = load_file(args.vivado_path)
    vprint.level = int( args.verbosity)
    entity_name =  args.entity
    
    path =  constants.default_build_folder +"/" +entity_name+"/"
    intermediate_csv = path + entity_name + ".csv"
    clock_speed = load_file( path +"/clock_speed.txt"  )
    clock_speed = int(clock_speed)
    
    if args.OutputCSV != "":
        vprint(1)("removed old output file: " , args.OutputCSV)
        try_remove_file(args.OutputCSV, lambda : vprint(1)("File not found"))
    
    
    
    if args.InputXLS != "":
        vprint(1)( "loaded  " + args.InputXLS +" -> " + intermediate_csv)
        Convert2CSV(args.InputXLS, args.SheetXLS, intermediate_csv ,args.Drop)
        
    if args.InputCSV != "":
        vprint(1)( "loaded  " + args.InputCSV +" -> " + intermediate_csv)
        shutil.copyfile(args.InputCSV, intermediate_csv)
    
    l = load_file(intermediate_csv, lambda x : len(x.readlines()) )
    vprint(1)("lines: ",l, "time in ns ", l*clock_speed)
    save_file(path+ "/run.tcl", 
"""run {time} ns
{quit123}
""".format(
    time = str( max( (l-10) ,0) *clock_speed ),
    quit123 =  "" if args.run_with_gui else "quit"               
            ))

    vivado_path = " && " + vivado_path if vivado_path != "" else ""
    cmd = """cd {build}/{entity_name}  {vivado_path} && xelab  {entity_name} -prj  {entity_name}.prj --debug all && xsim work.{entity_name}  -t run.tcl  {gui}""".format(
        build = constants.default_build_folder,
        entity_name = entity_name ,  
        vivado_path = vivado_path,
        gui = "-gui" if args.run_with_gui else "" 
    )
    vprint(1)("Run Command: " , cmd)
    os.system(cmd)
    
    if args.OutputCSV != "":
        vprint(1)("copy output file: " + path+ "/" + entity_name + "_out.csv  ->  " +   args.OutputCSV)
        shutil.copyfile(path+ "/" + entity_name + "_out.csv" , args.OutputCSV)
    
    



def vivado_run_wrap(x):
    parser = argparse.ArgumentParser(description='Run Entity in vavado simulator')
    cl_add_entity(parser)
    vprint(0)("hello from run-vivado")
    
    Convert2CSV_add_CL_args(parser)
    cl_add_OutputCSV(parser)
    cl_add_gui(parser=parser)
    
    parser.add_argument('--vivado_path', help='Path to the vivado settings64.bat file',default= constants.default_build_folder + "/vivado_path.txt")
    args = extract_cl_arguments(parser, x)

    vivado_run(args= args)
    

add_program("run-vivado", vivado_run_wrap)


    