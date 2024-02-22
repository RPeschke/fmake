import pandas as pd
import numpy as np
import uproot
import argparse

from fmake.vhdl_programm_list import add_programm
import fmake.vhdl_load_file_without_comments as ld
from fmake.vhdl_dependency_db import  get_dependency_db

from  fmake.generic_helper               import save_file, try_make_dir, cl_add_entity, join_str
from  fmake.vhdl_programm_list           import add_programm 
from  fmake.generic_helper               import  vprint, extract_cl_arguments



def append_dataframe(df, df_append):
    df_append = df_append[[x for x in df_append.columns if x in df.columns]]
    df = pd.concat( [df, df_append] )
        
    df.fillna(0,inplace=True)
    return df


def make_input_table(FileName):
    src = ld.load_file_witout_comments(FileName )
    columns = [x.split("data.")[1].strip() for x in src.split(";") if "csv_from_integer" in x] 
    columns  = [ x[:x.rfind(")")].replace(" ", "") for x in columns]
    return  pd.DataFrame(columns= columns)


def read_file(fileName, branch):
    if fileName[-3:].lower() == "csv":
        df = pd.read_csv(fileName,comment='#',skip_blank_lines=True)
        df = df.rename(columns=lambda x: x.strip())
        return df
    
    if fileName[-4:].lower() == "root":
        up  = uproot.open(fileName)
        
        df =  up[branch].arrays(library="pd")
        df["valid"] = 1
        df = df.rename(columns=lambda x: x.strip())
        df = df.rename(columns=lambda x: (branch+ "." + x).lower())  
        return df
    
def make_empty_rows(df,numOfRows):
    line = ""
    for c in df.columns:
        line += str(0) + " "
    line+= "\n"
    
    ret = ""
    for _ in range(numOfRows):
        ret += line
    return ret

def write_csv_file(df,entity, event_axis ,empty_rows ):
    df = df.astype(int)
    empty_block = make_empty_rows(df, empty_rows)
    
    with open("build/" + entity +"/"+ entity +".csv" ,"w" ) as f:
        line = ""
        for c in df.columns:
            line += c + " "
        f.write(line + '\n' )
        f.write(line + '\n' )
        
        old_event_axis = 0
        for i,x in df.iterrows():
            line = ""
            if old_event_axis != x[event_axis]:
                f.write(empty_block)
            old_event_axis = x[event_axis]                               
            for c in df.columns:
                line += str(x[c]) + " "
            
            f.write(line + '\n' )
        
def make_input_file(entity, file_list ,branch , event_axis ,empty_rows):

    fileList = get_dependency_db().get_dependencies(entity)
    vprint(1)(fileList[0])
    df = make_input_table(fileList[0])
    df = df.rename(columns=lambda x: x.strip())

    for x in file_list:
        df1 = read_file(x,branch)
        df = append_dataframe(df , df1)
    
    
    write_csv_file(df, entity , event_axis,empty_rows)

    



def make_input_file_wrap(x):
    parser = argparse.ArgumentParser(description='Creates stimulus file from csv files and root files')
    
    cl_add_entity(parser)
    parser.add_argument('--filelist', help='Path to where the test bench should be created',default="" ,required=True ,  nargs='+')
    parser.add_argument('--branch', help='Number of Rows in the Autogenerated CSV Files',default="KLMDigits")
    parser.add_argument('--event_axis', help='Number of Rows in the Autogenerated CSV Files',default="inklmdigits.event_nr")
    parser.add_argument('--empty_rows', help='Number of Rows in the Autogenerated CSV Files',default="200")
    
    args = extract_cl_arguments(parser= parser,x=x)
    print(args.filelist)
    
    make_input_file(    entity  = args.entity , file_list = args.filelist , branch = args.branch, event_axis=args.event_axis ,empty_rows = int(args.empty_rows))

add_programm("make-stimulus",make_input_file_wrap )