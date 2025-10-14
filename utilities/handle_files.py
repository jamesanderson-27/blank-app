import streamlit as st
import csv
import json
from typing import Set, Union
from datetime import datetime

####### File Upload Activity #######

def getJsonAttributes(obj: Union[dict, list], prefix: str="") -> Set[str]: ## Chat GPT credit
    attributes = set()
    if isinstance(obj, dict): # dict path
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key # attribute is parent data 
            attributes.add(full_key)
            attributes.update(getJsonAttributes(value, prefix=full_key)) # attribute is child data
    elif isinstance(obj, list): # list path
        for item in obj:
            attributes.update(getJsonAttributes(item, prefix=prefix)) # attribute is a list name

    return attributes

def jsonReader(file):
    attributes = set() # usage of set() elimates possibility of attribute duplicates
    prefix=""
    data = file.read().decode("utf-8") # assumed utf-8 encoding DOCUMENT
    try:
        json_obj = json.loads(data.strip())
        attributes=getJsonAttributes(json_obj)
    except Exception as e:
        st.badge(f"Error reading {str(file.name)}: {e}",color='red')

    return list(attributes)

def csvTxTReader(file):
    raw=file.read().decode('utf-8') # assumed utf-8 encoding DOCUMENT
    content = raw.splitlines()
    dialect = csv.Sniffer().sniff(raw)
    delim=dialect.delimiter # determines delimiter of file using csv library function
    try:
        reader = csv.reader(content, delimiter=delim)
    except Exception as e:
        st.badge(f"Error reading file: {e}",color='red')

    return list(next(reader))

def handleFiles(uploaded_files,data_sources):
    for file in uploaded_files:
        if file.type=='application/vnd.ms-excel' or file.type=='text/plain': # csv or excel
            attributes=csvTxTReader(file)
        if file.type=='application/json': # json
            attributes=jsonReader(file)
        data_sources["files"][str(file.name)]={
            "uploaded_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_type":file.type,
            "attributes":attributes
        }
        
    return data_sources