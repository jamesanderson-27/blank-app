import streamlit as st
import csv
import json
from typing import Set, Union
from datetime import datetime

####### File Upload Activity #######

def getJsonAttributes(obj: Union[dict, list], prefix: str = "") -> Set[str]:
    attributes = set()

    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict) or (isinstance(value, list) and any(isinstance(i, dict) for i in value)):
                # Skip adding this key, but recurse into it
                attributes.update(getJsonAttributes(value, prefix=full_key))
            else:
                attributes.add(full_key)

    elif isinstance(obj, list):
        for item in obj:
            attributes.update(getJsonAttributes(item, prefix=prefix))

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