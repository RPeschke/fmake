
from  .vhdl_get_entity_def import  get_list
from  .generic_helper import get_text_between_outtermost
from fmake.generic_helper import  vprint 

def vhdl_get_type_def_array(rawText):
    words = rawText.strip().split(" ")
    words = list(filter(None, words)) 
    ret = {}
    ret["name"] = words[0]
    sp = rawText.split(";")
    if len(sp) ==0:
        raise Exception("end Token not found")
    
    rawText = sp[0]
    sp = rawText.split(" of ")
    ret["BaseType"] = sp[1].strip()
    
    array_length= get_text_between_outtermost(sp[0],'(',')')
    ret["array_length"] =array_length
    ret["vhdl_type"] = "array"


    return ret



def vhdl_get_type_def_record(rawText):
    words = rawText.strip().split(" ")
    words = list(filter(None, words)) 
    ret = {}
    ret["name"] = words[0]
    sp = rawText.split(" end ")
    if len(sp) ==0:
        raise Exception("end Token not found")
    
    rawText = sp[0]
    try:
        rawText = rawText.split(" record ")[1]
    except:
        vprint(2)(rawText)
        raise

    lst = get_list("record ("+ rawText +")", "record")

    ret["record"] = lst
    

    ret["vhdl_type"] = "record"


    return ret

def vhdl_get_type_alias(rawText):
    words = rawText.strip().split(" ")
    words = list(filter(None, words)) 
    ret = {}
    ret["name"] = words[0]
    sp = rawText.split(";")
    if len(sp) ==0:
        raise Exception("end Token not found")
    
    rawText = sp[0]
    rawText = rawText.split(" is ")[1]
    ret["BaseType"] = rawText


    ret["vhdl_type"] = "subtype"


    return ret

def vhdl_get_type_def_enum(rawText):
    ret = {}
    ret["name"]=rawText.split("is")[0].strip()
    ret["vhdl_type"] = "enum"
    ret["record"] = [ {"name": x.strip(), "type" :"enum_element" , "InOut" :"" ,"default":""} for x in   rawText.split("(")[1].split(")")[0].split(",")]
    return ret

def vhdl_get_type_def_from_string(FileContent):
    fc =FileContent
    candidates =  fc.split(" type ")
    type_list = list()
    for x in candidates:
        ret = {}
        words = x.strip().split(" ")
        words = list(filter(None, words)) 
        if len(words)  > 1  and  "is" in words[1]:
            ret["name"] = words[0]
            ret["vhdl_type"] = "not_used"
            if words[2]== 'array':
                ret = vhdl_get_type_def_array(x)
            elif words[2]== 'record':
                ret = vhdl_get_type_def_record(x)
            elif words[2]== '(':
                ret = vhdl_get_type_def_enum(x)


        if len(ret) > 0:
            type_list.append(ret)


    candidates =  fc.split(" subtype")
    for x in candidates[1:]:
        ret = {}
        words = x.strip().split(" ")
        words = list(filter(None, words)) 
        if len(words)  > 1  and  "is" in words[1]:
            ret["name"] = words[0]
            ret["vhdl_type"] = "not_used"
            if words[2]== 'array':
                ret = vhdl_get_type_def_array(x)
            elif words[2]== 'record':
                ret = vhdl_get_type_def_record(x)
            elif words[2]== '(':
                ret = vhdl_get_type_def_enum(x)
            else:
                ret = vhdl_get_type_alias(x)


        if len(ret) > 0:
            type_list.append(ret)

    return type_list












