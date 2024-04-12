
import pandas as pd
from fmake.vhdl_programm_list import add_program
from fmake.generic_helper import  vprint, try_remove_file , save_file , load_file 
from fmake.generic_helper import extract_cl_arguments, cl_add_entity ,cl_add_OutputCSV, cl_add_gui, constants

import argparse

record_def = """
type reg_{module_name}_t is record
{members}
end record;\n\n    
""" 

procedure_def = """
{procedure_signature} is 
  begin

{body}

end procedure;

"""     

function_def = """
{function_signature} is
    variable ret : reg_{module_name}_t;
  begin

{body}
    return  ret;
end function;
"""     

unhandled_case = 'e\n        assert false report "Unhandled case" severity Failure;\n    end if;\n'

header = """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


package csv_register_top is 
type REG_instance is (
{instances}
);
end package;


"""     

package_header_and_body = """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.csv_register_top.all;

use work.rolling_register32_p.all;

    
package {package_name} is 

{records}

{ctr_header}

{read_header}

end package;


package body {package_name} is 

{ctr_body}

{read_body}

end package body;
   
   
    """

entity_no_arguments = """
library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;
    use work.csv_register_top.all;

    use work.rolling_register32_p.all;
    
    use work.reg_{module_name}_pac.all;
    
    use work.global_system_pack.all;

entity reg_{module_name} is 
    port(
        gSystem : in global_system_t;
        registers : out reg_{module_name}_t
    );
end entity;

architecture rtl of  reg_{module_name} is
    signal i_registers : reg_{module_name}_t := reg_{module_name}_t_ctr;

begin 

process (gSystem.clk) is 

begin 
    IF rising_edge(gSystem.clk) THEN
        read_registers(gSystem.reg, i_registers);
   end if;
end process;
    
    registers <=  i_registers;

end architecture;

"""

entity_with_arguments  = """
library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;
    use work.csv_register_top.all;

    use work.rolling_register32_p.all;
    
    use work.reg_{module_name}_pac.all;

entity reg_{module_name} is 
    generic (
        instance : in REG_instance
    ); 
    port(
        gSystem : in global_system;
        registers : out reg_{module_name}_t
    );
end entity;

architecture rtl of  reg_{module_name} is
    signal i_registers : reg_{module_name}_t := reg_{module_name}_t_ctr(instance);

begin 

process (gSystem.clk) is 

begin 
    IF rising_edge(gSystem.clk) THEN
        read_registers(gSystem.reg, instance, i_registers);
   end if;
end process;
    
    registers <=  i_registers;

end architecture;

"""


python_class_with_arguments = """   

class reg_{module_name}_t:
{ind}def __init__(self, reg, instance):
{ind}{ind}self.reg = reg
{ind}{ind}self.instance = instance

{members}

    """

python_class_no_arguments =  """
class reg_{module_name}_t:
{ind}def __init__(self, reg):
{ind}{ind}self.reg = reg

{members}


"""


def write_file(FileName, content):
    with open(FileName, "w") as f:
            f.write(content)




class register_exporter:

    def __init__(
            self, 
            register_file = "register_map.csv", 
            vhdl_output_folder = "klm-trg/src/generated/" , 
            python_output_file = "klm_trg_py_scripts/register_map.py" 
                 ) -> None:
        self.df = pd.read_csv(register_file, skip_blank_lines=True)
        self.vhdl_output_folder  = vhdl_output_folder
        self.python_output_file  = python_output_file
   
        pass

    def make_top(self):

        instances = ",\n".join("  " + instance for instance in self.df["instance"].unique())

        


        r = header.format(instances = instances )

        write_file(f"{self.vhdl_output_folder}/csv_register_top.vhd", r)
        
            

    def make_register_package(self):             
        ret =  extract_registers(self.df)
        for x in ret["records"].keys():

            package_name = f"reg_{x}_pac"
            content = package_header_and_body.format( 
                package_name = package_name,
                records = ret["records"][x],
                
                ctr_header = ret["ctr"][x]["header"],
                ctr_body = ret["ctr"][x]["body"],

                read_header = ret["read"][x]["header"],
                read_body = ret["read"][x]["body"]
            )
           
            vprint(10)(content)

            write_file(f"{self.vhdl_output_folder}/{package_name}.vhd", content)
            write_file(f"{self.vhdl_output_folder}/{package_name}_entity.vhd", ret["entity"][x])
             
        

    def make_python_package(self):
        ret = ""
        for i,x in self.df.groupby("module"):
            if x["instance"].unique().size == 1:
                ret += make_python_class_no_arguments(i, x)
            else:
                ret += make_python_class_with_arguments(i, x)
            
        vprint(10)(ret)
        write_file( self.python_output_file , ret)        
            

def make_default(x, reg_name= "ret"):
    
    #check if default is a number
    try:
        size_of_reg = x['size']
        t = "signed(to_signed(" if "s" in size_of_reg else "unsigned(to_unsigned(" if "u" in size_of_reg else "std_logic_vector(to_unsigned("
        r = f" {t}{str(int(x["default"]) )}, {reg_name}.{x["reg_name"]}'length ));\n"
        return r
    except:
        return x["default"] +";\n"
    
    



def create_vhdl_one_record(module_name, group):
    members = ""        
        # Remove duplicates and create record entries
    for _, row in group.drop_duplicates("reg_name").iterrows():
        vprint(10)(row['size'])
        size_of_reg = row['size']
        t = "signed" if "s" in size_of_reg else "unsigned" if "u" in size_of_reg else "std_logic_vector"
        size_of_reg = size_of_reg.replace("u","").replace("s","")
        members += f"  {row['reg_name']} : {t}({int(size_of_reg) - 1} downto 0);\n"

    record = record_def.format(
        module_name = module_name,
        members = members
    ) 

    return record

def create_vhdl_records(df):
    records = {}
    
    for module_name, group in df.groupby("module"):
        record = create_vhdl_one_record(module_name,  group)
        records[module_name] = record
            
    return records
    


def create_vhdl_ctr_functions_no_arguments(module_name, group):
    function_signature = f"function reg_{module_name}_t_ctr return reg_{module_name}_t"
    header = f"{function_signature};\n\n"
             

    function_body = ""
              
    for _, row in group.drop_duplicates("reg_name").iterrows():
        function_body += f"    ret.{row["reg_name"]} := {make_default(row)}"
                

    body = function_def.format(
        function_signature = function_signature,
        module_name = module_name,
        body = function_body
    )

    return {
           "header" : header,
           "body"   : body
    }

def create_vhdl_ctr_functions_with_arguments(module_name, group):
    function_signature = f"function reg_{module_name}_t_ctr(instance : in REG_instance) return reg_{module_name}_t"
    header = f"{function_signature};\n\n"
             
    
    function_body  = "    "
    
    for u in group["instance"].unique():
        function_body     += "if instance = " + u +" then\n"
        for e in group[group.instance == u].iterrows():
            function_body += "        ret." +  e[1]["reg_name"] +" := " +  make_default(e[1]) 
        function_body += "    els"
    
    function_body += unhandled_case

    body = function_def.format(
        function_signature = function_signature,
        module_name = module_name,
        body = function_body
    )

    

    return {
        "header" : header,
        "body"   : body
        }            

def create_vhdl_ctr_functions(df):
    ret = {}
    for i,x in df.groupby("module"):
        if len(x["instance"].unique()) == 1:
            ret[i] = create_vhdl_ctr_functions_no_arguments(i, x)
        else:
            ret[i] = create_vhdl_ctr_functions_with_arguments(i,x)
            
    return ret
    


def create_vhdl_read_procedure_no_argument(module_name, group):
    procedure_signature = f"procedure read_registers(reg: in register_32T; signal reg_out: out reg_{module_name}_t )"
    header = f"{procedure_signature};\n" 
             

    defaults = ""
    
    for e in group.iterrows():
        defaults += f"    reg_out.{e[1]["reg_name"]} <= {make_default(e[1], "reg_out"  )}" if e[1]["AutoReset"] == 1 else ""   
        defaults += f"    read_data_s(reg, {str(e[1]["addr"])}, reg_out.{e[1]["reg_name"]});\n"              
    
    body = procedure_def.format(
        procedure_signature = procedure_signature,
        body = defaults   
    )

    return {
        "header" : header,
        "body"   : body
    }

def create_vhdl_read_procedure_with_argument(module_name, group):
    procedure_signature = f"procedure read_registers(reg: in register_32T; instance : in REG_instance; signal  reg_out: out reg_{module_name}_t )"
    header = f"{procedure_signature};\n" 


    
    procedure_body = "    "
         
    for u in group["instance"].unique():
        procedure_body += "if instance = " + u +" then\n"
        for e in group[group.instance == u].iterrows():
            procedure_body += f"        reg_out.{e[1]["reg_name"]} <= {make_default(e[1], "reg_out"  )}" if e[1]["AutoReset"] == 1 else ""
            procedure_body += f"        read_data_s(reg, {str(e[1]["addr"])}, reg_out.{e[1]["reg_name"]} );\n"
        procedure_body += "    els"


    procedure_body += unhandled_case
    

    body = procedure_def.format(
        procedure_signature = procedure_signature,
        body = procedure_body   
    )

   
    return {
        "header" : header,
        "body"   : body
    }

def create_vhdl_read_procedure(df):
    ret = {}
    for i,x in df.groupby("module"):
        if len(x["instance"].unique()) == 1:
            ret[i] = create_vhdl_read_procedure_no_argument(i, x)
        else:
            ret[i] = create_vhdl_read_procedure_with_argument(i, x)
    return ret



def create_vhdl_entity_no_arguments(module_name, group):
    
    
    entity  = entity_no_arguments.format(
        module_name = module_name

    )
    
    return entity

def create_vhdl_entity_with_arguments(module_name, group):

    
    entity = entity_with_arguments.format(
        module_name = module_name
    )
   
    return entity



def create_vhdl_entity(df):
    ret = {}
    for i,x in df.groupby("module"):
        if len(x["instance"].unique()) == 1:
            ret[i] = create_vhdl_entity_no_arguments(i, x)
        else:
            ret[i] = create_vhdl_entity_with_arguments(i, x)
    return ret


def extract_registers(df):
    ret = {}

    ret["records"] = create_vhdl_records(df)
    ret["ctr"]     = create_vhdl_ctr_functions(df)
    ret["read"]    = create_vhdl_read_procedure(df)
    
    ret["entity"]    = create_vhdl_entity(df)
    return ret
        

set_reg  =  {
        1 : "self.reg.set_reg(",
        4 : "self.reg.set_register("
    }
ind = "    "
def make_python_class_no_arguments(module_name, group):

    
    members = ""
    
    
    for i1,x1 in group.groupby("reg_name"):
        members += f"{ind}def {i1}(self, value):\n"
        for e in x1.iterrows():
            members += f"{ind}{ind}{set_reg[e[1]["write"]] + str(e[1]["addr"])}, value)\n\n"

    ret = python_class_no_arguments.format(
        module_name = module_name,
        ind = ind,
        members = members
    )
    

    return ret                    
                    
def make_python_class_with_arguments(module_name, group):
    members =""   
    for i1,x1 in group.groupby("reg_name"):
        members += f"{ind}def {i1}(self, value):\n"
        for e in x1.iterrows():
            members += f"{ind}{ind}if self.instance == '{e[1]["instance"]}':\n"        
            members += f"{ind}{ind}{ind}{set_reg[e[1]["write"]] + str(e[1]["addr"])}, value)\n\n"

    ret = python_class_with_arguments.format(
        module_name= module_name,
        ind = ind,
        members = members
    ) 
    
    return ret



    
    

def run_export_registers_from_csv(register_file, vhdl_output_folder, python_output_file):
    ex = register_exporter(
        register_file, vhdl_output_folder, python_output_file
    )

    ex.make_top()
    ex.make_register_package()
    ex.make_python_package()


def export_registers_from_csv(x):
    parser = argparse.ArgumentParser(description='Run export_registers_from_csv')
    
    vprint(0)("hello from export_registers_from_csv")
    parser.add_argument('--csv',   help='Path to the input file', required=True)
    parser.add_argument('--vhd',   help='Path to the output vhdl folder', required=True)
    parser.add_argument('--py',   help='Path to the output python file', required=True)

    args = extract_cl_arguments(parser, x)

    register_file = args.csv
    vhdl_output_folder = args.vhd
    python_output_file =args.py
    
    run_export_registers_from_csv(register_file, vhdl_output_folder, python_output_file)


add_program("export-registers", export_registers_from_csv)


    