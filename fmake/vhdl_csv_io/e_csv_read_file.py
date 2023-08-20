e_csv_read_file = """



library ieee;
use ieee.std_logic_1164.all;
use work.CSV_UtilityPkg.all;
use STD.textio.all;

entity csv_read_file is
  generic (
    FileName : string := "read_file_ex.txt";
    NUM_COL : integer := 3;
    HeaderLines : integer := 1

  );
  port (
    clk : in std_logic;
    reopen_file : in std_logic := '0';
    open_on_startup : in std_logic := '1';

    Rows : out c_integer_array(NUM_COL - 1 downto 0) := (others => 0);

    Index : out integer := 0;
    valid : out std_logic := '0'
  );
end csv_read_file;

architecture Behavioral of csv_read_file is
  signal i_valid : std_logic := '0';

  type state_t is (s_idle,  s_read_file);
  signal i_state : state_t := s_idle;

begin

  process (clk) is

    variable start_up : boolean := true;
    file input_buf : text; 
    variable currentline : line;

    variable V_Rows : c_integer_array(NUM_COL - 1 downto 0) := (others => 0);
    variable read_header : boolean := true;
  begin
    if (falling_edge(clk)) then
      i_valid <= '0';
      V_Rows := (others => 0);


      case i_state is
        when s_idle =>
         

          if (start_up  and  open_on_startup ='1') or reopen_file = '1' then
            start_up := false;
            FILE_OPEN(input_buf, FileName, READ_MODE);
            i_state <= s_read_file;
            read_header := true;
          end if;

        when s_read_file =>
          if read_header then
            for i in 0 to HeaderLines - 1 loop
                readline(input_buf, currentline);
     
            end loop;
            read_header := false;
          end if;


          if endfile(input_buf) then
            FILE_CLOSE(input_buf);
            i_state <= s_idle;
          else
            readline(input_buf, currentline);
            i_valid <= '1';
            for i in 0 to NUM_COL - 1 loop
              read(currentline, V_Rows(i));
            end loop;
          end if;
      end case;




      Rows <= V_Rows;
    end if;
  end process;

  valid <= i_valid;

end architecture;






"""