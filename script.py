from argparse import ArgumentParser
import os
from json import load

argparser = ArgumentParser()
'''
TODO
flags:
content-path - single file or dir
is-dir - whether content-path is dir
save-dir
branch-specific - whether course branch specific, always true for course folder
'''

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
            content+=f'  - branch: {branch.upper()}\n    semester: {content_dict["specifics"][branch]["semester"]}\n    credits: {content_dict["specifics"][branch]["credits"]}\n\n'

    content += f'prereq: {[i.upper() for i in content_dict["prereq"]]}\n'
    content += f'kind: {content_dict["kind"].upper()}\n'
    content += '---\n\n'
    
    content += '# Objectives\n\n'
    for value in content_dict["objectives"]:
        content += f'- {value}\n'
    
    content += '\n# Content\n\n'
    for (i,unit_content) in enumerate(content_dict["units"]):
        # for (unit,unit_content) in content_dict["units"]:
        content += f'## UNIT {i+1}\n\n'
        for j,(topic,subtopics) in enumerate(unit_content.items()):
            content += f'{j+1}. **{topic}**\n'
            for sub in subtopics:
                content += f'   - {sub}\n'
        content += '\n'
    
    content += '# Reference Books\n\n'
    for ref_book in content_dict['reference books']:
        content += f'- {ref_book}\n'
        
    content += '\n# Outcomes\n\n'
    for outcome in content_dict['outcomes']:
        content += f'- {outcome}\n'
    
    return content

def flatten(arr : list):
    ret = []
    if isinstance(arr,list):
        for i in arr:
            ret.extend(flatten(i))
    else:
        ret.append(arr)
    return ret

unit_ctr = 1
PERIODS = ['.',';',')']
SEPARATORS = [':','-','–']
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
            code = line.split(':')[1].strip()
            template['code'] = code
            # template['kind'] = code[2:4]
            template['semester'] = code[4]
        
        # --- Course Title ---
        elif line.startswith('course title'):
            template['title'] = line.split(':')[1].strip()
        
        # --- Course Type ---
        elif line.startswith('course type'):
            template['kind'] = line.split(':')[1].strip()
        
        # --- Course Credits ---
        elif line[:2] in list(template['specifics'].keys()):
            credits = line.split(line[:2])[1].split()
            if all([i.isdigit() for i in credits]):
                template['specifics'][line[:2]]['credits'] = credits
        
        # --- Prerequisites --- 
        elif line.startswith(':'):
            pre = line.split(':')[1]
            pre = [i.strip() for i in pre.split(',')]
       
        # --- Objectives
        elif line.find('learning objectives') != -1:
            i = line_index+1
            string = ""
            while content[i].lower().find('course content') == -1:
                string += content[i]
                i += 1
            line_index = i - 1
            # strip trailing whitespace if any
            string = string.strip()
            # make it one coherent string
            string = ' '.join(string.splitlines())
            # split objectives by period, doesn't account for period abbreviations like Dr.
            string = [i.strip() for i in string.split('.') if i]
            template['objectives'].extend(string)
        
        # --- Units ---
        elif line.startswith('unit'):
            i = line_index + 1
            string = ""
            while not (content[i].lower().startswith('unit') or content[i].strip().isdigit()):
                string += content[i]
                i += 1
            line_index = i - 1
            # strip trailing whitespace if any
            string = string.strip()
            # make coherent string
            string = [' '.join(string.splitlines())]
            # split topics
            for period in PERIODS:
                string = [i.split(period) for i in string]
                string = flatten(string)
            # strip all elements
            topics = [[i.strip()] for i in string if i]
            # split topics and subtopics
            for separator in SEPARATORS:
                topics = [i[0].split(separator,maxsplit=1) if len(i) == 1 else i for i in topics]
                topics = [flatten(i) for i in topics]
            # strip all elements
            topics = [[sub.strip() for sub in i if bool(sub)] for i in topics]
            '''
            some black magic fuckery - 
            basically it is list[ [topic, subtopics] ] 
            where subtopics is one csv string and can be empty too
            so I have to split the subtopics and strip them too
            so final output is list[ [topic, [subtopics]] ]
            I convert it to dict, which is referenced by a unit number (so I make a dict with a value as dict)
            '''
            # template['units'].append({f'UNIT {unit_ctr}' : dict([(t[0],[s.strip() for s in t[1].split(',')] if len(t) > 1 else []) for t in topics])})
            template['units'].append(dict([(t[0],[s.strip() for s in t[1].split(',')] if len(t) > 1 else []) for t in topics]))
            unit_ctr += 1
            
        # --- Reference books ---
        elif line.find('reference books') != -1:
            i = line_index + 1
            string = ""
            while content[i].lower().find('course outcomes') == -1:
                string += content[i]
                i += 1
            line_index = i - 1
            # strip trailing whitespace if any
            string = string.strip()
            # make coherent string
            string = ' '.join(string.splitlines())
            ref_books = ''
            start = 3
            end = start
            # split through numbers
            for i in range(3,len(string)):
                if string[i].isdigit() and string[i+1] in PERIODS and string[i-1] == ' ':
                    end = i-1
                    ref_books += string[start:end] + "\n"
                    i = i + 3
                    start = i
            ref_books += string[start:]
            template['reference books'].extend(ref_books.splitlines())
            
        # --- Outcomes ---
        elif line.find('course outcomes') != -1:
            string = content[line_index + 2:]
            # make coherent string
            string = ' '.join(string)
            outcomes = ''
            start = 3
            end = start
            # split through numbers
            for i in range(3,len(string)):
                if string[i].isdigit() and string[i+1] in PERIODS and string[i-1] == ' ':
                    end = i-1
                    outcomes += string[start:end] + "\n"
                    i = i + 3
                    start = i
            outcomes += string[start:]
            template['outcomes'].extend(outcomes.splitlines())
            
with open(SAVE_PATH.format(COURSE.upper()),'w',encoding=ENCODING) as f:
    f.write(dict_to_md(template))