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

class Scope:
    def __init__(self):
        self._globals = {}
        self._locals = {}
        userProgramsn = get_fmake_user_programs()
        for p in userProgramsn:
            self._locals[p[2]] = lambda  *args, **kwargs: get_program(Name= p[2], file = p[0])(*args, **kwargs)

    def run(self, code: str):
        self._locals["disp"] = printer()
        exec(code, self._globals, self._locals)
        
    
    def disp(self, code: str):
        self._locals["disp"] = printer()
        exec("disp(" + code + ")", self._globals, self._locals)
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
def handle_run(tag, value, scope):
    if tag!="call":
        return None

    scope.run(value)
    return ""


@mdpy_processor
def handle_disp(tag, value, scope):
    if tag!="disp":
        return None

    return scope.disp(value)

@mdpy_processor
def handle_fdisp(tag, value, scope):
    if tag!="fdisp":
        return None

    return scope.disp(value)

def handle_XML_section(tag, newscope):
    ret4 = ""
    for k in tag["attributes"]:
        for p  in reversed(mdPyEx_processors):
            r = p(k, tag["attributes"][k] , newscope)
            if r is not None:
                ret4 += str(r)
                break
    
    return ret4


def update_content(content):

    ret1 = find_custom_mdpyex_tags(content)
    

    ret2 = extract_mdpyex_tags_with_positions(content)
    

    ret1.extend(ret2)
    ret3 = clean_nested_tags(ret1)
    md_config["tags"] = ret3

    newscope = Scope()
    newscope._locals["test"] = lambda : "lambda test"

    newscope._locals["include"] = lambda x: f'<img src={x}  alt="Description of image">'
    newscope._locals["include1"] = lambda x: f'\n![fig]({x})'
    len_content = len(content)

    offset = 0
    for x in ret3:
        try:
            where = x.get('start', '?')
            full_tag = x.get('full_tag', '?')
            line = content[where:].split('\n')[0]
            lineNR = len(content[:where].split('\n'))
            md_config["lineNR"] = lineNR
            newscope._locals["__md_config__"] = md_config
            ret4 = handle_XML_section(x, newscope)
        except Exception as e:
            where = x.get('start', '?')
            full_tag = x.get('full_tag', '?')
            line = content[where:].split('\n')[0]
            lineNR = len(content[:where].split('\n'))
            raise Exception(f"Error at: {lineNR}\n{line}")
        finally:
            md_config["lineNR"] = None


        if len(ret4) == 0:
            continue
        
        new_content = "<" + x["full_tag"] + " "

        for k in x["attributes"]:
            new_content += k+'="' + x["attributes"][k] + '" '
        ret4 =  update_subcontent(ret4)
        new_content += "/>\n" + ret4 + "\n<" + x["full_tag"] + ' end="true"/>'

        

        content= content[:x['start']+offset] + new_content + content[offset + x["end"]:] 
        
        offset = len(content) - len_content
    
    return content

def update_file(fileName):
    
    try:
        md_config["filename"] = fileName
        md_config["abs_path"] = os.path.abspath(fileName)
        content = load_file(fileName)
        md_config["content"] = content
        content1 = update_content(content)
        if content != content1:
            save_file(content=content1, filename=fileName)
    except Exception as e:
        print("Error in File:", fileName)
        print(e)
    finally:
        md_config["filename"] = None
        md_config["content"] =  None
        md_config["tags"] = None
        md_config["abs_path"] =None


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