import re
import os
import docx2txt
from tika import parser
import pdfplumber
from statistics import mode
import logging
import docx


def convert_docx_to_txt(docx_file):
    """
        A utility function to convert a Microsoft docx files to raw text.

    """
    try:
        text = parser.from_file(docx_file, service='text')['content']

    except RuntimeError as e:
        logging.error('Error in tika installation:: ' + str(e))
        logging.error('--------------------------')
        logging.error('Install java for better result ')
        text = docx2txt.process(docx_file)

    except Exception as e:
        logging.error('Error in docx file:: ' + str(e))
        return [], " "
    try:
        clean_text = re.sub(r'\n+', '\n', text)
        clean_text = clean_text.replace("\r", "\n").replace("\t", " ")  # Normalize text blob
        resume_lines = clean_text.splitlines()  # Split text blob into individual lines
        resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if
                        line.strip()]  # Remove empty strings and whitespaces

        return resume_lines, text
    except Exception as e:
        logging.error('Error in docx file:: ' + str(e))
        return [], " "


def convert_pdf_to_txt(pdf_file):
    """
    A utility function to convert a machine-readable PDF to raw text.

    """

    try:
        raw_text = parser.from_file(pdf_file, service='text')['content']


    except RuntimeError as e:
        logging.error('Error in tika installation:: ' + str(e))
        logging.error('--------------------------')
        logging.error('Install java for better result ')
        pdf = pdfplumber.open(pdf_file)
        raw_text = ""
        for page in pdf.pages:
            raw_text += page.extract_text() + "\n"
        pdf.close()
    except Exception as e:
        logging.error('Error in pdf file:: ' + str(e))
        return [], " "
    try:
        full_string = re.sub(r'\n+', '\n', raw_text)
        full_string = full_string.replace("\r", "\n")
        full_string = full_string.replace("\t", " ")

        # Remove awkward LaTeX bullet characters

        full_string = re.sub(r"\uf0b7", " ", full_string)
        full_string = re.sub(r"\(cid:\d{0,2}\)", " ", full_string)
        full_string = re.sub(r'• ', " ", full_string)
        full_string = re.sub(r'● ', " ", full_string)
        # Split text blob into individual lines
        resume_lines = full_string.splitlines(True)

        # Remove empty strings and whitespaces
        resume_lines = [re.sub('\s+', ' ', line.strip()) for line in resume_lines if line.strip()]

        return resume_lines, raw_text
    except Exception as e:
        logging.error('Error in docx file:: ' + str(e))
        return [], " "


def read_file(file):
    file = os.path.join(file)

    if file.endswith('docx') or file.endswith('doc'):
        resume_lines, raw_text = convert_docx_to_txt(file)
    elif file.endswith('pdf'):
        resume_lines, raw_text = convert_pdf_to_txt(file)
    elif file.endswith('txt'):
        with open(file, 'r', encoding='latin') as f:
            resume_lines = f.readlines()
    else:
        resume_lines = None

    return resume_lines