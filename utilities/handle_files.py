import csv
import json
import streamlit as st
from typing import Union
from datetime import datetime

def getJsonAttributes(obj: Union[dict, list],prefix=""):
    attributes = set() # set for auto dup checking
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key # record parent nodes
            if isinstance(value, dict) or (isinstance(value, list) and any(isinstance(i, dict) for i in value)): # dict or list of dicts
                attributes.update(getJsonAttributes(value, prefix=full_key)) # self ref for child / grandchild nodes
            else:
                attributes.add(full_key)
    elif isinstance(obj, list): # there won't be any child nodes
        for item in obj:
            attributes.update(getJsonAttributes(item, prefix=prefix))
    return attributes

def jsonReader(file):
    attributes = set() # in case the parsing fails, we load empty attribute list
    data = file.read().decode("utf-8")
    try:
        json_obj = json.loads(data.strip())
        attributes=getJsonAttributes(json_obj)
    except Exception as e:
        st.badge(f"Error reading {str(file.name)}: {e}",color='red')
    return list(attributes)

def csvTxTReader(file):
    raw=file.read().decode('utf-8')
    content = raw.splitlines()
    dialect = csv.Sniffer().sniff(raw)
    delim=dialect.delimiter # should determine delimiter of file
    try:
        reader = csv.reader(content, delimiter=delim)
    except Exception as e:
        st.badge(f"Error reading file: {e}",color='red')
    return list(next(reader))

def handleFiles(uploaded_files,data_sources):
    for file in uploaded_files:
        try:
            if file.type=='application/json': # json
                attributes=jsonReader(file)
            else:
                attributes=csvTxTReader(file)
            data_sources["files"][str(file.name)]={
                "uploaded_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file_type":file.type,
                "attributes":attributes
            }
        except:
            st.write("Something went wrong with the file upload... please reach out to James!")
    return data_sources