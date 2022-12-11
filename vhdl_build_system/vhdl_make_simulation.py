import os

import argparse
from vhdl_build_system.generic_helper import try_make_dir,save_file,load_file, cl_add_entity

from vhdl_build_system.vhdl_dependency_db  import get_dependency_db


from vhdl_build_system.vhdl_programm_list import  add_programm

from vhdl_build_system.generic_helper import  vprint, extract_cl_arguments

def vhdl_make_simulation_intern(entity,BuildFolder = "build/"):  
    OutputPath = BuildFolder + entity + "/"
    
    CSV_readFile=OutputPath+entity+".csv" 
    CSV_writeFile=OutputPath+entity+"_out.csv" 
    try_make_dir(OutputPath)
    
    save_file(CSV_readFile,"")
    save_file(CSV_writeFile,"")
    save_file(OutputPath+"clock_speed.txt","10")

   





def extract_header_from_top_file(Entity, FileName,BuildFolder):
    vprint(1)("=======Extracting Header From File========")
    vprint(1)(FileName)

    Content =load_file(FileName)
    
    
    h1 = Content.split("</header>")
    if len(h1)>1:
        Content=h1[0].split("<header>")[1]+"\n"
    else:
        Content=""

    save_file(BuildFolder+Entity+ "/"+ Entity +"_header.txt", Content)
    vprint(1)("=======Done Extracting Header From File====")


def vhdl_make_simulation(Entity,BuildFolder = "build/"):

    
    fileList = get_dependency_db().get_dependencies_and_make_project_file(Entity)
    if len(fileList)==0:
        vprint(1)("unable to find entity: ", Entity)
        return 
    
    extract_header_from_top_file(Entity, fileList[0],BuildFolder)


    vhdl_make_simulation_intern(Entity,BuildFolder)


def vhdl_make_simulation_wrap(x):
    parser = argparse.ArgumentParser(description='make project files etc. for the simulation')
    cl_add_entity(parser)
    args = extract_cl_arguments(parser= parser,x=x)
    vprint(0)('Make-Simulation for Entity: ' , args.entity)
    vhdl_make_simulation(args.entity)

add_programm("make-simulation", vhdl_make_simulation_wrap)