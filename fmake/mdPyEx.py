import re
from xml.etree.ElementTree import fromstring, ParseError
import random

from fmake.vhdl_programm_list import add_program
from fmake.user_program_runner import run_fmake_user_program,parse_args_to_kwargs, get_fmake_user_programs, get_program

md_config = {}

def load_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        return content
    

def save_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)


class printer:
    def __init__(self):
        self.content = ""
    
    def __call__(self, arg):
        if arg is None:
            return 
        self.content += str(arg)
    
    def __str__(self):
        return self.content

class run_fmake_user_program:
    def __init__(self, Name, Filename=None):
        self.Name = Name
        self.Filename = Filename
    
    def __call__(self, *args, **kwargs):
        return get_program(Name= self.Name, file = self.Filename)(*args, **kwargs)


class Scope:
    def __init__(self, exec_path = None):
        self._globals = {}
        self._locals = {}
        self.exec_path = exec_path if exec_path is not None else os.getcwd()
                # Create a namespace object to hold user functions
        class UserNamespace:
            pass

        user = UserNamespace()

        userProgramsn = get_fmake_user_programs()
        for p in userProgramsn:
            func = run_fmake_user_program(Name= p[2], Filename = p[0]) 
            name = p[2]

            setattr(user, name, func)
        
        self._locals["program"] = user

    def run_internal(self, code):
        original_dir = os.getcwd()
        try:
            os.chdir(self.exec_path)
            exec(code, self._globals, self._locals)
        finally:
            os.chdir(original_dir)
    
    def run(self, code: str):
        self._locals["disp"] = printer()
        self.run_internal(code)
        
        
    
    def disp(self, code: str):
        self._locals["disp"] = printer()
        self.run_internal("disp(" + code + ")")
        return str(self._locals["disp"])

    def get(self, varname: str, default=None):
        return self._locals.get(varname, default)

    def vars(self):
        return self._locals.copy()

    def __getitem__(self, key):
        return self._locals[key]

    def __contains__(self, key):
        return key in self._locals
    

def clean_nested_tags(tag_list):
    # Step 1: Sort by start index
    tag_list = sorted(tag_list, key=lambda x: x['start'])

    cleaned = []
    last_end = -1

    for tag in tag_list:
        start, end = tag['start'], tag['end']

        # Fully nested (inside previous tag) → skip
        if start >= last_end:
            cleaned.append(tag)
            last_end = end
        elif end > last_end:
            # Partial overlap → bad format
            raise ValueError(f"Tag starting at {start} overlaps with previous tag ending at {last_end}. Possibly malformed.")
        # else: fully inside another tag → silently skip

    return cleaned


def generate_random_digits(length=10):
    return ''.join(random.choices('0123456789', k=length))



def handle_XML_section(tag, environment):
    ret4 = ""
    environment["tag"] = tag
    for k in tag["attributes"]:
        for p  in reversed(mdPyEx_processors):
            r = p(k, tag["attributes"][k] , environment)
            if r is not None:
                environment["content"] = r
                break
    
    environment["tag"] = None
    return  environment["content"]






def extract_mdpyex_tags_with_positions(content):
  

    pattern = re.compile(r"<mdpyex\s+[^>]*?/>")  # Match self-closing <mdpyex ... />
    results = []


    for match in pattern.finditer(content):
        tag = match.group()
        start = match.start()
        end = match.end()
        try:
            element = fromstring(tag)
            uid  = generate_random_digits()
            full_tag = "mdpyexL0U" + uid
            results.append({
                "full_tag": full_tag,
                "uid": uid,
                "attributes": element.attrib,
                "start": int(start),
                "end": int(end)

            })
        except ParseError:
            print(f"Warning: Could not parse tag: {tag}")

    return results




import re
from html import unescape

import re
import ast





def find_custom_mdpyex_tags(text):

    results = []
    
    # Pattern for opening and closing tags, capturing the full tag name and attributes
    pattern = re.compile(
        r'<(?P<tag>mdpyexL0(U\d+))(?P<attrs>[^>]*)/>'   # Opening tag with attributes
        r'(.*?)'                                        # Content (non-greedy)
        r'<\s*(?P=tag)\s+end\s*=\s*"true"\s*/>',        # Closing tag with flexible spacing
        re.DOTALL
    )
    
    for match in pattern.finditer(text):
        full_tag = match.group("tag")
        uid = match.group(2)
        raw_attrs = match.group("attrs").strip()

        # Parse attributes into a dict
        attr_dict = {}
        attr_matches = re.findall(r'(\w+)\s*=\s*"([^"]*)"', raw_attrs)
        for key, val in attr_matches:
            attr_dict[key] = unescape(val)

        results.append({
            "full_tag": full_tag,
            "uid": uid,
            "attributes": attr_dict,
            "start": int(match.start()),
            "end": int(match.end())

        })

    return results

import numpy as np
def update_subcontent(x):
    for i in np.arange(100, -1, -1):
        x= x.replace("mdpyexL"+(str(int(i))), "mdpyexL"+(str(int(i+1))), )
    return x
    

mdPyEx_processors = []
def mdpy_processor(fun):
    mdPyEx_processors.append(fun)
    return fun

@mdpy_processor
def handle_run(tag, value,environment):
    if tag!="call":
        return None

    environment["scope"].run(value)
    return environment["content"]


@mdpy_processor
def handle_disp(tag, value, environment):
    if tag!="disp":
        return None

    ret4 =  environment["scope"].disp(value)
    content = environment["content"]
    if len(ret4) == 0:
        return content
        
    offset = environment["offset"]
    tag  = environment["tag"]
    new_content = "<" + tag["full_tag"] + " "
    
    for k in tag["attributes"]:
        new_content += k+'="' + tag["attributes"][k] + '" '
    ret4 =  update_subcontent(ret4)
    new_content += "/>\n" + ret4 + "\n<" + tag["full_tag"] + ' end="true"/>'

        

    content= content[:tag['start']+offset] + new_content + content[offset + tag["end"]:] 
    return content


@mdpy_processor
def handle_block(tag, value, environment):
    if tag!="block":
        return None
    
    content = environment["content"]
    offset = environment["offset"]
    start = environment['tag']["start"]
    open_tag = "\n```python\n"
    close_tag = "\n```\n"
    index0 = content.find(open_tag, start+offset)
    index0a = content.find(">", start+offset)
    index1 = content.find(close_tag, start+offset+index0+len(open_tag))
    if abs(index0 - index0a) > 10:
        raise Exception("Did not find open tag")

    code = content[index0 +len(open_tag): index1]
    environment["scope"].run(code)

    
    tag  = environment["tag"]
    new_content = "<" + tag["full_tag"] + " "
    
    for k in tag["attributes"]:
        new_content += k+'="' + tag["attributes"][k] + '" '

    new_content += "/>\n" + open_tag + code + close_tag + "<" + tag["full_tag"] + ' end="true"/>'

    closing_index = max(index1 + len(close_tag)   ,offset + tag["end"]  )
    content= content[:tag['start']+offset] + new_content + content[closing_index:] 
    return content


def update_content(content, exec_path = None):

    ret1 = find_custom_mdpyex_tags(content)
    

    ret2 = extract_mdpyex_tags_with_positions(content)


    

    ret1.extend(ret2)


    ret3 = clean_nested_tags(ret1)
    md_config["tags"] = ret3

    newscope = Scope(exec_path)


    newscope._locals["include"] = lambda path, label=None: f'\n![fig]({x})'
    len_content = len(content)

    offset = 0
    for x in ret3:
        try:
            where = x.get('start', '?')
            full_tag = x.get('full_tag', '?')
            line = content[where:].split('\n')[0]
            lineNR = len(content[:where].split('\n'))
            md_config["lineNR"] = lineNR
            content = handle_XML_section(x, {
                "scope" : newscope,
                "content" : content,
                "offset" :offset
            })
        except Exception as e:
            where = x.get('start', '?')
            full_tag = x.get('full_tag', '?')
            line = content[where:].split('\n')[0]
            lineNR = len(content[:where].split('\n'))
            
            raise Exception(f"Error at: {lineNR}\n{line}\n{e}")
        finally:
            md_config["lineNR"] = None


        offset = len(content) - len_content
    
    return content

def update_file(fileName):
    
    try:
        md_config["filename"]  = fileName
        md_config["fullname"]  = os.path.abspath(fileName)
        md_config["directory"] = os.path.dirname(md_config["fullname"])
        content = load_file(fileName)
        md_config["content"] = content
        content1 = update_content(content, os.path.dirname(md_config["fullname"]))
        if content != content1:
            save_file(content=content1, filename=fileName)
    except Exception as e:
        print("Error in File:", fileName)
        print(e)
    finally:
        md_config["filename"] = None
        md_config["content"] =  None
        md_config["tags"] = None
        md_config["fullname"] =None
        md_config["directory"] = None


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time
import os
from datetime import datetime

last_processed = {}
class MarkdownUpdateHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if the modified file is a Markdown file
        if event.is_directory:
            return
        if not event.src_path.endswith('.md'):
            return
        
        last = last_processed.get(event.src_path)
        if last is not None and (datetime.now() - last).seconds < 1:
            return
        print(f"Markdown file changed: {event.src_path}")
        try:
            update_file(event.src_path)
            last_processed[event.src_path]  =  datetime.now()
            print(f"Processed updated file: {event.src_path}")
        except Exception as e:
            print(f"Error processing file {event.src_path}: {e}")


def markdown_monitor(path):

    event_handler = MarkdownUpdateHandler()
    observer = Observer()

    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Monitoring folder: {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


def markdown_monitor_wrap(x):
        args, kwargs = parse_args_to_kwargs(x[2:])
        markdown_monitor(*args, **kwargs)


add_program("markdown-monitor", markdown_monitor_wrap)   