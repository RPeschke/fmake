import os
import re

import argparse

from fmake.programm_list import add_program

from fmake.generic_helper import  vprint,  save_file , load_file ,try_make_dir


from fmake.generic_helper import extract_cl_arguments, cl_add_entity , cl_add_gui, constants



from cocotb_test.simulator import run
from pathlib import Path

import fmake


def load_vhdl_sources_from_prj(project_file):
    project_file_path = Path(project_file).resolve()
    project_dir = project_file_path.parent
    vhdl_sources = []

    with open(project_file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            match = re.match(r'^vhdl\s+\S+\s+"([^"]+)"\s*$', stripped, re.IGNORECASE)
            if match is None:
                continue

            rel_path = match.group(1)
            abs_path = (project_dir / rel_path).resolve()
            vhdl_sources.append(str(abs_path))

    return vhdl_sources


def run_cocotb(args):
    
    test_file = Path(args.cocotb_file).resolve()
    if not test_file.is_file():
        print(f"Error: cocotb file does not exist: {test_file}")
        raise SystemExit(1)

    build_path = fmake.get_project_directory() + "/build/"   + args.entity  

    if not os.path.isdir(build_path):
        print(f"Error: build path does not exist: {build_path}")
        raise SystemExit(1)

    project_file = os.path.join(build_path, f"{args.entity}.prj")
    if not os.path.isfile(project_file):
        print(f"Error: project file does not exist: {project_file}")
        raise SystemExit(1)

    vhdl_sources = load_vhdl_sources_from_prj(project_file)
    if len(vhdl_sources) == 0:
        print(f"Error: no VHDL sources found in project file: {project_file}")
        raise SystemExit(1)

    build_sim_path = build_path +"/cocotb_sim"
    try_make_dir(build_sim_path)
    

    run(
        vhdl_sources=vhdl_sources,
        toplevel=args.entity.lower(),
        module=test_file.stem,
        python_search=[str(test_file.parent)],
        sim_build=build_sim_path,
        simulator=os.getenv("SIM", "ghdl"),
        compile_args=["--std=19"],
        sim_args=[f"--wave={args.entity}.ghw"],
    )
    print("Test completed")



def ghdl_run_wrap(x):
    parser = argparse.ArgumentParser(description='Run Entity in vavado simulator')
    cl_add_entity(parser)
    vprint(0)("hello from ghdl_run_wrap")
    parser.add_argument('--cocotb_file',   help='path to the cocotb File ',default="None", required=True)
    cl_add_gui(parser=parser)
    args = extract_cl_arguments(parser, x)

    run_cocotb(args= args)
    

add_program("run-ghdl", ghdl_run_wrap)


    