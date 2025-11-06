import csv
import json
import streamlit as st
from typing import Union
from datetime import datetime
import io

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
    try:
        file.seek(0)
        chunk_size = 8192  # 8KB chunks
        first_line = ""
        sample_for_sniffing = ""
        
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunk_str = chunk.decode('utf-8', errors='ignore')
            sample_for_sniffing += chunk_str
            newline_pos = chunk_str.find('\n')
            if newline_pos != -1:
                first_line = (first_line + chunk_str[:newline_pos]).strip()
                break
            else:
                first_line += chunk_str
            if len(sample_for_sniffing) > 2048:
                sample_for_sniffing = sample_for_sniffing[:2048]
                break
        if not first_line and sample_for_sniffing:
            first_line = sample_for_sniffing.strip()
        dialect = csv.Sniffer().sniff(sample_for_sniffing[:1024])  # Use max 1KB for sniffing
        delim = dialect.delimiter
        if first_line:
            reader = csv.reader([first_line], delimiter=delim)
            headers = list(next(reader))
            return headers
        else:
            st.badge(f"Could not read header from {str(file.name)}", color='orange')
            return []
    except Exception as e:
        st.badge(f"Using simple fallback for {str(file.name)}: {str(e)[:50]}...", color='orange')
        try:
            file.seek(0)
            first_line = file.readline().decode('utf-8', errors='ignore').strip()
            if first_line:
                for delim in [',', '\t', ';', '|']:
                    try:
                        reader = csv.reader([first_line], delimiter=delim)
                        headers = list(next(reader))
                        if len(headers) > 1:  # If we get multiple columns, this is likely correct
                            return headers
                    except:
                        continue
                return [first_line]
            else:
                st.badge(f"Empty file: {str(file.name)}", color='red')
                return []
        except Exception as fallback_error:
            st.badge(f"Error reading file: {fallback_error}", color='red')
            return []

def handleFiles(uploaded_files):

    st.session_state.debug={}


    for file in uploaded_files:
        if str(file.name) in st.session_state.data_sources["files"]:
            pass
        else:
            try:
                if file.type=='application/json': # json
                    attributes=jsonReader(file)
                else:
                    attributes=csvTxTReader(file)
                st.session_state.data_sources["files"][str(file.name)]={
                    "uploaded_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "file_type":file.type,
                    "attributes":attributes
                }
            except:
                st.write(f"Something went wrong with the upload of {str(file.name)}... please reach out to James!")
    return st.session_state.data_sources