import os
import glob
from datetime import datetime
import re

import importlib.util
import sys
import base64
import inspect
import os


import hashlib
import fmake

import importlib.util
import os
import sys
from pathlib import Path


def find_fmake_program_functions(file_path):
    pattern = re.compile(r"@fmake\.program\s*\n\s*def\s+(\w+)\s*\(")
    with open(file_path, "r") as f:
        contents = f.read()
    return pattern.findall(contents)


def list_python_file_timestamps(base_dir):
    # Get all .py files in base_dir and one level down
    ret = []
    pattern_top = os.path.join(base_dir, "*.py")
    pattern_sub = os.path.join(base_dir, "*", "*.py")
    
    files = glob.glob(pattern_top) + glob.glob(pattern_sub)

    for file in files:
        mtime = os.path.getmtime(file)
        ret.append( [file, mtime] )
        #print(f"{file}: {mtime}")
    return ret

def check_unique_program_names(data):
    seen = set()
    duplicates = set()

    for entry in data:
        if len(entry) >= 3:
            name = entry[2]
            if name in seen:
                duplicates.add(name)
            else:
                seen.add(name)

    if duplicates:
        print("Duplicates found:", duplicates)
        return False
    else:
        return True
    
def find_program_rows(data, program_name):
    return [row for row in data if len(row) >= 3 and row[2] == program_name]

def import_from_filepath_full(filepath):
    # Extract module name from filepath
    
    
    module_name = filepath.replace("\\","/").split('/')[-1].split('.')[0]
    
    # Create a module spec from the filepath
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    
    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)
    
    # Add the module to sys.modules
    sys.modules[module_name] = module
    
    # Execute the module (run its code)
    spec.loader.exec_module(module)
    
    return module


def load_and_run_module(path_to_module):
    module_path = Path(path_to_module).resolve()
    module_dir = module_path.parent
    module_name = module_path.stem

    # Create the spec
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    module = importlib.util.module_from_spec(spec)

    # Add module directory to sys.path for relative imports
    sys.path.insert(0, str(module_dir))

    # Save current directory
    old_cwd = os.getcwd()
    try:
        # Change to module directory
        os.chdir(module_dir)

        # Execute the module
        spec.loader.exec_module(module)

    finally:
        # Restore the original working directory and sys.path
        os.chdir(old_cwd)
        sys.path.pop(0)

    return module

 
def parse_args_to_kwargs(arglist):
    args = []
    kwargs = {}
    i = 0
    while i < len(arglist):
        if arglist[i].startswith("--"):
            key = arglist[i][2:]  # remove leading '--'
            value = arglist[i + 1]
            kwargs[key] = value
            i += 2
        else:
            args.append(arglist[i])
            i += 1
    return args, kwargs

def get_fmake_user_programs():
    files = list_python_file_timestamps(fmake.get_project_directory())
    ret = []

    for f in files:
        programs  = find_fmake_program_functions(f[0])
        for p in programs:
            ret.append(
                [f[0], f[1] , p ]
            )
    return ret

def get_program(Name, file = None):
    if file is None:
        user_programs = get_fmake_user_programs()
        if not check_unique_program_names(user_programs ):
            raise Exception("Programs are not unique")
            
        FileList =  find_program_rows(user_programs, Name)

        if len(FileList) == 0:
            raise Exception("Program Not Found")

        file = FileList[0][0]
    
    
    module = load_and_run_module(file  )

    if not hasattr(module, Name):
        raise Exception("Program Not Found")
    

    return getattr(module, Name)


def run_fmake_user_program(programName):


    user_programs = get_fmake_user_programs()
    if not check_unique_program_names(user_programs ):
        return None, user_programs
        
    FileList =  find_program_rows(user_programs, programName)

    if len(FileList) == 0:
        return False, user_programs

    filepath = FileList[0][0]
    functionName = FileList[0][2]
    module = load_and_run_module(filepath  )


    if not hasattr(module, functionName):
        return None, user_programs
    

    config.Execution_Path = os.getcwd()
    fun = getattr(module, functionName) # (*args, **kwargs)  # Call the function
    return fun, user_programs



def program(func):
    return func


class programs_config_t:
    def __init__(self):
        self.Execution_Path=os.getcwd()
        self.argv = sys.argv[2:]
        self.generic = {}

config = programs_config_t()
