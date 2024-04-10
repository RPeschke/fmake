import sys


from shutil import copyfile
import pandas as pd


import argparse
from fmake.vhdl_programm_list import add_program
from fmake.generic_helper import  extract_cl_arguments

from fmake.generic_helper import  vprint

def Convert2CSV(XlsFile,Sheet,OutputFile,drop):
    if XlsFile == "":
        return 
    data_xls = pd.read_excel(XlsFile, Sheet, index_col=None)
    vprint(1)(data_xls.columns)
    for d in drop:
        try:
            data_xls.drop(d, axis=1, inplace=True)
        except:
            pass
            vprint(0)("unable to drop column",d)
    data_xls.to_csv(OutputFile, encoding='utf-8',index =False, sep=" ") 
    
    
def Convert2CSV_args(args, OutputCSV):
    if args.InputXLS.split(".")[-1].lower() == "csv":
        copyfile( args.InputXLS , OutputCSV)
    else:
        drop = args.Drop.split(",") if args.Drop else []
        Convert2CSV(args.InputXLS,args.SheetXLS,OutputCSV,drop)
    
def Convert2CSV_add_CL_args(parser):
    parser.add_argument('--InputXLS',   help='Path to the input file',default="")
    parser.add_argument('--SheetXLS',   help='Sheet inside the XLS file',default="Simulation_Input")
    parser.add_argument('--Drop',   help='drops columns from data frame',default='')
    parser.add_argument('--InputCSV',   help='Path to the input file',default="")
    

def excel_to_csv_wrap(x):
    parser = argparse.ArgumentParser(description='Excel To CSV Converter')
    Convert2CSV_add_CL_args(parser)
    parser.add_argument('--OutputCSV',    help='Path to the output',default="test.csv")
    args = extract_cl_arguments(parser , x)
    
    vprint(2)("\nargs.InputXLS: ",args.InputXLS,"\nargs.SheetXLS",args.SheetXLS,"\nargs.OutputCSV",args.OutputCSV)
    Convert2CSV_args(args, args.OutputCSV)
    vprint(1)("done Converting")

add_program("excel2csv", excel_to_csv_wrap)    