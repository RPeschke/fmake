from fmake.generic_helper import constants

csv_text_io_poll = """





library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.CSV_UtilityPkg.all;

use STD.textio.all;


entity csv_text_io_poll is 
generic (
    FileName : string := "text_io_query";
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

    constant request_index_filename    : string    := FileName & "/send_lock.txt";
    constant request_data_filename         : string    := FileName & "/send.txt";
    
    constant response_data_filename      : string    := FileName & "/receive.txt";
    constant response_index_filename : string    := FileName & "/receive_lock.txt";

    type state_t is (s_idle, s_read,s_write,  s_write_poll, s_done, s_reset );
    signal i_state : state_t := s_reset;

    signal last_index : integer := 0;





    constant NUM_COL_index : integer := 1;
    
    signal request_index_rows  : c_integer_array(NUM_COL_index - 1 downto 0) := (others => 0);
    signal response_index_rows : c_integer_array(NUM_COL_index - 1  downto 0) := (others => 0);
    

    signal i_write_Rows_valid : std_logic := '0';


    type csv_reader_t is record
        reopen_file : std_logic;
        open_on_startup : std_logic;
        Index :  integer ;
        valid : std_logic ;
    end record;

    constant csv_reader_t_null : csv_reader_t := (
        reopen_file => '0',
        open_on_startup => '0',
        Index => 0,
        valid => '0'
    );

    type writer_state_t is (s_idle, s_open, s_closing);

    type csv_writer_t is record
        state : writer_state_t;
        done : std_logic;
        reopen_file : std_logic;
        Index :  integer ;
        valid : std_logic ;
        old_valid : std_logic;
    end record;

    constant csv_writer_t_null : csv_writer_t := (
        state => s_idle,
        reopen_file => '0',
        done => '0',
        Index => 0,
        valid => '0',
        old_valid => '0'
    );

    signal request_index : csv_reader_t := csv_reader_t_null;
    signal request_data : csv_reader_t := csv_reader_t_null;

    signal response_index : csv_writer_t := csv_writer_t_null;
    signal response_data : csv_writer_t := csv_writer_t_null;

    signal read_wantchdog : unsigned(7 downto 0) := (others => '0');
    
    procedure pull(signal self : inout csv_writer_t) is 

    begin
        self.old_valid <= self.valid;
        self.reopen_file <= '0';
        self.valid <= '0';
        self.done <= '0';

        if self.state = s_closing then 
            self.state <= s_idle;
        end if;

        if self.state = s_open and  self.old_valid = '1' and self.valid = '0' then 
            self.done <= '1';
            self.state <= s_closing;
        end if;

    end procedure;

    procedure write_to_file(signal self : inout csv_writer_t) is
    begin 
        self.valid <= '1';
    end procedure;

begin


    process (clk) is

    begin
        if rising_edge(clk) then
            request_index.reopen_file <= '0';
            
    
            request_data.reopen_file <= '0';
            response_index.reopen_file <= '0';
            response_index.valid <= '0';
            response_index.done <= '0';
            response_data.valid  <= '0';
            response_data.done <= '0';
            response_data.reopen_file <= '0';
            read_wantchdog <= read_wantchdog + 1;
            

            case i_state is 
            when s_idle => 
                read_wantchdog <= (others =>'0');
                if request_index.valid = '0' then 
                    request_index.reopen_file  <= '1';
                end if;
                if  request_index_rows(0) = -1 then 
                    assert false report "Test: OK" severity failure;
                elsif  request_index_rows(0) = -2 then 
                    response_data.reopen_file <= '1';
                    response_index.reopen_file <= '1';
                    i_state <= s_write_poll;
                elsif  request_index_rows(0) > last_index then 
                    last_index <= request_index_rows(0);
                    response_data.reopen_file <= '1';
                    request_data.reopen_file <= '1';
                    response_index.reopen_file <= '1';
                    i_state <= s_read;
                end if;
            when s_read => 
                if read_wantchdog >50 then 
                    i_state <= s_write;
                    read_wantchdog <= (others =>'0');
                end if;

                if  write_Rows_valid = '1' then 
                    i_state <= s_write;
                    read_wantchdog <= (others =>'0');
                end if;
            when s_write => 
                if write_Rows_valid = '0' then 
                    response_data.done <= '1';
                    i_state <= s_write_poll;
                end if;
            when s_write_poll => 
               response_index.valid  <= '1';
                response_index_rows(0) <= last_index;
                i_state <= s_done ;

            when s_done =>
            
                response_index.done <= '1';
                i_state <= s_idle;
                
            when s_reset => 
                last_index <= 0;
                response_data.valid <= '1';
                i_state <= s_write_poll;
            end case;
            




        end if;

    end process;



    u_request_index  : entity work.csv_read_file
        generic map(
            FileName => request_index_filename,
            NUM_COL => NUM_COL_index,
            HeaderLines => 0
            ) port map (
            clk => clk,
            Rows =>  request_index_rows,
            reopen_file => request_index.reopen_file,
            open_on_startup => request_index.open_on_startup,

            Index => request_index.Index,
            valid => request_index.valid
        );

    u_request_data : entity work.csv_read_file
        generic map(
            FileName => request_data_filename,
            NUM_COL => read_NUM_COL,
            HeaderLines => 1
            ) port map (
            clk => clk,
            Rows => read_Rows,
            reopen_file => request_data.reopen_file,
            open_on_startup => request_data.open_on_startup,
            Index => request_data.Index,
            valid => request_data.valid
        );
    read_Rows_valid <=  request_data.valid;

    i_write_Rows_valid  <= response_data.valid or  write_Rows_valid;
u_response_data  : entity work.csv_write_file
    generic map(
            FileName => response_data_filename,
            NUM_COL => write_NUM_COL,
            HeaderLines =>  HeaderLines
        ) port map (
            clk => clk,
            reopen_file => response_data.reopen_file,
            Rows => write_Rows,
            valid => i_write_Rows_valid,
            done => response_data.done

    );

u_response_index : entity work.csv_write_file
    generic map(
            FileName => response_index_filename,
            NUM_COL => NUM_COL_index,
            HeaderLines =>  HeaderLines
        ) port map (
            clk => clk,
            reopen_file => response_index.reopen_file,
            Rows => response_index_rows,
            valid => response_index.valid,
            done => response_index.done

    );

end architecture;





""".format(
    text_io_query = constants.text_IO_polling,
    send_lock     = "/"+ constants.text_io_polling_send_lock_txt,
    send          = "/"+ constants.text_io_polling_send_txt,
    receive       = "/"+ constants.text_io_polling_receive_txt, 
    receive_lock  = "/"+ constants.text_io_polling_receive_lock_txt 
)