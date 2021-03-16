from __future__ import division

import re
import os
from datetime import date

import docx2txt
import pandas as pd
from tika import parser
import phonenumbers
import pdfplumber

import logging

import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher

import sys
import operator
import string
import nltk
from stemming.porter2 import stem
import en_core_web_sm

# load pre-trained model
base_path = os.path.dirname(__file__)


# nlp = spacy.load('en_core_web_sm')
nlp = en_core_web_sm.load()
custom_nlp2 = spacy.load(os.path.join(base_path,"data_files","degree","model"))

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

file = os.path.join(base_path,"data_files","titles_combined.txt")
file = open(file, "r", encoding='utf-8')
designation = [line.strip().lower() for line in file]
designitionmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in designation if len(nlp.make_doc(text)) < 10]
designitionmatcher.add("Job title", None, *patterns)

file = os.path.join(base_path,"data_files","SKILLS.txt")
file = open(file, "r", encoding='utf-8')    
skill = [line.strip().lower() for line in file]
skillsmatcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(text) for text in skill if len(nlp.make_doc(text)) < 10]

skillsmatcher.add("Job title", None, *patterns)


class resumeparse(object):

    objective = (
        'career goal',
        'objective',
        'career objective',
        'employment objective',
        'professional objective',
        'summary',
        'career summary',
        'professional summary',
        'summary of qualifications',
        # 'digital'
    )

    work_and_employment = (
        'employment history',
        'work history',
        'work experience',
        'experience',
        'professional experience',
        'professional background',
        'additional experience',
        'career related experience',
        'related experience',
        'programming experience',
        'freelance',
        'freelance experience',
        'army experience',
        'military experience',
        'military background',
    )

    education_and_training = (
        'academic background',
        'academic experience',
        'programs',
        'courses',
        'related courses',
        'education',
        'educational background',
        'educational qualifications',
        'educational training',
        'education and training',
        'training',
        'academic training',
        'professional training',
        'course project experience',
        'related course projects',
        'internship experience',
        'internships',
        'apprenticeships',
        'college activities',
        'certifications',
        'special training',
    )

    skills_header = (
        'credentials',
        'qualifications',
        'areas of experience',
        'areas of expertise',
        'areas of knowledge',
        'skills',
        'skill set',
        'work experience',
        'technology skillset',
        'technology skills',
        'professional experience',
        "other skills",
        "other abilities",
        'career related skills',
        'professional skills',
        'specialized skills',
        'technical skills',
        'computer skills',
        'personal skills',
        'computer knowledge',        
        'technologies',
        'technical experience',
        'proficiencies',
        'languages',
        'language competencies and skills',
        'programming languages',
        'competencies',
        'software proficiency',
        'responsibilities'
    )

    misc = (
        'activities and honors',
        'activities',
        'affiliations',
        'professional affiliations',
        'associations',
        'professional associations',
        'memberships',
        'professional memberships',
        'athletic involvement',
        'community involvement',
        'refere',
        'civic activities',
        'extra-Curricular activities',
        'professional activities',
        'volunteer work',
        'volunteer experience',
        'additional information',
        'interests'
    )

    accomplishments = (
        'achievement',
        'licenses',
        'presentations',
        'conference presentations',
        'conventions',
        'dissertations',
        'exhibits',
        'papers',
        'publications',
        'professional publications',
        'research',
        'research grants',
        'project',
        'research projects',
        'personal projects',
        'current research interests',
        'thesis',
        'theses',
    )

                   
    def find_segment_indices(string_to_search, resume_segments, resume_indices):
        for i, line in enumerate(string_to_search):

            if line[0].islower():
                continue

            header = line.lower()

            if [o for o in resumeparse.objective if header.startswith(o)]:
                try:
                    resume_segments['objective'][header]
                except:
                    resume_indices.append(i)
                    header = [o for o in resumeparse.objective if header.startswith(o)][0]
                    resume_segments['objective'][header] = i
            elif [w for w in resumeparse.work_and_employment if header.startswith(w)]:
                try:
                    resume_segments['work_and_employment'][header]
                except:
                    resume_indices.append(i)
                    header = [w for w in resumeparse.work_and_employment if header.startswith(w)][0]
                    resume_segments['work_and_employment'][header] = i
            elif [e for e in resumeparse.education_and_training if header.startswith(e)]:
                try:
                    resume_segments['education_and_training'][header]
                except:
                    resume_indices.append(i)
                    header = [e for e in resumeparse.education_and_training if header.startswith(e)][0]
                    resume_segments['education_and_training'][header] = i
            elif [s for s in resumeparse.skills_header if header.startswith(s)]:
                try:
                    resume_segments['skills'][header]
                except:
                    resume_indices.append(i)
                    header = [s for s in resumeparse.skills_header if header.startswith(s)][0]
                    resume_segments['skills'][header] = i
            elif [m for m in resumeparse.misc if header.startswith(m)]:
                try:
                    resume_segments['misc'][header]
                except:
                    resume_indices.append(i)
                    header = [m for m in resumeparse.misc if header.startswith(m)][0]
                    resume_segments['misc'][header] = i
            elif [a for a in resumeparse.accomplishments if header.startswith(a)]:
                try:
                    resume_segments['accomplishments'][header]
                except:
                    resume_indices.append(i)
                    header = [a for a in resumeparse.accomplishments if header.startswith(a)][0]
                    resume_segments['accomplishments'][header] = i

    def slice_segments(string_to_search, resume_segments, resume_indices):
        resume_segments['contact_info'] = string_to_search[:resume_indices[0]]

        for section, value in resume_segments.items():
            if section == 'contact_info':
                continue

            for sub_section, start_idx in value.items():
                end_idx = len(string_to_search)
                if (resume_indices.index(start_idx) + 1) != len(resume_indices):
                    end_idx = resume_indices[resume_indices.index(start_idx) + 1]

                resume_segments[section][sub_section] = string_to_search[start_idx:end_idx]

    def segment(string_to_search):
        resume_segments = {
            'objective': {},
            'work_and_employment': {},
            'education_and_training': {},
            'skills': {},
            'accomplishments': {},
            'misc': {}
        }

        resume_indices = []

        resumeparse.find_segment_indices(string_to_search, resume_segments, resume_indices)
        if len(resume_indices) != 0:
            resumeparse.slice_segments(string_to_search, resume_segments, resume_indices)
        else:
            resume_segments['contact_info'] = []

        return resume_segments

    def calculate_experience(resume_text):

        def correct_year(result):
            if len(result) < 2:
                if int(result) > int(str(date.today().year)[-2:]):
                    result = str(int(str(date.today().year)[:-2]) - 1) + result
                else:
                    result = str(date.today().year)[:-2] + result
            return result

        # try:
        experience = 0
        start_month = -1
        start_year = -1
        end_month = -1
        end_year = -1

        not_alpha_numeric = r'[^a-zA-Z\d]'
        number = r'(\d{2})'

        months_num = r'(01)|(02)|(03)|(04)|(05)|(06)|(07)|(08)|(09)|(10)|(11)|(12)'
        months_short = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
        months_long = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
        month = r'(' + months_num + r'|' + months_short + r'|' + months_long + r')'
        regex_year = r'((20|19)(\d{2})|(\d{2}))'
        year = regex_year
        start_date = month + not_alpha_numeric + r"?" + year
        

        end_date = r'((' + number + r'?' + not_alpha_numeric + r"?" + month + not_alpha_numeric + r"?" + year + r')|(present|current))'
        longer_year = r"((20|19)(\d{2}))"
        year_range = longer_year + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + r'(' + longer_year + r'|(present|current))'
        date_range = r"(" + start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))" + end_date + r")|(" + year_range + r")"

        
        regular_expression = re.compile(date_range, re.IGNORECASE)
        
        regex_result = re.search(regular_expression, resume_text)
        
        while regex_result:

            date_range = regex_result.group()
            try:
                year_range_find = re.compile(year_range, re.IGNORECASE)
                year_range_find = re.search(year_range_find, date_range)
                replace = re.compile(r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
                replace = re.search(replace, year_range_find.group().strip())

                start_year_result, end_year_result = year_range_find.group().strip().split(replace.group())
                start_year_result = int(correct_year(start_year_result))
                if end_year_result.lower().find('present') != -1 or end_year_result.lower().find('current') != -1:
                    end_month = date.today().month  # current month
                    end_year_result = date.today().year  # current year
                else:
                    end_year_result = int(correct_year(end_year_result))


            except:

                start_date_find = re.compile(start_date, re.IGNORECASE)
                start_date_find = re.search(start_date_find, date_range)

                non_alpha = re.compile(not_alpha_numeric, re.IGNORECASE)
                non_alpha_find = re.search(non_alpha, start_date_find.group().strip())

                replace = re.compile(start_date + r"(" + not_alpha_numeric + r"{1,4}|(\s*to\s*))", re.IGNORECASE)
                replace = re.search(replace, date_range)
                date_range = date_range[replace.end():]

                start_year_result = start_date_find.group().strip().split(non_alpha_find.group())[-1]

               
                start_year_result = int(correct_year(start_year_result))

                if date_range.lower().find('present') != -1 or date_range.lower().find('current') != -1:
                    end_month = date.today().month  # current month
                    end_year_result = date.today().year  # current year
                else:
                    end_date_find = re.compile(end_date, re.IGNORECASE)
                    end_date_find = re.search(end_date_find, date_range)

                    end_year_result = end_date_find.group().strip().split(non_alpha_find.group())[-1]

                    end_year_result = int(correct_year(end_year_result))

            if (start_year == -1) or (start_year_result <= start_year):
                start_year = start_year_result
            if (end_year == -1) or (end_year_result >= end_year):
                end_year = end_year_result

            resume_text = resume_text[regex_result.end():].strip()
            regex_result = re.search(regular_expression, resume_text)
        
        return end_year - start_year  # Use the obtained month attribute


    def get_experience(resume_segments):
        total_exp = 0
        if len(resume_segments['objective'].keys()):
            text = ""
            for key, values in resume_segments['objective'].items():
                text += " ".join(values) + " "
            rx = re.compile(r"(\d+(?:-\d+)?\+?)\s*(years?)", re.I)
            op = rx.search(text)

            
            if op!=None:
                final_exp = [float(i) for i in op.groups() if i.isnumeric()]
                if len(final_exp) > 0:
                    total_exp_objective = max(final_exp)
                else:
                    total_exp_objective = 'Could not be calculated'
                
            else:
                total_exp_objective = 'Could not be calculated'
                    
        if len(resume_segments['work_and_employment'].keys()):
            text = ""
            for key, values in resume_segments['work_and_employment'].items():
                text += " ".join(values) + " "
            total_exp = resumeparse.calculate_experience(text)
            return total_exp, text,total_exp_objective
        else:
            text = ""
            for key in resume_segments.keys():
                if key != 'education_and_training':
                    if key == 'contact_info':
                        text += " ".join(resume_segments[key]) + " "
                    else:
                        for key_inner, value in resume_segments[key].items():
                            text += " ".join(value) + " "
            total_exp = resumeparse.calculate_experience(text)
            return total_exp, text,total_exp_objective
        return total_exp, " ",total_exp_objective

    def find_phone(text):
        try:
            return list(iter(phonenumbers.PhoneNumberMatcher(text, None)))[0].raw_string
        except:
            try:
                return re.search(
                    r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
                    text).group()
            except:
                return ""

    def extract_email(text):
        email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
        if email:
            try:
                return email[0].split()[0].strip(';')
            except IndexError:
                return None

    def extract_name(resume_text):
        nlp_text = nlp(resume_text)

        # First name and Last name are always Proper Nouns
     
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        matcher.add('NAME', None, pattern)

        matches = matcher(nlp_text)
        
        for match_id, start, end in matches:
            span = nlp_text[start:end]
            if str(span) != 'CURRICULUM VITAE':
                return span.text
        return ""

    def extract_university(text, file):
        df = pd.read_csv(file, header=None)
        universities = [i.lower() for i in df[1]]
        college_name = []
        listex = universities
        listsearch = [text.lower()]

        for i in range(len(listex)):
            for ii in range(len(listsearch)):
                
                if re.findall(listex[i], re.sub(' +', ' ', listsearch[ii])):
                
                    college_name.append(listex[i])
        
        return college_name

    def job_designition(text):
        job_titles = []
        
        __nlp = nlp(text.lower())
        
        matches = designitionmatcher(__nlp)
        for match_id, start, end in matches:
            span = __nlp[start:end]
            job_titles.append(span.text)
        return job_titles

    def get_degree(text):
        doc = custom_nlp2(text)
        degree = []

        degree = [ent.text.replace("\n", " ") for ent in list(doc.ents) if ent.label_ == 'Degree']
        return list(dict.fromkeys(degree).keys())
    
    def extract_skills(text):

        skills = {}

        __nlp = nlp(text.lower())
        print('here')
        matches = skillsmatcher(__nlp)
        for match_id, start, end in matches:
            rule_id = nlp.vocab.strings[match_id] 
            span = __nlp[start:end]
            skills[rule_id] = span.text

        return skills
    
    def extract_degree(text):
       
        degree=open(os.path.join(base_path,'data_files','education.txt'),'r').read()
        degree=set(degree.split('\n'))
        education = []
        for key in degree:
            lookup_key = r"\b{0}\b".format(key)
            try:
                temp = text[re.search(lookup_key,text).span()[0]:re.search(lookup_key,text).span()[1]]
                education.append(temp)
            except:
                pass
        return education

    
