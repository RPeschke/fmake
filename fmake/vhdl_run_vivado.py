import os
import shutil

import pandas as pd
import argparse

from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint,  save_file , load_file 


from fmake.generic_helper import extract_cl_arguments, cl_add_entity , cl_add_gui, constants








def vivado_run(args):
    vivado_path = load_file(args.vivado_path)
    vprint.level = int( args.verbosity)
    entity_name =  args.entity
    
    path =  constants.default_build_folder +"/" +entity_name+"/"

    clock_speed = load_file( path +"/clock_speed.txt"  )
    clock_speed = int(clock_speed)

    if "ns" in args.time:
        time = int(args.time.split("ns")[0])
    elif "clk" in args.time:
        time = int(args.time.split("clk")[0])*clock_speed
            

    
    

    
   
    vprint(1)("time: ", args.time , "time in ns ", time)
    save_file(path+ "/run.tcl", 
"""run {time} ns
{quit123}
""".format(
    time = str( max( time  , 0) ),
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
    

    
    



def vivado_run_wrap(x):
    parser = argparse.ArgumentParser(description='Run Entity in vavado simulator')
    cl_add_entity(parser)
    vprint(0)("hello from run-vivado")
    parser.add_argument('--time',   help='time in ns or clk example: 100ns or 100clk',default="100clk")
    

    cl_add_gui(parser=parser)
    
    parser.add_argument('--vivado_path', help='Path to the vivado settings64.bat file',default= constants.default_build_folder + "/vivado_path.txt")
    args = extract_cl_arguments(parser, x)

    vivado_run(args= args)
    

add_program("run-vivado", vivado_run_wrap)


    