import pandas as pd
import os.path
from time import sleep


from fmake.generic_helper import constants
from fmake.generic_helper import verbose_printer_cl 
from fmake.generic_helper import get_build_directory

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
    def __init__(self, path , columns=None):
        self.columns = columns
        self.path = path

        if not os.path.exists(path):
            os.mkdir(path)

        self.send_lock_FileName     = path + "/"+ constants.text_io_polling_send_lock_txt 
        self.send_FileName          = path + "/"+ constants.text_io_polling_send_txt 
        self.receive_FileName       = path + "/"+ constants.text_io_polling_receive_txt 
        self.receive_lock_FileName  = path + "/"+ constants.text_io_polling_receive_lock_txt 

        vprint(10)("self.columns:               ", self.columns)
        vprint(10)("self.FileName:              ", self.path)
        vprint(10)("self.send_lock_FileName:    ", self.send_lock_FileName)
        vprint(10)("self.send_FileName:         ", self.send_FileName)
        vprint(10)("self.receive_FileName:      ", self.receive_FileName)
        vprint(10)("self.receive_lock_FileName: ", self.receive_lock_FileName)
        try:
            index =int( get_content(self.send_lock_FileName))
        except:
            index = 0
            vprint(10)("vhdl_file_io.__init__: except")
            vprint(10)(self.send_lock_FileName)
            set_content(self.send_lock_FileName, 0)
            set_content(self.send_FileName, 0)
            set_content(self.receive_lock_FileName, "time, id\n 0 , 0")
            set_content(self.receive_FileName, "time, id\n 0 , 0")
            
    def set_verbosity(self, level):
        vprint.level = level
        
    def read_poll(self):
        try:
            txt = get_content(self.receive_lock_FileName)
            return int(txt.split("\n")[1].split(",")[1])
        except:
            vprint(11)("read_poll:" , txt)

    def reset(self):
        set_content(self.send_lock_FileName, 0)
        set_content(self.send_FileName, 0)
        set_content(self.receive_lock_FileName, "time, id\n 0 , 0")
        set_content(self.receive_FileName, "time, id\n 0 , 0")
        
        set_content(self.send_lock_FileName, -2)
        sleep(1)     
        set_content(self.send_lock_FileName, 0)
        sleep(1)  
        
        
    def wait_for_index(self ,index ):
        for i in range(10000):
            try:
                if i == 10000-1:
                    sleep(0.1)

                ret = self.read_poll()
                if ret  ==  index:
                    return True

            except: 
                pass
        vprint(10)("wait_for_index: Expected index:", index, " received index:", ret)
        return False
    
    def write_file(self, df):
        if self.columns is not None:
            df[self.columns ].to_csv(self.send_FileName, sep = " ", index = False)
        else :
            df.to_csv(self.send_FileName, sep = " ", index = False)
            
    def stop(self):
        set_content(self.send_lock_FileName, -1 )  
        sleep(1)      
        set_content(self.send_lock_FileName, 0 )  
        
        
    def query(self , df):
        df = to_dataframe(df)
        index = self.read_poll() 
        error_detected = False
        for i in range(10):
            index += 1
            self.write_file(df)
            set_content(self.send_lock_FileName, index )
            if error_detected:
                vprint(10)("query: retry Index Expected: ", index ," try: " , i)
        
            if self.wait_for_index(index):
                error_detected = False
                break
                
            vprint(10)("query: error: Index read: ", self.read_poll() , " 	Index Expected: ", index ," try: " , i)
            error_detected = True
    
        if error_detected:
            vprint(0)("query: error: Index read: ", self.read_poll() , " 	Index Expected: ", index)

        return self.read_file()
    
        
    def read_file(self):
        
        df = pd.read_csv(self.receive_FileName)
        df.columns = df.columns.str.replace(' ', '')
        return df
    


def text_io_query(entity, prefix = None,  columns=None, build = None ):
    prefix = constants.text_IO_polling if prefix is None else prefix
    build =  build if build  else get_build_directory()
    path = build + "/" +  entity + "/" + prefix
    return vhdl_file_io(path, columns)