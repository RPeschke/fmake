

ret=[]


def add_program(name, function):
    ret.append({"name": name, "func": function})
    
def get_function(name):
    for x in ret:
        if x["name"] == name:
            return x["func"]
    return None

def get_list_of_programms():
    r = []
    for x in ret:
        r.append(x["name"])
    r.sort() 
    return r
    
def print_list_of_programs(printer):
    for x in get_list_of_programms():
        printer(x)