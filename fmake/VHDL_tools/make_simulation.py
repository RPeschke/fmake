import os

import argparse
from fmake.generic_helper import try_make_dir,save_file,load_file, cl_add_entity

from fmake.VHDL_tools.dependency_db  import get_dependency_db


from fmake.programm_list import  add_program
from fmake.generic_helper import constants

from fmake.generic_helper import  vprint, extract_cl_arguments

def make_query_pkg(packagename, path):
    return """


library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;

package {packagename} is

    constant query_folder           : string  := "{path}/";

end package;

""".format(
        packagename=packagename, 
        path=  path 
    )


def make_simulation_query_interface(entity, BuildFolder = constants.default_build_folder):
    OutputPath = BuildFolder + entity + "/"
    query_folder = OutputPath+ constants.text_IO_polling + "/"
    
    try_make_dir(query_folder)
    
    save_file(query_folder + constants.text_io_polling_send_lock_txt ,"0")
    save_file(query_folder + constants.text_io_polling_receive_lock_txt ,
"""Time, N
0,     0
""")
    save_file(query_folder + constants.text_io_polling_send_txt,    "")
    save_file(query_folder + constants.text_io_polling_receive_txt ,"")    

    query_pkl = query_folder + entity + "_text_io_query_pkg.vhd"
    save_file(query_pkl,
               make_query_pkg( 
                   packagename=entity+"_text_io_query_pkg",
                   path= os.path.abspath( query_folder ).replace("\\","/")   
               )
    )
    ret = {}
    ret["OutputPath"] = OutputPath
    ret["query_folder"] = query_folder
    ret["query_pkl"] = query_pkl
    return ret


def vhdl_make_simulation_intern(entity,BuildFolder = constants.default_build_folder ):  
    ret ={} 
    OutputPath = BuildFolder + entity + "/"
    
    CSV_readFile=OutputPath+entity+".csv" 
    CSV_writeFile=OutputPath+entity+"_out.csv" 

    try_make_dir(OutputPath)
    
    save_file(CSV_readFile,"")
    save_file(CSV_writeFile,"")
    save_file(OutputPath+"clock_speed.txt","10")

    query_interface_ret = make_simulation_query_interface(entity, BuildFolder = BuildFolder)
    



    ret["CSV_readFile"] = CSV_readFile
    ret["CSV_writeFile"] = CSV_writeFile
    ret["OutputPath"] = OutputPath
    ret["query_folder"] = query_interface_ret["query_folder"]
    ret["query_pkl"] = query_interface_ret["query_pkl"]
    
    return ret



def extract_header_from_top_file(Entity, FileName,BuildFolder):
    vprint(1)("=======Extracting Header From File========")
    vprint(1)(FileName)

    Content =load_file(FileName)
    
    
    h1 = Content.split("</header>")
    if len(h1)>1:
        Content=h1[0].split("<header>")[1]+"\n"
    else:
        Content=""

    header_file = BuildFolder+Entity+ "/"+ Entity +"_header.txt"
    save_file(header_file, Content)
    vprint(1)("=======Done Extracting Header From File====")
    return header_file


def make_simulation(Entity, BuildFolder = constants.default_build_folder):
    





    ret = vhdl_make_simulation_intern(Entity,BuildFolder)


    fileList = get_dependency_db().get_dependencies_and_make_project_file(Entity, OutDict = ret)
    
    if len(fileList)==0:
        vprint(1)("unable to find entity: ", Entity)
        return ret
    
    

    header_file = extract_header_from_top_file(Entity, fileList[0],BuildFolder)
    ret["header_file"] = header_file


    return ret


def vhdl_make_simulation_wrap(x):
    parser = argparse.ArgumentParser(description='make project files etc. for the simulation')
    cl_add_entity(parser)

    args = extract_cl_arguments(parser= parser,x=x)
    vprint(0)('Make-Simulation for Entity: ' , args.entity)
    make_simulation(args.entity)
    vprint(0)('Done Make-Simulation')
    
    
add_program("make-simulation", vhdl_make_simulation_wrap)