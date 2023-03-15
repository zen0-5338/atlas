from argparse import ArgumentParser
import os
from json import load

argparser = ArgumentParser()

TEMPLATE_FILE_PATH = './courses/template.json'
COURSE_CONTENT_PATH = './courses/{}.txt'
SAVE_PATH = './courses/new_{}.md'
ENCODING = 'utf-8'
COURSE = 'ecpc30'

def parse_course_text(content : list[str]) -> dict:
   return dict()

def dict_to_md(content_dict : dict) -> str:
    content = "---\n"
    content += f'code: {content_dict["code"].upper()}\n'
    content += f'title: {content_dict["title"].title()}\n'
    content += f'similar: {[value.upper() for value in content_dict["similar"]]}\n\n'

    content += 'specifics:\n'
    for branch in content_dict["specifics"].keys():
        if content_dict['specifics'][branch]['credits']:
            content+=f'\t- branch: {branch.upper()}\n\tsemester: {content_dict["specifics"][branch]["semester"]}\n\tcredits: {content_dict["specifics"][branch]["credits"]}\n\n'
    
    content += f'prereq: {content_dict["prereq"]}\n'
    content += f'kind: {content_dict["kind"]}\n'
    content += '---\n\n'
    return content

def flatten(arr : list):
    ret = []
    if isinstance(arr,list):
        for i in arr:
            ret.extend(flatten(i))
    else:
        ret.append(arr)
    return ret

with open(TEMPLATE_FILE_PATH,encoding=ENCODING) as template, open(COURSE_CONTENT_PATH.format(COURSE),encoding=ENCODING) as content:
    # load the json template
    template = load(template)
    # read course content file
    content = content.readlines()
    content = [line for line in content if line != '\n']

    # loop over lines - I know this is not optimal but who cares, it's python
    for line_index in range(len(content)):
        line = content[line_index].lower() # You will see soon why I chose index insteacad of foreach

        # --- Course Code ---
        if line.startswith('course code'):
            template['code'] = line.split(':')[1].strip()
        # --- Course Title ---
        elif line.startswith('course title'):
            template['title'] = line.split(':')[1].strip()
        # --- Course Type ---
        elif line.startswith('course type'):
            template['kind'] = line.split(':')[1].strip()
        # --- Course Credits and Semester ---
        elif line[:2] in list(template['specifics'].keys()):
            credits = line.split(line[:2])[1].split()
            if all([i.isdigit() for i in credits]):
                template['specifics'][line[:2]]['credits'] = credits
        # for branch in template['specifics'].keys():
        #    if line.startswith(branch):
        #       credits = line.split(branch)[1].split()
        #       if all([i.isdigit() for i in credits]):
        #          template['specifics']['branch']['credits'] = credits
        #       else:
        #          break

with open(SAVE_PATH.format(COURSE.upper()),'w',encoding=ENCODING) as f:
    f.write(dict_to_md(template))