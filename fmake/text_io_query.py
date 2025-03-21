import pandas as pd
import os.path
from time import sleep


from fmake.generic_helper import constants
from fmake.generic_helper import verbose_printer_cl 
from fmake.generic_helper import get_build_directory
from io import StringIO
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
        self.wait_time = 10
        self.last_send_index  = 0

        if not os.path.exists(path):
            os.mkdir(path)

        self.send_lock_FileName     = path + "/"+ constants.text_io_polling_send_lock_txt 
        self.send_FileName          = path + "/"+ constants.text_io_polling_send_txt 
        self.receive_FileName       = path + "/"+ constants.text_io_polling_receive_txt 
        self.receive_lock_FileName  = path + "/"+ constants.text_io_polling_receive_lock_txt 

        vprint(20)("self.columns:               ", self.columns)
        vprint(20)("self.FileName:              ", self.path)
        vprint(20)("self.send_lock_FileName:    ", self.send_lock_FileName)
        vprint(20)("self.send_FileName:         ", self.send_FileName)
        vprint(20)("self.receive_FileName:      ", self.receive_FileName)
        vprint(20)("self.receive_lock_FileName: ", self.receive_lock_FileName)
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
            for _  in range(10):
                txt = get_content(self.receive_lock_FileName)
                if len(txt)> 5:
                    return int(txt.split("\n")[1].split(",")[1])
                sleep(0.1)
            
        except:
            vprint(21)("read_poll:" , txt)
        return -1

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
        size_new = 1
        size_old = 0
        ret = -5
        current_index = 0
        tries = 0
        while True:
            size_old = size_new
            size_new = os.path.getsize(self.receive_FileName) 

            if size_new > 10 and size_new == size_old:
                tries += 1 
                size_old = 0
                sleep(0.1)
                vprint(40)("wait_for_index: Expected index: "+  str(index) + " received index: "+str( current_index))
            
            if tries > self.wait_time:
                vprint(40)("wait_for_index: tried NTimes; Expected index: "+  str(index) + " received index: "+str( current_index))
                return False
            

            
            try:
                current_index = self.read_poll()
                if current_index  ==  index:
                    vprint(50)("wait_for_index: return True; Expected index: "+  str(index) + " received index: "+str( current_index))
                    return True

            except: 
                pass




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
        try:
            index = self.read_poll() 
            self.last_send_index = index
        except:
            vprint(10)("query: error: unable to read last index")
            
        error_detected = False
        for i in range(10):
            self.last_send_index += 1
            self.write_file(df)
            set_content(self.send_lock_FileName,  self.last_send_index )
            if error_detected:
                vprint(10)("query: retry Index Expected: ",  self.last_send_index ," try: " , i)
        
            if self.wait_for_index( self.last_send_index ):
                
                error_detected = False
                break
                
            vprint(10)("query: error: Index read: ", self.read_poll() , " 	Index Expected: ",  self.last_send_index ," try: " , i)
            error_detected = True
    
        if error_detected:
            vprint(0)("query: error: Index read: ", self.read_poll() , " 	Index Expected: ",  self.last_send_index)

        return self.read_file()
    
        
    def read_file(self):
        
        for i in range(100):
            if i > 50:
                sleep(0.1)
            try:
                content = get_content(self.receive_FileName)
                if len(content) < 10:
                    continue
                csv_data = StringIO(content)
                df = pd.read_csv(csv_data)
                df.columns = df.columns.str.replace(' ', '')
                return df
            except:
                vprint(10)("read_file: error: unable to read: receive_FileName: ", self.receive_FileName )
        print("read_file: error: unable to read after N tries: receive_FileName:  ", self.receive_FileName )


    


def text_io_query(entity, prefix = None,  columns=None, build = None ):
    prefix = constants.text_IO_polling if prefix is None else prefix
    build =  build if build  else get_build_directory()
    path = build + "/" +  entity + "/" + prefix
    return vhdl_file_io(path, columns)