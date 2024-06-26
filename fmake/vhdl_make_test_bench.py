



from  fmake.vhdl_make_test_bench_names   import get_IO_pgk_name, get_writer_record_name, get_reader_record_name, get_reader_entity_name, get_includes, get_writer_entity_name

from  fmake.vhdl_dependency_db           import get_dependency_db
from  fmake.vhdl_entity_class            import vhdl_entity
from  fmake.vhdl_merge_split_test_cases  import merge_test_case
from  fmake.generic_helper               import save_file, try_make_dir, cl_add_entity, join_str
from  fmake.vhdl_programm_list           import add_program 
from  fmake.generic_helper               import vprint, extract_cl_arguments, constants

import argparse
import numpy as np 

import pandas as pd
import wget


class test_bench_maker:
    def __init__(self, EntityName,NumberOfRows,OutputPath) -> None:
        
        self.InputFile = get_dependency_db().entity2FileName(EntityName)
        self.NumberOfRows = int(NumberOfRows)
        self.entetyCl  =  vhdl_entity(self.InputFile)
        get_dependency_db().get_dependencies(EntityName)

        self.OutputPath = OutputPath
        
        self.CSV_in_FileName =  self.OutputPath+"/"+get_test_bench_file_basename(self.entetyCl)+".csv"
        self.CSV_out_FileName =  self.OutputPath+"/"+get_test_bench_file_basename(self.entetyCl)+"_out.csv"


    def make_package_file(self):
        et_name = self.entetyCl.name()
        write_pgk_file = self.OutputPath+"/"+et_name +"_IO_pgk.vhd"
        
       
        write_pgk = get_IO_pgk_name(self.entetyCl)
        
        
        userPackages = "" 
        for i, x in get_dependency_db().df[(get_dependency_db().df.filename ==self.InputFile) & (get_dependency_db().df["type"] == "packageUSE" )].iterrows():
                userPackages += "use work." + x["name"] + ".all;\n"
        
        records =""
        records += self.make_generic_constants()
        records += self.make_IO_record("none")
        records +="\n\n"
        records += self.make_IO_record("out")

        write_pgk_str = '''

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use ieee.std_logic_arith.all;
use work.CSV_UtilityPkg.all;


-- Start Include user packages --
{userPackages}
-- End Include user packages --

package {write_pgk} is

{records}

end package;

package body {write_pgk} is

end package body {write_pgk};

        '''.format(
            userPackages=userPackages,
            write_pgk=write_pgk,
            records=records
        )

        save_file(write_pgk_file,write_pgk_str)

            

        return write_pgk

    def make_generic_constants(self):
        df = self.entetyCl.df_entity[self.entetyCl.df_entity.generic_or_port == "generic"]
        ret = ""
        for i in range(len(df)):
            ret += "  constant " + df.iloc[i]["port_name"] + " : " + df.iloc[i]["port_type"] + " := " + df.iloc[i]["default"]  +';\n'
        
        return ret
        
        
    def make_IO_record(self,inOutFilter):
        if inOutFilter == "none":
            IO_record_name = get_writer_record_name(self.entetyCl)
        else :
            IO_record_name =get_reader_record_name(self.entetyCl)
        
        ports = self.entetyCl.ports(Filter= lambda x : x["InOut"] != inOutFilter)

        RecordMember = ""
        defaultsstr = ""
        
        for i, x in ports.iterrows():
            RecordMember += "    " + x["port_name"] + " : "+ x["port_type"] +  ";  \n"
        
            

        IO_record = '''
type {IO_record_name} is record
{RecordMember}
end record;
'''.format(
            IO_record_name=IO_record_name,
            RecordMember=RecordMember,
            defaultsstr=defaultsstr
        )
        return IO_record

    def make_entities(self):
        read_entity = make_read_entity(self.entetyCl)
        write_entity = make_write_entity(self.entetyCl)
        tb_entity,test_bench = make_test_bench_for_test_cases(self.entetyCl)
  
        save_file(self.OutputPath+"/"+get_test_bench_file_basename(self.entetyCl)+".vhd" ,  read_entity+write_entity+test_bench) 


    def make_sim_csv_file(self, FilterOut):
        FileName =  self.CSV_in_FileName if FilterOut =="out" else self.CSV_out_FileName
        
           
        ports = self.entetyCl.ports(Filter= lambda a : a["InOut"] != FilterOut, ExpandTypes =True)
        
        delimiter=", " 
        start = "" if FilterOut == "out" else "time  " + delimiter
        ret = ""
        ret = join_str(ports["plainName"] , Delimeter= delimiter  ,start= start , end="\n" )
        
        start = "" if FilterOut == "out" else "1, " 
        line =  join_str( np.int32(np.zeros(len(ports))) , Delimeter= delimiter, end="\n"  ,start= start )
            
        for i in range(self.NumberOfRows):
            ret +=  line
            

        save_file(FileName,Data=ret )      
            

    def get_test_bench_file_basename(self):
        et_name   =  self.entetyCl.name()
        tb_entity =  et_name +"_tb_csv"     
        return tb_entity

    def make_xml_test_case(self):
        testCaseName = self.OutputPath +"/"+ self.get_test_bench_file_basename()+".testcase.xml"
        testCaseXml='''<?xml version="1.0"?>
<testcases>
    <testcase name="{et_name}empty_test01">
        <descitption> autogenerated empty test case</descitption>
        <inputfile>{sim_in_filename}</inputfile>
        <referencefile>{sim_out_filename}</referencefile>
        <entityname>{et_name}</entityname>
        <tc_type>Unclear</tc_type>
        <difftool>diff</difftool>
        <RegionOfInterest>
            <Headers></Headers>
            <Lines></Lines>
        </RegionOfInterest>
        <Stimulus/>
        <Reference/>
    </testcase>
</testcases>
        '''.format(
            et_name= self.get_test_bench_file_basename(),
            sim_in_filename=self.get_test_bench_file_basename()+".csv",
            sim_out_filename=self.get_test_bench_file_basename()+"_out.csv",

        )

        save_file(testCaseName, testCaseXml)
        merge_test_case(testCaseName)

      




def make_read_entity(entityDef):
    reader_entity = get_reader_entity_name(entityDef)
    reader_pgk = get_IO_pgk_name(entityDef)
    
    ports = entityDef.ports(Filter= lambda a : a["InOut"] == "in",  ExpandTypes = True)
    
    connections=""
    index = 0
    for i,x in ports.iterrows():
        connections += '  csv_from_integer(csv_r_data(' +str(index) +'), data.' + x["port_name"] + ');\n'
        index +=1


    reader_entity_str = '''

{includes}

use work.{reader_pgk}.all;


entity {reader_entity}  is
    generic (
        FileName : string 
    );
    port (
        clk : in std_logic ;
        eof : out std_logic;
        data : out {reader_record_name}
    );
end entity;   

architecture Behavioral of {reader_entity} is 

  constant  NUM_COL    : integer := {NUM_COL};
  signal    csv_r_data : c_integer_array(NUM_COL -1 downto 0)  := (others=>0)  ;
  signal valid : std_logic := '0';
  signal valid_1 : std_logic := '0';
  signal valid_2 : std_logic := '0';
  
begin

  csv_r :entity  work.csv_read_file 
    generic map (
        FileName    =>  FileName, 
        NUM_COL     =>  NUM_COL,
        HeaderLines =>  2
    ) port map (
        clk   => clk,
        Rows  => csv_r_data,
        valid => valid
    );
    
  eof <= not valid;

  process(clk) is 
  begin 
  if rising_edge(clk) then 
    valid_2 <= valid_1;
    valid_1 <= valid;
    if valid_2 = '1' and valid_1 = '0' then 
      assert false report "Test: OK" severity failure;
    end if;
  end if;
  end process;
  
{connections}

end architecture;
---------------------------------------------------------------------------------------------------
    '''.format(
    includes=get_includes(),
    reader_pgk=reader_pgk,
    reader_entity=reader_entity,
    reader_record_name=get_reader_record_name(entityDef),
    connections=connections,
    NUM_COL=str(len(ports))
    )
    

    return reader_entity_str

   
def make_out_header(entityDef):
    ports = entityDef.ports( ExpandTypes = True)

    HeaderLines=""
    start = ""
    for i,x in ports.iterrows():
            
        HeaderLines += start + x["plainName"]
        start=", "

    return HeaderLines


def make_write_entity(entityDef,path="."):
    write_entity = get_writer_entity_name(entityDef)
    write_pgk = get_IO_pgk_name(entityDef)

    ports = entityDef.ports(ExpandTypes = True)


    HeaderLines = make_out_header(entityDef)


    connections=""
    index = 0
    for i, x in ports.iterrows():
        connections += '  csv_to_integer(data.' + x["port_name"] + ', data_int(' +str(index) +') );\n'
        index += 1


    writer_entity_str='''

{includes}

use work.{write_pgk}.all;

entity {write_entity}  is
    generic ( 
        FileName : string 
    ); port (
        clk : in std_logic ;
        eof : in std_logic;
        data : in {writer_record_name}
    );
end entity;

architecture Behavioral of {write_entity} is 
  constant  NUM_COL : integer := {NUM_COL};
  signal data_int   : c_integer_array(NUM_COL - 1 downto 0)  := (others=>0);
  signal reopen_file : std_logic := '0';
begin

    csv_w : entity  work.csv_write_file 
        generic map (
            FileName    =>   FileName,
            HeaderLines =>   "{HeaderLines}",
            NUM_COL     =>   NUM_COL ,
            empty_line  =>   1
        ) port map(
            clk         => clk, 
            Rows        => data_int,
            done        => eof,
            reopen_file => reopen_file
        );
    reopen_file <= not eof;

{connections}

end architecture;
---------------------------------------------------------------------------------------------------
    '''.format(
        includes=get_includes(),
        write_entity=write_entity,
        write_pgk=write_pgk,
        writer_record_name=get_writer_record_name(entityDef),
        HeaderLines=HeaderLines,
        connections=connections,
        NUM_COL=str(len(ports)+1)
    )

    return writer_entity_str
    

        

        
def get_test_bench_file_basename(entityDef):
    et_name = entityDef.name()
    tb_entity =  et_name +"_tb_csv"     
    return tb_entity

def make_generic_str(df_entity):        
    df_generics = df_entity[df_entity.generic_or_port == "generic"]
        
    
    generic_list = df_generics.apply( lambda x:  x["port_name"] + " => " + x["port_name"] , axis = 1 )
    generic_str = join_str(generic_list , start= "  generic map(\n" , end=  "  )" ,Delimeter= ",\n  " , IgnoreIfEmpty= True )
    
    return generic_str


def make_input2OutputConnection(entityDef):
    
    ports = entityDef.ports(Filter= lambda a : a["InOut"] == "in", RemoveClock = True)
    clk_port = entityDef.get_clock_port()
    input2OutputConnection = "  data_out.clk <=clk;\n"
    if entityDef.IsUsingGlobals():
        input2OutputConnection ="""  
  data_out.{globals}.clk <=clk;
  data_out.{globals}.reg <= data_in.{globals}.reg;
  data_out.{globals}.rst <= data_in.{globals}.rst;
  """.format(
      globals = clk_port.iloc[0]["port_name"]
    )
    
        

    for i,x in ports.iterrows():
        input2OutputConnection +=  '  data_out.' + x['port_name'] + " <= data_in." + x['port_name'] +";\n"
    
    return input2OutputConnection

def make_port_str(entityDef):
    clk_port = entityDef.get_clock_port()
    ports = entityDef.ports(RemoveClock = True)
    
    start = "\n  clk => clk,\n  " if not entityDef.IsUsingGlobals() else "\n  " + clk_port.iloc[0]["port_name"] + " => data_out."+ clk_port.iloc[0]["port_name"] +",\n  "

    portsstr = join_str( ports.apply(lambda x:  "  " + x["port_name"] +" => data_out." + x["port_name"] , axis = 1  ) , start= start, Delimeter= ",\n")
    
        
    return portsstr
        
    
def make_test_bench_for_test_cases(entityDef):
    et_name = entityDef.name()

    tb_entity = get_test_bench_file_basename(entityDef)
    write_pgk = get_IO_pgk_name(entityDef)
    
    input2OutputConnection = make_input2OutputConnection(entityDef)
    portsstr =make_port_str(entityDef)
    generic_str = make_generic_str(entityDef.df_entity)        
    
    testBenchStr = '''
{includes}
use work.{write_pgk}.all;

entity {tb_entity} is 
end entity;

architecture behavior of {tb_entity} is 
  signal clk : std_logic := '0';
  signal data_in : {readerRecordName};
  signal data_out : {writerRecordName};
  signal  eof : std_logic;
begin 

  clk_gen : entity work.ClockGenerator generic map ( CLOCK_period => 10 ns) port map ( clk => clk );

  csv_read : entity work.{reader_entity_name} 
    generic map (
        FileName => "./{tb_entity}.csv" 
    ) port map (
          clk => clk ,data => data_in , eof => eof
    );
 
  csv_write : entity work.{writer_entity_name}
    generic map (
        FileName => "./{tb_entity}_out.csv" 
    ) port map (
        clk => clk ,data => data_out , eof => eof
    );
  

{input2OutputConnection}

DUT :  entity work.{et_name} {generic_str} port map(
{ports}
    );

end architecture;
---------------------------------------------------------------------------------------------------
    '''.format(
  includes=get_includes(),
  write_pgk=write_pgk,
  tb_entity=tb_entity,
  et_name=et_name,
  readerRecordName=get_reader_record_name(entityDef),
  writerRecordName=get_writer_record_name(entityDef),
  reader_entity_name=get_reader_entity_name(entityDef),
  writer_entity_name= get_writer_entity_name(entityDef),
  input2OutputConnection=input2OutputConnection,
  ports=portsstr,
  generic_str = generic_str
    )



    return tb_entity,testBenchStr





def make_test_bench_main(EntityName,NumberOfRows,OutputPath):
    try_make_dir(OutputPath)
    tb_maker = test_bench_maker(EntityName=EntityName,NumberOfRows=NumberOfRows, OutputPath=OutputPath)  
    tb_maker.make_package_file()
    tb_maker.make_entities()
    tb_maker.make_sim_csv_file("out")
    tb_maker.make_sim_csv_file("none")
    tb_maker.make_xml_test_case()



   



   #make_stand_alone_impl( entityDef = tb_maker.entetyCl , path =  OutputPath, suffix= "")

    vprint(0)("generated test bench file", tb_maker.get_test_bench_file_basename())
    



def make_test_bench_main_wrap(x):
    parser = argparse.ArgumentParser(description='Creates Test benches for a given entity')
    
    cl_add_entity(parser)
    parser.add_argument('--OutputPath', help='Path to where the test bench should be created',default="" ,required=True)
    parser.add_argument('--NumberOfRows', help='Number of Rows in the Autogenerated CSV Files',default="1000")
    
    args = extract_cl_arguments(parser= parser,x=x)
    make_test_bench_main(args.entity,args.NumberOfRows, args.OutputPath)
           
    URL = constants.empty_testbench_xlsm_URL
    response = wget.download(URL, args.OutputPath+"/" +args.entity+".xlsm")
    vprint(0)("\ndone make-testbench\n\n")

add_program("make-testbench", make_test_bench_main_wrap)   

