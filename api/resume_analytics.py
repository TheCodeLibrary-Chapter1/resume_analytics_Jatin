#!/usr/bin/env python
# coding: utf-8

# In[1]:


from resume_parser import parse_resume
from data_parser import base_path
import os


# #### Unit Testing

# In[2]:

print("IN")

path = os.path.join(base_path,"TestResume","Big Data","AbhijeetShivajiMolavade-Data Eng -Associate.pdf")
out = parse_resume(path,job_desc_name='Big Data',job_desc_id=1,
                   comp_id=10,created_by='ABC',profile_loc='Delhi')
out

print("OUT")

# In[ ]:
