e_csv_write_file="""


library ieee;
use ieee.std_logic_1164.all;
use work.CSV_UtilityPkg.all;
use STD.textio.all;
entity csv_write_file is
  generic (
    FileName : string := "read_file_ex.txt";
    NUM_COL : integer := 3;
    HeaderLines : string := "x, y, z"
  );
  port (
    clk : in sl;

    reopen_file : in std_logic := '0';
    done  : in std_logic := '0';
    valid : in std_logic := '1';
    Rows : in c_integer_array(NUM_COL - 1 downto 0) := (others => 0)

  );
end csv_write_file;

architecture Behavioral of csv_write_file is
  constant Integer_width : integer := 5;
  type state_t is (s_idle, s_open , s_header , s_write);
  signal state : state_t := s_idle;

begin

  seq : process (clk) is
    file outBuffer : text;

    variable done_header : boolean := false;
    variable currentline : line;
    variable sim_time_len_v : natural := 0;
  begin
    if rising_edge(clk) then
     
    case state is 
      when s_idle => 
      sim_time_len_v := 0;
      if reopen_file = '1' then 
        FILE_OPEN(outBuffer, FileName, write_mode);
        state <= s_open;
      end if;

      when s_open => 
        state <= s_header;

      when s_header =>
        write(currentline, string'("Time, "));
        write(currentline, HeaderLines);
        writeline(outBuffer, currentline);

      --  write(currentline, 0, right, Integer_width);
		  state <= s_write;
      when s_write => 
        if valid = '1' then
          write(currentline, sim_time_len_v, right, Integer_width);
          for i in 0 to NUM_COL - 1 loop
            write(currentline, string'(", "));
            write(currentline, Rows(i), right, Integer_width);

          end loop;
          writeline(outBuffer, currentline);
          sim_time_len_v := sim_time_len_v + 1;
        end if;

        if done = '1' then
          state <= s_idle;
          FILE_CLOSE(outBuffer);
        end if;

      end case;

    end if;
  end process;

end Behavioral;


"""