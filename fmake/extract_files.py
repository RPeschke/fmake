import zipfile

import shutil
import os
from  fmake.vhdl_programm_list           import add_program 
from  fmake.generic_helper               import  vprint, extract_cl_arguments, constants
import argparse

build_folder = constants.default_build_folder

def extract_bitfiles(in_zip_file, ouput_path = None):
    basename = os.path.basename(in_zip_file) 
    out_folder = build_folder+basename+"/zip/"
    try:
        os.mkdir(build_folder+basename )
        os.mkdir(out_folder)
    except:
        pass
    with zipfile.ZipFile(in_zip_file,"r") as zip_ref:
        zip_ref.extractall(out_folder)
        
        
    dir_hwh = [x for x in  os.listdir(out_folder) if ".hwh" in  x ]
    dir_bit= [x for x in  os.listdir(out_folder) if  ".bit" in x ]
    vprint(2)(dir_bit)
    vprint(2)(dir_hwh)

    if len(dir_bit) != 1:
        vprint(2)("error")
        return
        
    if len(dir_bit) != 1:
        vprint(2)("error")
        return
    ouput_hwh = build_folder+basename +"/"+dir_bit[0][:-4] + ".hwh" 
    output_bit = build_folder+basename +"/"+dir_bit[0] 
    shutil.move(out_folder + dir_bit[0], output_bit )
    shutil.move(out_folder + dir_hwh[0], ouput_hwh  )
    
    if ouput_path is None:
        return
    
    shutil.copy(output_bit, ouput_path)
    shutil.copy(ouput_hwh,  ouput_path)
    
    
def extract_bitfiles_wrap(x):
    parser = argparse.ArgumentParser(description='Creates Test benches for a given entity')
    
    
    parser.add_argument('--xsa', help='',default="" ,required=True)
    parser.add_argument('--out', help='',default= None)
    args = extract_cl_arguments(parser= parser,x=x)
    extract_bitfiles(args.xsa, args.out)
    


add_program("extract-xsa", extract_bitfiles_wrap)   
    
      