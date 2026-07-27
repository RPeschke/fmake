import atexit
import os
import glob
from datetime import datetime
import re
import threading

import importlib.util
import sys
import base64
import inspect
import os


import hashlib
from tokenize import Name
import fmake

import importlib.util
import os
import sys
from pathlib import Path
from functools import lru_cache
import dataframe_helpers as dfh


import re

def find_fmake_program_functions(file_path):
    """
    Finds functions decorated with @fmake.program or #@fmake.program,
    supporting both sync and async functions.
    Returns a list of function names.
    """
    pattern = re.compile(
        r"#?@fmake\.program(?:\(\s*version\s*=\s*([^)]*)\))?"
        r"\s*\n\s*(?:async\s+)?def\s+(\w+)\s*\(",
        re.MULTILINE,
    )
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
    except UnicodeDecodeError:
        return []

    return pattern.findall(contents)



def find_fmake_target_functions(file_path):
    pattern = re.compile(r"@fmake\.target(?:\([^)]*\))?\s*\n\s*def\s+(\w+)\s*\(")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            contents = f.read()
    except UnicodeDecodeError:
        return []
    return pattern.findall(contents)









def _is_subpath(path_obj, base_dir_obj):
    try:
        path_obj.relative_to(base_dir_obj)
        return True
    except ValueError:
        return False


def _get_callsite_script_path():
    this_file = Path(__file__).resolve()
    for frame in inspect.stack()[2:]:
        frame_path = Path(frame.filename).resolve()
        if frame_path != this_file:
            return frame_path
    return None


def _filter_rows_for_callsite_subfolder(file_list):
    if len(file_list) <= 1:
        return file_list

    callsite = _get_callsite_script_path()
    if callsite is None:
        return file_list

    project_parent = Path(fmake.get_project_directory()).resolve()
    search_dir = callsite.parent.resolve()
    while True:
        filtered = []
        for row in file_list:
            row_path = Path(row[0]).resolve()
            if _is_subpath(row_path, search_dir):
                filtered.append(row)

        if len(filtered) > 0:
            return filtered

        if search_dir == project_parent:
            # Reached the configured search ceiling.
            return file_list

        parent = search_dir.parent
        if parent == search_dir:
            # Reached filesystem root without finding scoped matches.
            #make an assert here. this should never happen since it should always be stopped by the project parent 
            assert False, "Reached filesystem root without finding scoped matches."
            
        if not _is_subpath(parent, project_parent):
            # Do not walk above the parent of project directory.
            return file_list
        search_dir = parent




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
            value = arglist[i + 1] if i + 1 < len(arglist) else ""
            kwargs[key] = value
            i += 2
        else:
            args.append(arglist[i])
            i += 1
    return args, kwargs


def print_user_program_table(user_programs, printer=print):
    rows = [row for row in user_programs if len(row) >= 3]
    rows.sort(key=lambda row: (row[2].lower(), row[0].lower()))

    program_width = max(len("Program"), *(len(row[2]) for row in rows)) if rows else len("Program")

    printer(f"{'Program'.ljust(program_width)}  File")
    printer(f"{'-' * program_width}  {'-' * 4}")

    for file_path, _, program_name in rows:
        printer(f"{program_name.ljust(program_width)}  {file_path}")




class user_program_finder_t:
    def __init__(self):
        current_file = os.path.abspath(__file__)
        self.user_programs_buffer_file = current_file + ".buffer.pkl"
        if not os.path.exists(self.user_programs_buffer_file):
            dfh.pkl_save({}, self.user_programs_buffer_file)

        self._buffer_lock = threading.Lock()
        self.user_programs_buffer  = dfh.pkl_load(self.user_programs_buffer_file)
        self.programs_buffered = self.user_programs_buffer.get(fmake.get_project_directory() , [])
        self.running = True
        self.external_roots = [] 

        
        self.program_threads = [threading.Thread(target=self.get_fmake_user_programs, daemon=True)]
        self.program_threads[0].start()
        atexit.register(self._on_exit)

    def _on_exit(self):
        self.running = False
        for t in self.program_threads:
            t.join()

    def add_external(self , root):
        self.external_roots.append(root)
        self.program_threads = [threading.Thread(target= lambda : self.get_fmake_user_programs(root=root), daemon=True)]
        self.program_threads[-1].start()


    def get_programs(self, root=None):
        root = root if root is not None else fmake.get_project_directory()
        with self._buffer_lock:
            return self.user_programs_buffer.get(root, [])
    
        
    def find_program_and_file_rows_internal(self, program_name, file_name = None):
        fltr = lambda row: (
            row["program_name"] == program_name
            and (file_name is None or Path(row["filename"]).name  == file_name)
        )
        
        b =  [
            row for row in self.get_programs() 
              if fltr(row) 
            ]
        if len(b) > 0:
            return b

        for root in self.external_roots:
            b =  [
                row for row in self.get_programs(root) 
                if fltr(row) 
            ]
            if len(b) > 0:
                return b
        return []

    
    def find_program_rows(self, program_name,  file_name = None):
        b = self.find_program_and_file_rows_internal(program_name, file_name)
        if len(b) > 0:
            return b    

        self.wait_for_programs()

        return  self.find_program_and_file_rows_internal(program_name, file_name)
        



    def wait_for_programs(self):
        """Wait for the background thread to complete loading programs"""
        for t in self.program_threads:
            t.join()


    def get_fmake_user_programs(self, root = None ):
        programs = []
        root = root if root is not None else fmake.get_project_directory()
        files = self.list_python_file_timestamps(root)
        for f in files:
            if not self.running:
                return 
            programs_regex  = find_fmake_program_functions(f[0])
            for p in programs_regex:
                programs.append(
                    {
                        "filename" : f[0], 
                        "version" : float(p[0]) if p[0] else 0 , 
                        "program_name" : p[1] 
                    }
                )
        if not self.running:
            return  
        with self._buffer_lock:
            self.user_programs_buffer  = dfh.pkl_load(self.user_programs_buffer_file)
            if self.user_programs_buffer.get(root) == programs:
                return 
            self.user_programs_buffer[root] = programs
            dfh.pkl_save(self.user_programs_buffer, self.user_programs_buffer_file)


    
    def list_python_file_timestamps(self, base_dir):
        ret = []

        for root, dirs, files in os.walk(base_dir):
            if not self.running:
                return []
            # Skip directories starting with a dot
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    mtime = 0  #os.path.getmtime(full_path)
                    ret.append([full_path, mtime])

        return ret

user_program_finder_t_instance = user_program_finder_t()

def user_programs_refresh():
    for t in user_program_finder_t_instance.program_threads:
        if t.is_alive():
            
            user_program_finder_t_instance.wait_for_programs()
            return
    
    user_program_finder_t_instance.running = True
    user_program_finder_t_instance.get_fmake_user_programs()
    for root in user_program_finder_t_instance.external_roots:
        user_program_finder_t_instance.get_fmake_user_programs(root)
    user_program_finder_t_instance.running = False


def get_fmake_user_programs1():
    user_program_finder_t_instance.wait_for_programs()
    return user_program_finder_t_instance.get_programs()


def add_external_root(root):
    user_program_finder_t_instance.add_external(root)

def get_program(Name, fullpath = None,file = None, unique = False, version = None, version_exact = False):

    def filter_version(programs, version=None, version_exact=False):
        if version is not None:
            if version_exact:
                programs = [row for row in programs if row["version"] == version]
            else:
                programs = [row for row in programs if row["version"] >= version]

        return programs

    def filter_unique(programs, unique=False):
        if unique and len(programs) > 1:
            raise Exception(
                f"Program '{programs[0][2]}' is not unique for this call site: "
                f"{[row[0] for row in programs]}"
            )
        return programs

    def filter_caller_subfolder(programs):
        if len(programs) <= 1:
            return programs

        filtered = _filter_rows_for_callsite_subfolder(programs)
        return filtered

    def assert_one_candidate_found(FileList, Name , fullpath , file , unique ):
        
        if len(FileList) == 0:
            raise Exception(f"Program Not Found: {Name}, {fullpath}, {file}, {unique}"  )

        if len(FileList) > 1:
            raise Exception(
                    f"Program '{Name}' is ambiguous for this call site: "
                    f"{[row[0] for row in FileList]}"
                )

    def assert_function_found(module, Name):
        if not hasattr(module, Name):
            raise Exception("Program Not Found")
    
    if fullpath is None:
        FileList =  user_program_finder_t_instance.find_program_rows(Name, file)

        FileList = filter_version(FileList, version=version, version_exact=version_exact)

        FileList = filter_unique(FileList, unique=unique)

        FileList = filter_caller_subfolder(FileList)

        
        assert_one_candidate_found(FileList, Name , fullpath , file , unique  )
      
        fullpath = FileList[0]["filename"]
    
    
    module = load_and_run_module(fullpath  )

    assert_function_found(module, Name )

    return getattr(module, Name)


def run_fmake_user_program(programName):


    
    
        
    FileList =  user_program_finder_t_instance.find_program_rows(programName)

    if len(FileList) == 0:
        user_program_finder_t_instance.wait_for_programs()
        user_programs =  user_program_finder_t_instance.get_programs()
        return None, user_programs

    filepath = FileList[0][0]
    functionName = FileList[0][2]
    module = load_and_run_module(filepath  )


    if not hasattr(module, functionName):
        user_program_finder_t_instance.wait_for_programs()
        user_programs =  user_program_finder_t_instance.get_programs()
        return None, user_programs
    

    config.Execution_Path = os.getcwd()
    fun = getattr(module, functionName) # (*args, **kwargs)  # Call the function
    return fun, None



from functools import wraps

def program(_func=None, *, version=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"running {func.__name__}, version={version}")
            return func(*args, **kwargs)

        wrapper.version = version
        return wrapper

    if _func is None:
        return decorator

    return decorator(_func)



def target(func):
    return func


class programs_config_t:
    def __init__(self):
        self.Execution_Path=os.getcwd()
        self.argv = sys.argv[2:]
        self.generic = {}

config = programs_config_t()
