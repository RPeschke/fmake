
import os

import pandas as pd

from .vhdl_get_list_of_files import getListOfFiles




from fmake.vhdl_load_file_without_comments import load_file_witout_comments



from fmake.generic_helper import  vprint



    

       
def vhdl_parser(FileName, ret1={}):
    
    
    
    Modified= os.path.getmtime(FileName)
    
    FileContent=load_file_witout_comments(FileName)
    
    entityDef=findDefinitionsInFile(FileContent," entity ","is")
    
    ret1["symbols"].extend([
        [ FileName , "entityDef", x,Modified ]   
        for x in entityDef 
    ])
    
    Type_Def=findDefinitionsInFile(FileContent," type ","is")
    subType_Def=findDefinitionsInFile(FileContent," subtype ","is")
    
    
    ret1["symbols"].extend([
        [FileName , "Type_Def", x,Modified]   
        for x in Type_Def + subType_Def 
    ])




    packageDef=findDefinitionsInFile(FileContent," package ","is")
    
    ret1["symbols"].extend(  [ 
        [ FileName , "packageDef", x , Modified]   
        for x in packageDef  
    ])

    packageUSE=findDefinitionsInFile(FileContent,"work.","all",".")
    
    
    ret1["symbols"].extend([
        [ FileName , "packageUSE", x , Modified]   
        for x in packageUSE  
    ])



    entityUSE_G=findDefinitionsInFile(FileContent," entity ","generic")
    entityUSE=findDefinitionsInFile(FileContent," entity ","port")
    entityUSE2=findDefinitionsInFile(FileContent," entity ","(")
    
    ret1["symbols"].extend([
        [ FileName , "entityUSE", x,Modified ]   
        for x in entityUSE + entityUSE_G +entityUSE2  
    ])
    
    ComponentUSE=findDefinitionsInFile(FileContent," component ","is")
    ComponentUSE_G=findDefinitionsInFile(FileContent," component ","generic")
    ComponentUSE_P=findDefinitionsInFile(FileContent," component ","port")
    
    ret1["symbols"].extend([
        [ FileName , "ComponentUSE", x ,Modified]   
        for x in ComponentUSE +ComponentUSE_G +ComponentUSE_P  
    ])
    
    


def findDefinitionsInFile(FileContent,prefix,suffix,delimiter=" ",offset = 0):
    ret=[]


    entity_cantidates = FileContent.split(prefix)
    for x in entity_cantidates[1:]:
        
        words = x.strip().split(delimiter)
        words = list(filter(None, words)) 
        if len(words)  > 1 + offset and   suffix in words[1 +offset][0:10] and words[0 +offset].strip() not in ret:
            ret.append(words[0 +offset].strip())
            
    
    return ret




def vhdl_parse_folder( Folder = ".", verbose = False):
    ret1 ={
        "symbols" : [],

    }
    flist = getListOfFiles(Folder,"*.vhd")
    for f in flist:
        vprint(1)("process file: ",f)
        
        try:
            vhdl_parser(f,ret1)
        except:
            vprint(1)("Error in file: ", f)
            



    

    df = pd.DataFrame(ret1["symbols"], 
        columns = [
            "filename",
            "type",
            "name",
            "data"
        ]
    )
    df["name"] = df.apply(lambda x: x["name"].replace("work.",""), axis=1)
     

     
    vprint(1) ( '</vhdl_parse_folder>')
    
    return df


