from fmake.generic_helper import try_make_dir, save_file, try_load_file,load_file, cl_add_entity
from  fmake.vhdl_make_simulation import vhdl_make_simulation
from fmake.vhdl_get_list_of_files import getListOfFiles
from fmake.vhdl_programm_list import  add_program
from fmake.generic_helper import  vprint, extract_cl_arguments, constants

from fmake.makeise.makeise import do_makeise


from shutil import copyfile

import wget
import argparse

def File_get_base_name(FullName,DotIndex = -2):
    baseName = FullName.replace("\\","/").split("/")[-1].split(".")[DotIndex]
    return baseName

def FileBaseNameNotInList(FullName,FileList,DotIndex = -2):
    baseName = File_get_base_name(FullName,DotIndex)
    for x in FileList:
        x = File_get_base_name(x,DotIndex)
        if baseName == x:
            return False
    return True


def get_proto_project(build_path, Entity):
    proto_Project = build_path+"/"+Entity + "/" +Entity + "_proto_Project.in"
    f = try_load_file(proto_Project)
    if f is None:
        URL =constants.proto_Project_url
        response = wget.download(URL, proto_Project)
        f = load_file(proto_Project)
        
    return f  


def get_template( simpleTemplate_path ):
    
    f = try_load_file(simpleTemplate_path)
    if f is None:
        URL = constants.xise_prototype_url
        response = wget.download(URL, simpleTemplate_path)

   
    
def load_file_list_from_prj(project_file_path , veto_IPcoreList, veto_IPcoreList_in):
    ret = ""
    with open(project_file_path) as f:
        
        
        for x in f:
            spl = x.split('"')
            if len(spl) > 1 and FileBaseNameNotInList(spl[1],veto_IPcoreList) and FileBaseNameNotInList(spl[1],veto_IPcoreList_in,0):
                ret += spl[1] + "\n"
    return ret
       
       
def make_IPcoreList_str(IPcoreList):
    IPcoreList_str = ""
    used_ip_cores =list()
    for x in IPcoreList:
        x = File_get_base_name(x)
        if x not in used_ip_cores:
            used_ip_cores.append(x)
            IPcoreList_str  += "./"+ x+".xco\n"
    return IPcoreList_str

def make_IPcoreList_in_str(IPcoreList_in):
    IPcoreList_in_str =""   
    used_IP = []
    for x in IPcoreList_in:
        x1 = File_get_base_name(x,0)
        if x1 in used_IP:
            continue
        used_IP.append(x1)
        IPcoreList_in_str+= x1 + ".xco = " + x1 + "\n"   
    return IPcoreList_in_str

def make_IPcoreList_in2_str(IPcoreList_in):
    ret = ""
    used_IP = []
    for x in IPcoreList_in:

        x1 = File_get_base_name(x,0)
        if x1 in used_IP:
            continue
        used_IP.append(x1)
        ret +="[" + x1 + "]\n"
        ret += "InputFile = ../../" + x + "\n\n"
    return ret
        
def copy_ipcore_file(IPcoreList, build_path, outPath):
    for x in IPcoreList:
        if build_path not in x:
            copyfile(x, outPath + x.split("/")[-1])

    
def vhdl_make_implementation(Entity, UCF_file):
    build_path =  constants.default_build_folder
  
    Entity_build_path = build_path+  Entity +"/"
    project_file_path = Entity_build_path + Entity+ ".prj"
    xise_file_path = Entity_build_path + Entity+ ".xise"
    outPath = Entity_build_path +'/coregen/'
    
    try_make_dir(build_path+"/"+Entity)
    proto_Project =get_proto_project (build_path , Entity )
    
    simpleTemplate_path = build_path+"/"+Entity+'/'+ "simpleTemplate.xise.in"
    get_template(simpleTemplate_path)
    
    
    vhdl_make_simulation(Entity, build_path)





    IPcoreList_in = getListOfFiles(".","*.xco.in")
    
    IPcoreList = getListOfFiles(".","*.xco")
    IPcoreList = [x for x in IPcoreList if build_path not in x]

    
    
    IPcoreList = [x for x in IPcoreList if FileBaseNameNotInList(x, IPcoreList_in,0)]
    vprint(1)(IPcoreList)
    vprint(1)(IPcoreList_in)
    
    try_make_dir(outPath)

    copy_ipcore_file(IPcoreList, build_path, outPath)

    

    files  = load_file_list_from_prj(project_file_path, IPcoreList, IPcoreList_in )
        
    IPcoreList_str = make_IPcoreList_str(IPcoreList)

    
    IPcoreList_in_str =make_IPcoreList_in_str(IPcoreList_in)
    IPcoreList_in2_str = make_IPcoreList_in2_str(IPcoreList_in)

    
    vprint(1)(proto_Project)

    project_file_content = """
{proto_Project}
InputFile = simpleTemplate.xise.in


[UCF Files]
#Normally just one UCF file
# ../../{UCF_file}


[VHDL Files]
#List of VHDL source files... by default added for sim + implementation
{files}
        
       


[CoreGen Files]
#Add XCO files. You can just list the filename, OR have the CoreGen files be
#auto-generated as well by specifying the section name
#fifoonly_adcfifo.xco = ADC FIFO CoreGen Setup

{IPcoreList}

{IPcoreList_in}

{IPcoreList_in2}

#[ADC FIFO CoreGen Setup]
#InputFile = fifoonly_adcfifo.xco.in
#input_depth = 8192
#output_depth = CALCULATE $input_depth$ / 4
#full_threshold_assert_value = CALCULATE $input_depth$ - 2
#full_threshold_negate_value = CALCULATE $input_depth$ - 1
##These are set to 16-bits for all systems... overkills most of the time
#write_data_count_width = 16
#read_data_count_width = 16
#data_count_width = 16


#[Setup File]
#AVNET
#UART_CLK = 40000000
#UART_BAUD = 512000

    """.format(
        proto_Project = proto_Project,
        Entity = Entity, 
        UCF_file = UCF_file,
        files = files,
        IPcoreList = IPcoreList_str,
        IPcoreList_in = IPcoreList_in_str,
        IPcoreList_in2 = IPcoreList_in2_str
    )
    
    make_ise_file =  Entity_build_path+Entity+".in"
    save_file(make_ise_file  , project_file_content)
    return make_ise_file , xise_file_path
    
    
def vhdl_make_implementation_wrap(x):
    

    parser = argparse.ArgumentParser(description='make project files etc. for the simulation')
    cl_add_entity(parser)
    parser.add_argument('--ucf',      help='ucf file path',default="",required=True)
    args = extract_cl_arguments(parser= parser,x=x)
    vprint(0)('Make-implementation for Entity: ' , args.entity)
    inputfile, xise_file_path = vhdl_make_implementation(args.entity, args.ucf)
    do_makeise( inputfile , xise_file_path)
    

add_program("make-implementation", vhdl_make_implementation_wrap)