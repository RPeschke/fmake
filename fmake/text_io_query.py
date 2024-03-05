import pandas as pd
from fmake.generic_helper import constants
from fmake.generic_helper import  verbose_printer_cl
	
from time import sleep

vprint = verbose_printer_cl()

def get_content(filename):
    for _ in range(10000):
        try:
            with open(filename) as f:
                return f.read()
        except: 
            pass
    
    raise Exception("file not found")

def set_content(filename, content):
    for _ in range(10000):
        try:
            with open(filename, "w") as f:
                f.write(str(content))
                return
        except: 
            pass
  
    raise Exception("wile cannot be written")
  
def to_dataframe(x):
    if isinstance(x, pd.DataFrame):
        return x
    else:
        return pd.DataFrame(x)

class vhdl_file_io:
    def __init__(self, FileName , columns=None):
        self.columns = columns
        self.FileName = FileName
        
        self.poll_FileName = FileName + "_poll.txt"
        self.read_FileName =  FileName + "_read.txt"
        self.write_FileName = FileName + "_write.txt"
        self.write_poll_FileName  = FileName + "_write_poll.txt"
        try:
            index =int( get_content(self.poll_FileName))
        except:
            index = 0
            set_content(self.poll_FileName, 0)
            set_content(self.read_FileName, 0)
            set_content(self.write_poll_FileName, "time, id\n 0 , 0")
            set_content(self.write_FileName, "time, id\n 0 , 0")
            
    def set_verbosity(self, level):
        vprint.level = level
        
    def read_poll(self):
        try:
            txt = get_content(self.write_poll_FileName)
            return int(txt.split("\n")[1].split(",")[1])
        except:
            vprint(11)("read_poll:" , txt)

    def reset(self):
        set_content(self.poll_FileName, 0)
        set_content(self.read_FileName, 0)
        set_content(self.write_poll_FileName, "time, id\n 0 , 0")
        set_content(self.write_FileName, "time, id\n 0 , 0")
        
        set_content(self.poll_FileName, -2)
        sleep(1)     
        set_content(self.poll_FileName, 0)
        sleep(1)  
        
        
    def wait_for_index(self ,index ):
        for i in range(10000):
            try:
                ret = self.read_poll()
                if ret  ==  index:
                    return True

            except: 
                pass
        vprint(10)("wait_for_index: Expected index:", index, " received index:", ret)
        return False
    
    def write_file(self, df):
        if self.columns is not None:
            df[self.columns ].to_csv(self.read_FileName, sep = " ", index = False)
        else :
            df.to_csv(self.read_FileName, sep = " ", index = False)
            
    def stop(self):
        set_content(self.poll_FileName, -1 )  
        sleep(1)      
        set_content(self.poll_FileName, 0 )  
        
        
    def query(self , df):
        df = to_dataframe(df)
        
        self.write_file(df)
        index = self.read_poll() + 1   
        set_content(self.poll_FileName, index )
        
        if not self.wait_for_index(index):
            vprint(0)("query: error: Index read: ", self.read_poll() , " 	Index Expected: ", index)
    
        return self.read_file()
    
        
    def read_file(self):
        
        df = pd.read_csv(self.write_FileName)
        df.columns = df.columns.str.replace(' ', '')
        return df
    
    
def text_io_query(entity, prefix = None,  columns=None ):
    prefix = constants.text_IO_polling if prefix is None else prefix
    FileName = "build/" + entity + "/" + prefix
    return vhdl_file_io(FileName, columns)