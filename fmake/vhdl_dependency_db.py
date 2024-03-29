
import pandas as pd
from .vhdl_parser import vhdl_parse_folder 


from .generic_helper import save_file, try_make_dir,  first_diff_between_strings
from fmake.generic_helper import  vprint


class dependency_db_cl:
    def __init__(self,FileName) -> None:
        self.FileName = FileName
        self.filelist =[]
        self.IsInitilized = False
        
        self.df = None
        self.df_records = None
        self.df_constants = None
        
    def initilize(self):
        if self.IsInitilized:
            return

        self.IsInitilized = True
        self.reparse_files()
        self.df = pd.read_pickle(self.FileName + ".pkl")
        self.df_records = pd.read_pickle(self.FileName + "_records.pkl")
        self.df_constants = pd.read_pickle(self.FileName + "_constants.pkl")


    def reparse_files(self):
        if not  self.IsInitilized:
            raise Exception("dependency_db_cl not initilized")
        df,df_records,df_constants =  vhdl_parse_folder()
        df.to_pickle(self.FileName + ".pkl")
        df_records.to_pickle(self.FileName + "_records.pkl")
        df_constants.to_pickle(self.FileName + "_constants.pkl")


    def entity2FileName(self, entityName):
        if not  self.IsInitilized:
            raise Exception("dependency_db_cl not initilized")
        entity =  self.df[ (self.df["name"] == entityName.lower()) & ( self.df["type"] == "entityDef" )]["filename"].iloc[0]
        return entity

    def get_dependencies(self, Entity):
        if not  self.IsInitilized:
            raise Exception("dependency_db_cl not initilized")
        df = self.df
        df = df[df["filename"].apply( lambda  x: ".vhd" in x) == True]
        df_entity_def = df[df["type"] == "entityDef"]
        df_packageDef  = df[(df["type"] == "packageDef")]
        
        df_entities_USED = df[(df["type"] == "entityUSE")] 
        df_packageUSE = df[(df["type"] == "packageUSE")] 
        df_component_USED = df[(df["type"] == "ComponentUSE")] 
        
        
        def get_dependencies_recursive(df_used,df_def, df_fileNames):
            df_new_entities_old = pd.merge(df_used, df_fileNames, on="filename")
            df_new_entities_new = pd.merge(df_def, df_new_entities_old, how="right", on="name")
            if len(df_new_entities_new[df_new_entities_new.filename_x.isna()].name):
                vprint(1)("unable to find entity:")
                vprint(1)(df_new_entities_new[df_new_entities_new.filename_x.isna()].name)
                
            df_new_entities_new = df_new_entities_new[~df_new_entities_new.filename_x.isna()]
            
            if len(df_new_entities_new) == 0:
                return df_new_entities_old[["name"]]
            
            
            df_new_entities_new["first_diff"] = df_new_entities_new.apply(lambda x: first_diff_between_strings(x["filename_x"],x["filename_y"])  , axis=1) 
            df_new_entities_new = df_new_entities_new.sort_values("first_diff",ascending=False).drop_duplicates("name")
            df_new_entities_new["filename"]= df_new_entities_new["filename_x"]
            return pd.concat([df_new_entities_old, pd.merge(df_used,  df_new_entities_new[["filename"]],  on="filename")]) [["name"]]
            
            
        def get_dependencies_recursive_full(df_used,df_def, df_find_entity_main):
            df_find_entity = df_find_entity_main
            new_length1 = len(df_find_entity)
            old_length1 = 0
            while new_length1 > old_length1:
                df_new_entities_new = get_dependencies_recursive(df_used,df_def,  df_find_entity[["filename"]] )
                df_find_entity = pd.merge(df_def, df_new_entities_new,on="name")
                df_find_entity.drop_duplicates("filename",inplace=True)
                old_length1 = new_length1
                df_find_entity = pd.concat([df_find_entity_main, df_find_entity])
                new_length1 = len(df_find_entity)
            
            df_find_entity.drop_duplicates("filename",inplace=True)     
            df_find_entity.drop_duplicates("name",inplace=True) 
            return df_find_entity
                
        df_find_entity_main = df_entity_def[df_entity_def["name"] == Entity].iloc[:1]
        
        df_find_entity = get_dependencies_recursive_full(df_entities_USED,    df_entity_def, df_find_entity_main)
        df_find_entity = get_dependencies_recursive_full(df_component_USED,   df_entity_def, df_find_entity)
        df_find_entity = get_dependencies_recursive_full(df_packageUSE,       df_packageDef, df_find_entity)
        
        self.filelist = df_find_entity["filename"].tolist()   
        return self.filelist

            
    def get_dependencies_and_make_project_file(self,Entity):
        if not  self.IsInitilized:
            raise Exception("dependency_db_cl not initilized")
        fileList = self.get_dependencies(Entity)
        
        OutputFile =  "build/" +Entity+"/"+Entity+".prj"
        outPath = "build/" +Entity
        
        try_make_dir(outPath)
         
        lines = ""
        for k in fileList:
            lines += 'vhdl work "../../' + k + '"\n'
        save_file(OutputFile, lines)
        self.filelist  = fileList
        return fileList



     

dependency_db = dependency_db_cl(FileName= "build/DependencyBD" )

def get_dependency_db():
    dependency_db.initilize()
    return dependency_db

