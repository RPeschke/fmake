
fmake_csv_IO_py = """


#@fmake.program
def fmake_csv_IO(prj):
    
    prj.add_sources_sim([

            "ClockGenerator.vhd",
            "csv_register_interface.vhd",
            "CSV_UtilityPkg.vhd",
            "csv_text_io_poll.vhd",
            "e_csv_read_file.vhd",
            "e_csv_write_file.vhd",
            "type_conversions_helper.vhd",
    ])
    
"""