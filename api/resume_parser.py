import os
import configparser
import json
import re
import sys
from api.data_parser import resumeparse, base_path
from api.file_reader import read_file


def parse_resume(file, job_desc_name=' ', job_desc_id=0, created_by=' ', comp_id=0, profile_loc=' '):
    '''This function parses resume.'''
    resume_lines = read_file(file)
    
    # Resume segments
    resume_segments = resumeparse.segment(resume_lines)
                
    full_text = " ".join(resume_lines)
    
    # pulling data from resume
    email = resumeparse.extract_email(full_text)
    phone = resumeparse.find_phone(full_text)
    name = resumeparse.extract_name(" ".join(resume_segments['contact_info']))
    total_exp, text,total_ex_obj = resumeparse.get_experience(resume_segments)
    print(total_ex_obj)
    university = resumeparse.extract_university(full_text, os.path.join(base_path,'data_files','world-universities.csv'))

    designition = resumeparse.job_designition(full_text)
    designition = list(dict.fromkeys(designition).keys())

    degree = resumeparse.get_degree(full_text)
    degree2 = resumeparse.extract_degree(full_text)
    
    skills = ""
    
    # skills
    if len(resume_segments['skills'].keys()):
        for key , values in resume_segments['skills'].items():
            mod_values = [val for val in values if len(val.split()) <10]
            add_skill = re.sub(key, '', ",".join(mod_values), flags=re.IGNORECASE)

            skills +=  add_skill  

        skills = skills.strip().strip(",").split(",")

    if len(skills) == 0:
        skills = resumeparse.extract_skills(full_text)

    skills = list(dict.fromkeys(skills).keys())
    
    # degree
    final_degree = list(set(degree + degree2))
    if str(total_ex_obj) !='Could not be calculated':
        total_exp_final=total_ex_obj
    elif total_exp != None:
        total_exp_final=total_exp
    else: 
        total_exp_final='Could not be calculated'
    
    
    output_json = {'Job Description Name' : job_desc_name,
                   'Job Description ID' : job_desc_id,
                   'Company ID' : comp_id,
                   'Relevancy Match': 'Work in Progress',
                   'Candidate Name' : name,
                   'Candidate Email' : email,
                   'Candidate Phone' : phone,
                   'Candidate Last Location' : 'Work in Progress',
                   'Skills' : skills,
                   'Total Experience' : total_exp_final,
                   'Designation' : designition,
                   'Education' : final_degree
    }
    
    return output_json
