e_csv_write_file="""

library ieee;
  use ieee.std_logic_1164.all;


  use work.CSV_UtilityPkg.all;
  use STD.textio.all;
  



entity csv_write_file is
  generic (
    FileName : string := "read_file_ex.txt";
    NUM_COL : integer := 3;
    HeaderLines :string := "x, y, z"
  );
  port(
    clk : in sl;

    Rows : in c_integer_array(NUM_COL - 1  downto 0) := (others => 0)

  ); 
end csv_write_file;

architecture Behavioral of csv_write_file is
  constant Integer_width : integer := 5;
begin

  seq : process(clk) is
    file outBuffer : text open write_mode is FileName;  
    
    variable done_header : boolean := false;
    variable currentline : line;
    variable sim_time_len_v : natural := 0;
  begin
    if rising_edge(clk) then 
      --write(currentline, string'("asdasdasd"));
      if not done_header then 
        write(currentline, string'("Time, "));
        write(currentline, HeaderLines);
        writeline(outBuffer , currentline);

        write(currentline,  0 , right, Integer_width);
        for i in 0 to  NUM_COL - 1 loop 
          write(currentline, string'(", "));
          write(currentline,  0 , right, Integer_width);
          
        end loop;
        writeline(outBuffer , currentline);
        done_header := true;
      end if;

      write(currentline,  sim_time_len_v , right, Integer_width);
      for i in 0 to  NUM_COL - 1 loop 
        write(currentline, string'(", "));
        write(currentline,  Rows(i) , right, Integer_width);
        
      end loop;
      writeline(outBuffer , currentline);
      sim_time_len_v := sim_time_len_v +1;
    end if;
  end process;

end Behavioral;



"""