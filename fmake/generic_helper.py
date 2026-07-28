import os
import pandas as pd
import copy
import argparse

class constants:
    text_IO_polling = "text_io_query"
    text_io_polling_send_lock_txt    = "send_lock.txt"
    text_io_polling_send_txt         = "send.txt"
    text_io_polling_receive_txt      = "receive.txt"
    text_io_polling_receive_lock_txt = "receive_lock.txt"

    env_FMAKEBUILD = "FMAKEBUILD"
    env_PROJECTDIRECTORY = "FMAKEPROJECT"

    default_build_folder = "build/"
    alternative_build_folder = "fbuild/"
    fmake_filename = "fmake.txt"
    proto_Project_url  =  "https://raw.githubusercontent.com/RPeschke/fmake/main/proto_build/proto_Project.in"
    xise_prototype_url =  "https://raw.githubusercontent.com/RPeschke/fmake/main/proto_build/simpleTemplate.xise.in"
    empty_testbench_xlsm_URL = "https://github.com/RPeschke/fmake/raw/main/proto_build/empty_testbench.xlsm"



g_vars = {"project_directory": None, 
          "build_directory": None}

class verbose_printer_cl:
    def __init__(self) -> None:
        self.level = 0
        self.printer = print
        
    def __call__(self, debug_level):
        def local_printer( *args , **kwds):
            if self.level >= debug_level:
                self.printer(*args , **kwds)        
        
        return local_printer
            
    def add_cl_args(self, parser):
        parser.add_argument('--verbosity',   help='drops columns from data frame',default='0')
        
    def use_cl_arg(self, args):
        self.level = int(args.verbosity)

vprint = verbose_printer_cl()

def extract_cl_arguments(parser, x):
    vprint.add_cl_args(parser) 
    args = parser.parse_args(x[2:])
    vprint.use_cl_arg(args)
    if hasattr(args , "entity"):
        args.entity  = args.entity.lower()
    return args

def cl_add_entity(parser):
    parser.add_argument('--entity',      help='entity name',default="",required=True)
    
def cl_add_OutputCSV(parser):
    parser.add_argument('--OutputCSV',      help='output csv file',default="")

def cl_add_gui(parser):
    parser.add_argument('--gui', dest='run_with_gui', action='store_const',
                    const=True, default=False,
                    help='')
    
def cl_add_run_infinitly(parser):
    parser.add_argument('--inf', dest='run_infinitly', action='store_const',
                    const=True, default=False,
                    help='')
    
def first_diff_between_strings(x,y):
    for i in range(min(len(x),len(y))):
        if x[i] != y[i]:
            return i
                
    return min(len(x),len(y))
        

def try_remove_file(fileName, onError = None ):
    try:
        os.remove(fileName )
    except :
        if onError is not None:
            onError()

def try_make_dir(name,isRelativePath=True):
    try:
        if isRelativePath:
            abs_name = os.getcwd()+"/" +name
        else:
            abs_name = name

        os.makedirs(abs_name, exist_ok=True)
    except OSError:  
        vprint(1) ("Creation of the directory %s failed" % name)





def get_text_between_outtermost(raw_text,startToken,EndToken):
    ret = ""
    
    sp = raw_text.find(startToken)
    if sp == -1:
        return ""
    TokenLevel = 1
    cut_start = sp+len(startToken)
    current_index = cut_start
    
    while TokenLevel > 0:
        startIndex = raw_text.find(startToken,current_index)
        endIndex = raw_text.find(EndToken,current_index)

        if endIndex == -1:
            raise Exception("end Token not find",raw_text)
        elif startIndex > -1 and startIndex < endIndex:
            TokenLevel+=1
            current_index = startIndex +len(startToken)

            continue
        
        elif startIndex == -1 or endIndex < startIndex:
            TokenLevel -= 1
            current_index = endIndex +len(EndToken)
            if TokenLevel == 0:
                return raw_text[cut_start:endIndex]        



    
def load_file(filename, read_function = lambda x : x.read() ):
    with open(filename) as f:
        return read_function(f)    

def try_load_file(filename, read_function = lambda x : x.read()):
    try:
        return load_file(filename, read_function )
    except:
        return None

def save_file(fileName,Data,newline="\n"):
    Data = Data.replace("\n",newline)
    with open(fileName,"w", newline = "") as f:
        return f.write(Data)                 
    
    
def expand_dataframe(df, axis):
    dummy_name = "sdadasdasdasdaweqweqewqe"
    df[dummy_name] =1
    for key in axis:
        df1 = pd.DataFrame({key: axis[key]})
        df1[dummy_name] =1
        df = df.merge(df1, on = dummy_name)
    df = df.drop(dummy_name , axis=1)
    return df       



def get_converter():
    f_values ={}
    def connect_prefex_and_name(prefix, name):
        return prefix + "." +name if prefix != "" else name
    
    def process_dict_values(ret, dic, prefix =""):
        for k in dic.keys():
            process_values(ret, dic[k],connect_prefex_and_name(prefix , k) )
            
    def process_list_values(ret, x, prefix =""):
        ret_1 =  copy.deepcopy(ret)
        pr = connect_prefex_and_name(prefix , "list")
        pr_type = connect_prefex_and_name(prefix , "type")
        for i,elem in enumerate(x):
            if i == 0:
                ret[-1][pr_type ] = type(elem).__name__
                
                process_values(ret, elem, pr )
            else:
                ret_copy = copy.deepcopy(ret_1)
                ret_copy = ret_copy[-2:]
                ret_copy[-1][pr_type] = type(elem).__name__
                process_values(ret_copy, elem, pr )
                ret.extend(ret_copy)
                
    def process_int_values(ret, x, prefix =""):
        ret[-1][prefix] = x 

    def process_str_values(ret, x, prefix =""):
        ret[-1][prefix] = x             
            
    f_values["dict"]  = process_dict_values
    f_values["int"]  = process_int_values
    f_values["str"]  = process_str_values
    f_values["list"]  = process_list_values
    return f_values


f_values = get_converter()
def process_values(ret, x, prefix =""):
    
    try:
        return f_values[type(x).__name__ ] (ret, x,prefix)
    except:
        return process_values(ret, x.__dict__,prefix)
    
    
    

def flatten_list(In_list):
    ret = []
    for x in  In_list:
        if type(x).__name__ == "list":
            buff = flatten_list(x)
            ret += buff
        else:
            ret.append(x)

    return ret



def join_str(content, start="",end="",LineEnding="",Delimeter="",LineBeginning="", IgnoreIfEmpty=False, RemoveEmptyElements = False):
    ret = ""
    if len(content) == 0 and IgnoreIfEmpty:
        return ret
    

    
    if len(content) == 0:
        ret += start
        ret += end
        return ret

    ret += start
    if RemoveEmptyElements:
        content = [x for x in content if x]

    index = 0
    for x in content:
        if index < len(content) - 1:
            ret += LineBeginning + str(x) + Delimeter + LineEnding
        else:
            ret += LineBeginning + str(x) +  LineEnding
        index += 1
        
        

    
    ret += end
    return ret


def get_build_directory():
    env_build_folder = os.environ.get(constants.env_FMAKEBUILD)
    if env_build_folder:
        if os.path.isdir(env_build_folder):
            return str(env_build_folder).replace("\\", "/")
        raise Exception(f"{constants.env_FMAKEBUILD} path does not exist", env_build_folder)

    prefix = ""
    fmake_file = constants.default_build_folder+"/"+constants.fmake_filename
    for i in range(100):
        if os.path.isfile(prefix+fmake_file):
            return str(os.path.abspath(prefix+ constants.default_build_folder + "/")).replace("\\", "/")
        prefix+="../"
    
    fmake_file = constants.alternative_build_folder+"/"+constants.fmake_filename
    for i in range(100):
        if os.path.isfile(prefix+fmake_file):
            return str(os.path.abspath(prefix+ constants.alternative_build_folder + "/")).replace("\\", "/")
        prefix+="../"

    raise Exception("unable to find build directory")




import os

def find_git_root(start_path=None):
    """
    Searches upward from the given path (or current working directory)
    for a .git *folder*. Returns the path to the folder containing .git,
    or None if not found.
    """
    if start_path is None:
        start_path = os.getcwd()

    current = os.path.abspath(start_path)

    while True:
        git_path = os.path.join(current, ".git")

        # Must be a directory, not a file
        if os.path.isdir(git_path):
            return current

        # Stop at filesystem root
        parent = os.path.dirname(current)
        if parent == current:
            return None

        current = parent


def set_project_directory(path):
    if not os.path.isdir(path):
        raise Exception("project directory is not a valid directory", path)
    g_vars["project_directory"] = path

def get_project_directory():
    env_project_folder = os.environ.get(constants.env_PROJECTDIRECTORY)
    if env_project_folder:
        if os.path.isdir(env_project_folder):
            return str(env_project_folder).replace("\\", "/")
        raise Exception(f"{constants.env_PROJECTDIRECTORY} path does not exist", env_project_folder)

    if g_vars["project_directory"] is not None:
        #check if this is a valid directory
        if os.path.isdir(g_vars["project_directory"]):
            return str(g_vars["project_directory"]).replace("\\", "/")
        else:
            raise Exception("project directory is not a valid directory", g_vars["project_directory"])
    try:
        build = get_build_directory()
        return str(os.path.abspath(build + "/../" )).replace("\\", "/")
    except:
        pass

    git_root = find_git_root()    
    if git_root:
        return str(git_root).replace("\\", "/")

    return str(os.path.abspath(".")).replace("\\", "/")
    
