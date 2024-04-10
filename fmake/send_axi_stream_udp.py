import argparse
import os


from fmake.vhdl_programm_list import add_program

from fmake.generic_helper import  vprint, try_remove_file , save_file , load_file 
from fmake.generic_helper import extract_cl_arguments, cl_add_entity , cl_add_OutputCSV, cl_add_gui

from fmake.Convert2CSV import Convert2CSV , Convert2CSV_add_CL_args





import socket
import select
import array
import argparse
import time
import os



  

class SCROD_ethernet:

    def __init__(self,IpAddress,PortNumber):
        self.IpAddress = IpAddress
        self.PortNumber = int(PortNumber)
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def __ToEventNumber(self, Data, Index):
        ret_h = 0
    
        ret_h += (Data[Index])
        ret_h += 0x100*(Data[Index+1])
        ret_h += 0x10000*(Data[Index+2])
        ret_h += 0x1000000*(Data[Index+3])
        return ret_h

    def __ArrayToHex(self,Data):
        ret = list()
        for j in range(0,len(Data),4):
            ret.append(hex(self.__ToEventNumber(Data,j)))
        
        return ret


    
    def send(self,Data):
        message = []
        for x in Data:
            message+=(int(x).to_bytes(4,'little'))


        str1=array.array('B', message).tobytes()

        self.clientSock.sendto(str1, ( self.IpAddress, self.PortNumber))

    def receive(self):
        data, addr = self.clientSock.recvfrom(4096)
        data = self.__ArrayToHex(data)
        return data
    
    
    def hasData(self):
        rdy_read, rdy_write, sock_err = select.select([self.clientSock,], [], [],0.1)
        return len(rdy_read) > 0


def get_index():
    with open("index.txt") as indexFile:
        index = indexFile.readline()
    print ( "'" + index +"'")
    index = int(index)
    with open("index.txt","w") as indexFile:
        indexFile.write(str(index+1))

    return index






def send_udp(args, conf):
    try:
        os.remove(args.OutputCSV)
    except:
        vprint(2) ( "output file not found")

        
    scrod1 = SCROD_ethernet(conf["ip"], conf["port"] )
    scrod1.hasData()
    content_in  = load_file(args.input , lambda x: x.readlines() )
    content_in  

    vprint(2)("send data")

    
    scrod1.send(content_in)
    vprint(3)(content_in )

            
    vprint(2)("receive data")
    i = 0 
    startTime = time.time()
    vprint(2)(startTime)
    content = ""
    
    delimiter = "\n" if conf["Send_by_rows"]  else "; "
    
    while scrod1.hasData():
        data = scrod1.receive()
        line = ""
        start = ""
        for d in data:
            line += start + str(int(d,16)) 
            start = delimiter 
        content+=(line+"\n")
        vprint(3)([i,line])
        i+= 1

    if args.OutputCSV == "":
        vprint(0)(content)
    else:
        save_file(args.OutputCSV,content)
    
    endTime = time.time()
    vprint(2)(endTime, endTime -startTime )
    vprint(2)("number of received packages: ",i)
    vprint(2)("----end udp_run script----")




def load_config(fileName):
    try:
        conf = load_file(fileName)
        conf = conf.lower()
        ip = [x.split("=")[1].strip()  for x in conf.split("\n") if "ip" in x][0].split("#")[0].strip()
        port = int([x.split("=")[1].strip()  for x in conf.split("\n") if "port" in x][0].split("#")[0])
        Send_by_rows= [x.split("=")[1].strip()  for x in conf.split("\n") if "send_by_rows" in x][0] == "true"
        return {
            "ip" : ip,
            "port" : port,
            "Send_by_rows" : Send_by_rows
        }
    except:
        vprint(0)("conf file does not exist. Creating new Conf file at:", fileName )
        
        conf = """
IP = 192.168.1.1 # replace with target ip
PORT = 21 # replace with target port
Send_by_rows = False        
        """
        save_file(fileName, conf )
        return None
    
    
        



def send_udp_wrap(x):
    parser = argparse.ArgumentParser(description='run_ise_wrap')
    cl_add_entity(parser)
    cl_add_OutputCSV(parser)
    parser.add_argument('--input', help='',default="",required=True)
    parser.add_argument('--config', help='',default="")
    parser.add_argument('--rows', dest='send_row_by_row', action='store_const',
                    const=True, default=False,
                    help='')
    args = extract_cl_arguments(parser, x)
    
    args.config = args.config if args.config != "" else "build/"+ args.entity +"/udp_config.txt"
    
    conf = load_config(args.config )
    if conf is None:
        return
    
    send_udp(args, conf)
    
    
    
    
    
    
add_program("send-udp", send_udp_wrap )