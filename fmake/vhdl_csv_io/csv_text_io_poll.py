from fmake.generic_helper import constants

csv_text_io_poll = """



library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.CSV_UtilityPkg.all;

use STD.textio.all;


entity csv_text_io_poll is 
generic (
    FileName : string := "{text_io_query}";
    read_NUM_COL : integer := 3;
    write_NUM_COL : integer := 3;
    HeaderLines : string := "x,y,z"
);
port (
  clk : in std_logic;

  read_Rows : out  c_integer_array(read_NUM_COL - 1 downto 0) := (others => 0);
  read_Rows_valid : out std_logic;

  write_Rows  : in c_integer_array(write_NUM_COL - 1  downto 0) := (others => 0);
  write_Rows_valid : in std_logic := '0'
);
end entity;

architecture rtl of csv_text_io_poll is

    constant send_lock_FileName    : string    := FileName & "{send_lock}";
    constant send_FileName         : string    := FileName & "{send}";
    
    constant receive_FileName      : string    := FileName & "{receive}";
    constant receive_lock_FileName : string    := FileName & "{receive_lock}";

    type state_t is (s_idle, s_read,s_write,  s_write_poll, s_done , s_reset );
    signal i_state : state_t := s_reset;

    signal last_index : integer := 0;


    signal reopen_file : std_logic := '0';

    signal valid : std_logic := '0';


    constant NUM_COL_index : integer := 1;
    
    signal Rows_index : c_integer_array(NUM_COL_index - 1 downto 0) := (others => 0);
    signal valid_index : std_logic := '0';
    signal reopen_file_index : std_logic := '0';

    
    signal reopen_file_write : std_logic := '0';
    signal done : std_logic := '0';

    signal Rows_write_poll : c_integer_array(0 downto 0) := (others => 0);
    signal valid_Rows_write_poll : std_logic := '0';
    signal reopen_Rows_write_poll : std_logic := '0';
    signal done_Rows_write_poll : std_logic := '0';


    signal i_write_Rows_valid : std_logic := '0';
    signal i_write_Rows_valid1 : std_logic := '0';
begin


    process (clk) is

    begin
        if rising_edge(clk) then
            reopen_file_index <= '0';
            reopen_file <= '0';
            reopen_file_write <= '0';
            reopen_Rows_write_poll <= '0';
            valid_Rows_write_poll<= '0';
            done_Rows_write_poll <= '0';
            done <= '0';
    
            

            case i_state is 
            when s_idle => 
                
                if valid_index = '0' then 
                    reopen_file_index <= '1';
                end if;
                if  Rows_index(0) = -1 then 
                    assert false report "Test: OK" severity failure;
                elsif  Rows_index(0) = -2 then 
                    reopen_file_write <= '1';
                    reopen_Rows_write_poll <= '1';
                    i_state <= s_write_poll;
                elsif  Rows_index(0) > last_index then 
                    last_index <= Rows_index(0);
                    reopen_file <= '1';
                    reopen_file_write <= '1';
                    reopen_Rows_write_poll <= '1';
                    i_state <= s_read;
                end if;
            when s_read => 
                if  write_Rows_valid = '1' then 
                    i_state <= s_write;
                end if;
            when s_write => 
                if write_Rows_valid = '0' then 
                    done <= '1';
                    i_state <= s_write_poll;
                end if;
            when s_write_poll => 
                valid_Rows_write_poll<= '1';
                Rows_write_poll(0) <= last_index;
                i_state <= s_done ;

            when s_done =>
                done_Rows_write_poll <= '1';
                i_state <= s_idle;
            
            when s_reset => 
                last_index <= 0;
                i_write_Rows_valid <= '1';
                i_state <= s_write_poll;

            end case;
            




        end if;

    end process;



    index_reader : entity work.csv_read_file
        generic map(
            FileName => send_lock_FileName,
            NUM_COL => NUM_COL_index,
            HeaderLines => 0
            ) port map (
            clk => clk,
            Rows => Rows_index,
            reopen_file => reopen_file_index,
            open_on_startup => '1',

            Index => open,
            valid => valid_index
        );

    csv_r : entity work.csv_read_file
        generic map(
            FileName => send_FileName,
            NUM_COL => read_NUM_COL,
            HeaderLines => 1
            ) port map (
            clk => clk,
            Rows => read_Rows,
            reopen_file => reopen_file,
            open_on_startup => '0',
            Index => open,
            valid => valid
        );
    read_Rows_valid <= valid;

    
    i_write_Rows_valid1 <= i_write_Rows_valid or  write_Rows_valid;

u_csv_write_file : entity work.csv_write_file
    generic map(
            FileName => receive_FileName,
            NUM_COL => write_NUM_COL,
            HeaderLines =>  HeaderLines
        ) port map (
            reopen_file => reopen_file_write,
            clk => clk,
            Rows => write_Rows,
            valid => i_write_Rows_valid1,
            done => done

    );

u_poll_write_file : entity work.csv_write_file
    generic map(
            FileName => receive_lock_FileName,
            NUM_COL => 1,
            HeaderLines =>  HeaderLines
        ) port map (
            reopen_file => reopen_Rows_write_poll,
            clk => clk,
            Rows => Rows_write_poll,
            valid => valid_Rows_write_poll,
            done => done_Rows_write_poll

    );

end architecture;



""".format(
    text_io_query = constants.text_IO_polling,
    send_lock     = "/"+ constants.text_io_polling_send_lock_txt,
    send          = "/"+ constants.text_io_polling_send_txt,
    receive       = "/"+ constants.text_io_polling_receive_txt, 
    receive_lock  = "/"+ constants.text_io_polling_receive_lock_txt 
)