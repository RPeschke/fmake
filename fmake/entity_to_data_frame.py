import numpy as np
import pandas as pd
import copy


from fmake.vhdl_load_file_without_comments import load_file_witout_comments
from fmake.generic_helper import get_text_between_outtermost
from  fmake.vhdl_entity_class            import vhdl_entity
from fmake.vhdl_parser import vhdl_parser ,parse_get_top_level_candidates


import dataframe_helpers as dfh

def get_ports(filename):
    entetyCl  =  vhdl_entity(filename)
    df = entetyCl.ports()
    
    df["directionality"] =df["InOut"]    
    df["vname"] =df["port_name"]
    df["vtype"] =df["port_type"]
    df["vdefault"] =df["default"]
    return df[["vname",  "directionality" , "vtype" ,"vdefault"] ]

def get_internal_signals(filename):
    content = load_file_witout_comments(filename)
    sp = parse_get_top_level_candidates(content, " signal ")
    signals = [ x.split(";")[0]  for x in sp  if ":" in x.split(";")[0] ]
    
    s = []
    for x in signals:
        ty_sp  = x.split(":")
        name1 = ty_sp[0].strip()
        ty_sp  = x.split(":")
        default = ty_sp[2][1:].strip() if len(ty_sp)==3 else None
        
        
        
        
        s.append( [name1 , ty_sp[1].strip()  ,default  ] )
    
    
    signals  = pd.DataFrame(s, columns=["vname", "vtype" , "vdefault"])
    signals["directionality"] = "internally"
    return signals



def get_entites(filename):
    ret1 ={
        "symbols" : [],
        "records": [],
        "constants": []
    }
    p = vhdl_parser(filename,ret1 )
    entities = ret1["symbols"]
    entities_used = [x for x in entities if x[1] ==  "entityUSE" or x[1] == "ComponentUSE"]
    content = load_file_witout_comments(filename)
    ret = []
    for entity in entities_used:
        ret.extend( [x for x in content.split(';') if entity[2] in x and " port map " in x])
    ret = [ " " + x.split(" generate ")[-1] for x in ret ]
    ret2 = []
    for entity in ret:
        name = entity.split(":")[0].strip()
        type1 = entity.split(":")[1].split("(")[0]
        type1 = type1.replace("work." ,"" ).replace(" entity ","").replace(" port map ","").strip()
        connections = entity[entity.find("port map (")+10:-2]
        for x in connections.split(","):
            sp = x.split("=>")
            port_name = sp[0].strip() if len(sp) == 2 else None
            signal_name = sp[1].strip() if len(sp) == 2 else sp[0].strip()
            signal_name_simple = signal_name.split("(")[0].split(".")[0].strip()
            ret2.append([name,type1 , port_name, signal_name ,signal_name_simple ] ) 
    df = pd.DataFrame(ret2, columns= ["instance_name", "instance_type" , "port_name" , "signal_name", "signal_name_simple"])
    
    return df 

def get_alias(filename):
    content = load_file_witout_comments(filename)
    candidates  = [ x for x in content.split(";") if "<=" in x]
    ret = []
    for x in candidates:
        s = max([x.find(" loop ") ,x.find(" begin ") ,x.find(" then ") ])
        s = s+6 if s > 0 else 0
        
        source =  x[x.find("<=") +2 : ].strip()
        target = x[s :x.find("<=") ].replace(" begin " ,"").replace(" loop " ,"").replace(" then " ,"") .strip()
        
        ret.append([ target  , source , target.split(".")[0].split("(")[0].strip(), source.split(".")[0].split("(")[0].strip()  ])
        
    df = pd.DataFrame(ret, columns= ["target", "source" , "target_short" , "source_short"])
    return df
    


def make_connection_dataframe(entities, alias, signals):
    sources = signals.merge(alias, left_on="vname" , right_on="source_short", how="left").drop(["source_short"] ,axis=1)
    
    
    
    s1 = copy.copy(sources[["vname", "directionality", "target_short"]])
    s1["alias"] = s1.apply( lambda x: [[ x["vname"] , x["directionality"]]] , axis=1)
    s1["t_short"] = s1["target_short"]
    
    s1 = copy.copy(s1[["t_short", "alias"]])
    while sum(~s1["t_short"].isna()):
        s2 = s1.merge(sources, left_on = "t_short" , right_on="vname",how="left" )
        s2.apply(lambda x: x["alias"].append([x["vname"] , x["directionality"] ] ),axis=1 )
        s2["t_short"] = s2["target_short"]
        s1 = copy.copy(s2[["t_short", "alias"]])
        
    df1 = dfh.expand_dataframe(s1, {"alias_index" : range(len(s1["alias"].iloc[0] ) )})
    
    def get_primary(x):
        
        ret = x["alias"][0]
        for xs in x["alias"]:
            if xs[1] == "in" or xs[1] == "out":
                ret = xs
                
        return ret
        
    df1["primary"] = df1.apply(lambda x: get_primary(x) , axis =1)
    df1["secondary"] = df1.apply(lambda x: x["alias"][x["alias_index"]]  , axis =1)
    
    
    df1["p.vname"] = df1.apply(lambda x: x["primary"][0]  , axis =1)
    df1["p.directionality"] = df1.apply(lambda x: x["primary"][1]  , axis =1)
    
    df1["s.vname"] = df1.apply(lambda x: x["secondary"][0]  , axis =1)
    df1["s.directionality"] = df1.apply(lambda x: x["secondary"][1]  , axis =1)
    
    df1 = df1[["p.vname" ,"p.directionality", "s.vname","s.directionality","alias_index" ]]
    df1 = df1 [~df1["s.vname"].isna()]
    
    def make_unique(gdf):
        x = gdf[gdf["alias_index"] == max(gdf["alias_index"] )].iloc[0]
        return  [ x["p.vname"],x["p.directionality"] ,x["alias_index"]]
    
        
    df1 = dfh.group_apply(df1,["s.vname", "s.directionality"] ,["p.vname","p.directionality","alias_index"] , make_unique)
    
    entities1 =  entities.merge(df1, left_on="signal_name_simple" , right_on="s.vname", how="left")
    def make_top_name(x):
        
        if x["p.directionality"] == "in" and x["instance_name"] == "top":
            return x["instance_name"]+"_in"
        if x["p.directionality"] == "out" and x["instance_name"] == "top":
            return x["instance_name"]+"_out"
        
        return x["instance_name"]
    
    entities1["instance_name"]  = entities1.apply( make_top_name , axis = 1 )
    entities1 = entities1.drop_duplicates(["instance_name","p.vname","p.directionality"])[["instance_name","p.vname","p.directionality"]] 
    
    

    return entities1 
    

def make_diagram_data(connections):
    entities = connections.drop_duplicates(["instance_name"])[["instance_name"]]
    entities["column"] = np.arange(1, len(entities) + 1)
    entities["column"] = entities.apply(lambda x: 0 if x["instance_name"] =="top_in" else max(entities["column"]) + 1 if   x["instance_name"] =="top_out" else x["column"]  , axis =1 )
    entities = entities.sort_values("column")
    entities["column"] = range(len(entities))
    
    signals = connections.drop_duplicates(["p.vname","p.directionality"])[["p.vname","p.directionality"]]
    signals["row"] = range(len(signals))
    entities_signals = connections.drop_duplicates(['p.vname', "instance_name"])[["p.vname", "instance_name"]]
    
    
    
    
    s = signals.merge(entities_signals , on="p.vname")
    ss = s.merge(entities, on ="instance_name")
    sss = dfh.group_apply(ss, ["p.vname","p.directionality", "row"] , ["columns_min" , "columns_max"] , lambda x: [ min(x["column"]) , max(x["column"])])
    ess = dfh.group_apply(ss, ["instance_name","column"] , ["row_min" , "row_max"] , lambda x: [ min(x["row"]) , max(x["row"])])
    ssss = dfh.expand_dataframe( sss , {"column" : range(max(sss["columns_max"]) )} )
    ssss = ssss[(ssss["columns_min"] <=ssss["column"] )&(ssss["columns_max"] >=ssss["column"])]
    
    esss = dfh.expand_dataframe( ess , {"row" : range(max(ess["row_max"]) )} )
    esss = esss[(esss["row_min"] <=esss["row"] )&(esss["row_max"] >=esss["row"])]
    esss.merge(ssss , on=["column", "row"]).drop_duplicates(["instance_name", "p.vname"])
    return entities
    
    
def entity_to_data_frame(filename, dependecies):
    entities = get_entites(filename)
    alias = get_alias(filename)
    
    
    ports  = get_ports(filename)
    signals = get_internal_signals(filename)
    
    signals = pd.concat([ports, signals ])
    
    ports["instance_name"]  = "top"
    ports["instance_type"]  = "top"
    ports["port_name"]  = ports["vname"]
    ports["signal_name"]  = ports["vname"]
    ports["signal_name_simple"]  = ports["vname"]
    top_entity = ports[["instance_name", "instance_type" , "port_name" , "signal_name", "signal_name_simple"]]
    entities = pd.concat([entities , top_entity])
    connections = make_connection_dataframe(entities , alias , signals)
    make_diagram_data(connections)
    return connections
    
    
    

