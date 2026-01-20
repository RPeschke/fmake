csv_register_interface = """

library ieee;
  use ieee.std_logic_1164.all;
  use ieee.numeric_std.all;
  use work.type_conversions_pgk.all;
  use work.CSV_UtilityPkg.all;

entity csv_register_interface is
  generic (
    FileName           : string  := "text_io_query";
    use_internal_clock : boolean := true;
    CLOCK_period       : time    := 10 ns;
    NInputs            : integer := 1;
    use_burst_mode     : boolean := false;
    BURST_length       : integer := 50
  );
  port (
    clk           : in  std_logic                             := '0';
    clk_out       : out std_logic                             := '0';

    -- register interface 
    reg_addr      : out std_logic_vector(15 downto 0);
    reg_value     : out std_logic_vector(31 downto 0);

    data_in       : in  c_integer_array(NInputs - 1 downto 0) := (others => 0);
    data_in_valid : in  std_logic                             := '0'
  );
end entity;

architecture rtl of csv_register_interface is

  function generate_header(N : integer) return string is
    variable result : string(1 to N * 4 - 1) := (others => ' ');
    variable pos    : integer                := 1;
  begin
    for i in 1 to N loop
      if i < 10 then
        result(pos) := 'x';
        result(pos + 1) := character'val(character'pos('0') + i);
        pos := pos + 2;
      elsif i < 100 then
        result(pos) := 'x';
        result(pos + 1) := character'val(character'pos('0') + i / 10);
        result(pos + 2) := character'val(character'pos('0') + (i mod 10));
        pos := pos + 3;
      end if;
      if i < N then
        result(pos) := ',';
        pos := pos + 1;
      end if;
    end loop;
    return result(1 to pos - 1);
  end function;

  signal i_clk     : std_logic := '0';
  signal i_clk_out : std_logic := '0';
  constant read_NUM_COL  : integer := 3;
  constant write_NUM_COL : integer := read_NUM_COL + NInputs;
  constant HeaderLines   : string  := "addr,value,ID," & generate_header(NInputs);
  signal read_Rows   : c_integer_array(read_NUM_COL - 1 downto 0) := (others => 0);
  signal read_Rows_1 : c_integer_array(read_NUM_COL - 1 downto 0) := (others => 0);

  signal read_Rows_valid  : std_logic;
  signal read_Rows_valid1 : std_logic;

  signal write_Rows       : c_integer_array(write_NUM_COL - 1 downto 0) := (others => 0);
  signal write_Rows_valid : std_logic                                   := '0';

  signal I_BURST_COUNT : integer := 0;
  type burst_state_t is (s_idle, s_burst);
  signal i_burst_state : burst_state_t := s_idle;
begin

  i_clk_out <= clk when use_internal_clock = false else i_clk;
  clk_out   <= i_clk_out;

  clk_gen: entity work.ClockGenerator
    generic map (
      CLOCK_period => CLOCK_period
    )
    port map (
      clk => i_clk
    );

  u_dut: entity work.csv_text_io_poll
    generic map (
      FileName      => FileName,
      read_NUM_COL  => read_NUM_COL,
      write_NUM_COL => write_NUM_COL,
      HeaderLines   => HeaderLines
    )
    port map (
      clk              => i_clk_out,

      read_Rows        => read_Rows,
      read_Rows_valid  => read_Rows_valid,

      write_Rows       => write_Rows,
      write_Rows_valid => write_Rows_valid
    );

  process (i_clk_out) is
  begin
    if rising_edge(i_clk_out) then

      read_Rows_1 <= read_Rows;
      read_Rows_valid1 <= read_Rows_valid;
      write_Rows(read_Rows'range) <= read_Rows_1(read_Rows'range);
      for i in 0 to NInputs - 1 loop
        write_Rows(3 + i) <= data_in(i);
      end loop;

      write_Rows_valid <= '0';
      case i_burst_state is
        when s_idle =>
          I_BURST_COUNT <= 0;
          if read_Rows_valid1 = '1' then
            write_Rows_valid <= '1';
            if use_burst_mode then
              i_burst_state <= s_burst;
            end if;
          end if;
        when s_burst =>
          write_Rows_valid <= '1';
          I_BURST_COUNT <= I_BURST_COUNT + 1;
          
          
          if data_in_valid = '0' then
            i_burst_state <= s_idle;
            write_Rows_valid <= '0';
          end if;
          
          
          if I_BURST_COUNT = BURST_length then
            --watchdog to prevent infinite bursts
            i_burst_state <= s_idle;
          end if;



      end case;

    end if;
  end process;

  csv_from_integer(read_Rows(0), reg_addr);
  csv_from_integer(read_Rows(1), reg_value);

end architecture;

"""
