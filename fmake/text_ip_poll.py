import pandas as pd

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
  
  
class vhdl_file_io:
    def __init__(self, FileName , columns=None):
        self.columns = columns
        self.FileName = FileName
        
        self.poll_FileName = FileName + "_poll.txt"
        self.read_FileName =  FileName + "_read.txt"
        self.write_FileName = FileName + "_write.txt"
        self.write_poll_FileName  = FileName + "_write_poll.txt"
        
        self.index =int( get_content(self.poll_FileName))

    def read_poll(self):
        return int(get_content(self.write_poll_FileName).split("\n")[1].split(",")[1])


    def wait_for_index(self):
        for i in range(10000):
            try:
                if self.read_poll() ==  self.index:
                    return True
            except: 
                pass

        return False
    
    def write_file(self, df):
        if self.columns is not None:
            df[self.columns ].to_csv(self.read_FileName, sep = " ", index = False)
        else :
            df.to_csv(self.read_FileName, sep = " ", index = False)
            
    def stop(self):
        set_content(self.poll_FileName, -1 )        
        
    def poll(self , df):
        self.write_file(df)
        self.index = self.read_poll() + 1   
        set_content(self.poll_FileName, self.index )
        
        if not self.wait_for_index():
            print("error", self.read_poll() ,self.index)
    
        return self.read_file()
    
        
    def read_file(self):
        
        df = pd.read_csv(self.write_FileName)
        df.columns = df.columns.str.replace(' ', '')
        return df