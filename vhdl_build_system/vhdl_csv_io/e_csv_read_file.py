e_csv_read_file = """
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE work.CSV_UtilityPkg.ALL;
USE STD.textio.ALL;

ENTITY csv_read_file IS
  GENERIC (
    FileName : STRING := "read_file_ex.txt";
    NUM_COL : INTEGER := 3;
    HeaderLines : INTEGER := 1

  );
  PORT (
    clk : IN STD_LOGIC;

    Rows : OUT c_integer_array(NUM_COL -1 downto 0)   := (OTHERS => 0);

    Index : OUT INTEGER := 0;
    eof : OUT STD_LOGIC := '0'
  );
END csv_read_file;

ARCHITECTURE Behavioral OF csv_read_file IS

BEGIN

  PROCESS (clk) IS
    FILE input_buf : text open read_mode is FileName; -- text is keyword
    variable currentline : line;
    variable line_counter : natural := 0;
    VARIABLE V_Rows : c_integer_array(NUM_COL -1 downto 0)  := (OTHERS => 0);
  BEGIN
    IF (falling_edge(clk)) THEN
      while line_counter <= HeaderLines loop
        readline(input_buf, currentline);
        line_counter := line_counter + 1;
      end loop;

      readline(input_buf, currentline);

    	for i in 0 to  NUM_COL -1 loop
    		read(currentline, V_Rows(i));
    	end loop;
      Rows <= V_Rows;
    END IF;
  END PROCESS;
END Behavioral;

"""