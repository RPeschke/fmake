import fmake

import inspect
f = open("dummy.txt" , "w")
def write(txt):
    f.write( str(txt) + "\n")

def autocompletionPS(argv):
    fragment = None

    write(str(argv))
    if not (len(argv) >= 3  and  argv[1] == "--autocompletePS"):
        return False

    if len(argv) == 5:
        fragment = argv[4]

    sp = []
    r = argv[3]# [int(argv[2]):]
    if len(r)>0:
        sp = r.split(" ")[1:]

    if fragment is not None:
        sp = [x for x in sp if fragment != x]
    write("'" + str(fragment) + " " + str(sp) + "'")
    autocompletion(fragment, sp)
    return True 


def handle_program_selection(fragment, arglist):
    if len(arglist) != 0:
        return False

    write("len(arglist) == 0")
    list_of_programs = fmake.get_list_of_user_programs()
    matches  = list_of_programs
    if fragment is not None:
        write("fragment is not None")
        matches = [
            x for x in matches
            if x["type"] == "program"
            and (x["program_name"]).lower().startswith(fragment.lower())
        ]
    for match in matches:
        print(match["program_name"])
        write(match["program_name"])
    return True

def autocompletion(fragment, arglist):
    write("autocompletion")
    write(str(fragment) + " " +str(arglist))
    if handle_program_selection(fragment, arglist):
        return

    if fragment is not None and  not fragment.startswith("-"):
        print( "__FMAKE_DEFAULT__")
        write( "__FMAKE_DEFAULT__")
        return 
    
    program_name = arglist[0]
    try:
        write( "load program " +  program_name)
        fun  = fmake.get_program(program_name, keyword="program")
    except:
        print("__ERROR__ unknown program", program_name)
        write( "__ERROR__ unknown program: " +  program_name)
        return
    sig = inspect.signature(fun)
    arguments = ["--"  + sig.parameters[x].name for x in sig.parameters.keys()]
    arguments = [x for x in arguments if x not in arglist]
    if fragment:
        arguments = [x for x in arguments if x.startswith(fragment)]
    for argument in arguments:
        print(argument)