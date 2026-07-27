
import fmake 
from fmake.generic_helper import get_project_directory,save_file

import inspect
from pathlib import Path


def get_caller_folder(levels_up=1):
    """Return the caller folder by walking up the call stack."""
    frame = inspect.currentframe()
    try:
        for _ in range(levels_up):
            if frame is None or frame.f_back is None:
                raise ValueError(f"Call stack is not deep enough for levels_up={levels_up}")
            frame = frame.f_back

        caller_file = inspect.getframeinfo(frame).filename
        return str(Path(caller_file).parent.resolve()).replace("\\", "/")
    finally:
        # Avoid reference cycles with frame objects.
        del frame

def assert_file_exists(path):
    """Raise FileNotFoundError when the provided file path does not exist."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"\n====================================\nFile not found:\n{p}\n====================================\n")
    return str(p.resolve()).replace("\\", "/")

def to_absolute(paths, base = None, caller_levels_up=1):
    caller_folder = get_caller_folder(caller_levels_up)
    if base is None:
        base = caller_folder
    return [assert_file_exists(f"{base}/{path}") for path in paths]


def get_current_path():
    return get_caller_folder(levels_up=2)

directory = get_project_directory()
class pyVivadoProject:
    def __init__(self, project_name):
        self.project_name = project_name
        self.project_path = None
        self.project = None
        self.top = None
        self.sources = []
        self.sources_sim = []
        self.constraints = []
        self.board = None
        self.part = None
        self.dependencies = []
        self.block_designs = []
        self.custom_code = []

        self.vivado_path = None
        self.vivado_params = []
    
    def add_vivado_params(self, name, params):
        self.vivado_params += [(name, params)]
    
    def set_vivado_path(self, path):
        self.vivado_path = assert_file_exists(path)
    
    def get_project_path(self):
        return self.project_path if self.project_path else f"{directory}/build/{self.project_name}"
    

    def add_sources(self, sources , base = None):
        self.sources += to_absolute(sources, base=base, caller_levels_up=3)


    def add_sources_sim(self, sources , base = None):
        self.sources_sim += to_absolute(sources, base=base, caller_levels_up=3)

    def add_constraints(self, constraints , base = None):
        self.constraints += to_absolute(constraints, base=base, caller_levels_up=3)
        
    def add_dependency(self, dependency, *args, **kwargs):
        fmake.get_program(dependency)(self, *args, **kwargs)
        self.dependencies.append(dependency)
    
    def assert_depenency_exists(self, dependency):
        if dependency not in self.dependencies:
            raise Exception(f"================================\nDependency '{dependency}' not found in project '{self.project_name}'. Please add it using 'add_dependency' method.\n================================")
        
    
    def add_block_design(self, script_path, block_name):
        # Implement logic to add a block design to the project
        caller = get_caller_folder(levels_up=2)
        script_path = assert_file_exists(f"{caller}/{script_path}")
        self.block_designs.append((script_path, block_name))

    def make_vivado(self):
        import os
        os.makedirs(self.get_project_path(), exist_ok=True)
        print(f"Creating Vivado project at: {self.get_project_path()}")
        
        ret = "" 
        ret += f'set project_name "{self.project_name}"\n'
        ret += f'set project_path "{self.get_project_path()}"\n'
        ret +=  "\n\n\n#=========== Vivado Vivado params ===========\n\n\n"
        for param in self.vivado_params:
            ret += f'set_param  {param[0]} "{param[1]}"\n'
        ret +=  "\n\n\n#=========== Vivado Project Configuration ===========\n\n\n"
        if self.part is not None:
            ret +=  f'create_project {self.project_name} {self.get_project_path()} -force -part {self.part}\n'
        else:
            ret +=  f'create_project {self.project_name} {self.get_project_path()} -force\n'

        if self.board is not None:
            ret += f'set_property BOARD_PART {self.board} [current_project]\n'
        
        
        ret += f'set_property TARGET_LANGUAGE VHDL [current_project]\n'
        ret += f'set_property SIMULATOR_LANGUAGE Mixed [current_project]\n'
        ret +=  "\n\n\n#=========== Vivado Project Sources ===========\n\n\n"
        files_added = set()
        for source in self.sources:
            if source not in files_added:
                ret += f'add_files -fileset sources_1  "{source}"\n'
                files_added.add(source)
        
        ret +=  "\n\n\n#=========== Vivado Project Sources simulation ===========\n\n\n"
        for source in self.sources_sim:
            if source not in files_added:
                ret += f'add_files -fileset sim_1 "{source}"\n'
                files_added.add(source)
            
        ret +=  "\n\n\n#=========== Vivado Project constraints ===========\n\n\n"
        for constraint in self.constraints:
            if constraint not in files_added:
                ret += f'add_files -fileset constrs_1 "{constraint}"\n'
                files_added.add(constraint)


        ret +=  "\n\n\n#=========== Vivado Project block design ===========\n\n\n"
        for script_path, block_name in self.block_designs:
            ret += f'source "{script_path}"\n'
            ret += f'make_wrapper -files [get_files {block_name}.bd] -top\n'

            ret += f'add_files -norecurse \\\n'
            ret += f'    [file normalize "{self.get_project_path()}/{self.project_name}.gen/sources_1/bd/{block_name}/hdl/{block_name}_wrapper.vhd"]\n'



        ret +=  "\n\n\n#=========== Vivado Project Top Level ===========\n\n\n"
        ret += f'set_property top {self.top} [current_fileset]\n'


        ret +=  "\n\n\n#=========== Vivado Project Custom Code ===========\n\n\n"
        for code in self.custom_code:
            ret += code + "\n"

        path = f"{self.get_project_path()}/vivado_project.tcl"
        save_file(path, ret)
        directory = get_project_directory()
        if self.vivado_path is None:
            cmd = f"cd {directory} && vivado -mode batch -source {path} -notrace  -log {self.get_project_path()}/vivado.log   -journal {self.get_project_path()}/vivado.jou"    
        else:
            cmd = f"{self.vivado_path} && cd {directory} && vivado -mode batch -source {path} -notrace  -log {self.get_project_path()}/vivado.log   -journal {self.get_project_path()}/vivado.jou"
        print(cmd)
        os.system(cmd)

        return path
        




