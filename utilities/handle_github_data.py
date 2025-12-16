import json
import base64
import requests as req
import streamlit as st
from datetime import datetime

#### Helper functions to build requests ####
def makeUrl(user,repo,path):
    if not path: # used by getCustomerList()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    elif repo=="entities-schema": # used by getEntitiesSchema()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/packages/entities-schema-ingest/schema/{path}"
    else: # used by getCustomerDataSources(), getCustomerDataMap() & updateGitHub()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers/{path}"
    return url
    
def makeHeaders(write,target):
    if write: # used by updateGitHub()
        auth_token=st.session_state.API_KEY_WRITE
    else:
        auth_token=st.session_state.API_KEY
    headers = {"Authorization": "Bearer "+str(auth_token),
               "Accept": "application/vnd.github+json",
               "sha": str(st.session_state[f"{target}_sha"])}
    return headers

def makeRequest(req_type,d,user,write=0,path="",repo="blank-app",target="data_map"):
    url=makeUrl(user,repo,path)
    headers=makeHeaders(write,target)
    try:
        if req_type=="GET":
            response = req.get(url, headers=headers)
            return response.json()
        if req_type=="PUT" or "PUT MD": # used by updateGitHub()
            response = req.put(url, headers=headers,json=d)
            return response.json()
    except Exception as e:
        st.badge(f"GitHub request failed: {e}.",color="red")
        return {}

#### Individual requests to GitHub API ####
@st.cache_data
def getCustomerList(user):
    customer_list=[""]
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,write=0)
    try:
        for item in data:
            customer_list.append(item["name"])
        customer_list.remove("schema") # only show real customers
        return customer_list
    except:
        return []

def getSchemaSmall(user,path):
    data=makeRequest("GET","",user,0,path,"entities-schema")
    content=data["content"]
    decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
    field_json = json.loads(decoded_content.decode('utf-8'))
    return field_json

@st.cache_data
def getEntitiesSchema(schemas,exclusion_list):
    user = "DexCare"
    def collectFields(schema_name, schema_path, seen_paths, store_seen):
        if (schema_path in seen_paths):
            return {}
        if store_seen:
            seen_paths.add(schema_path)
        field_dict = {}
        schema_json = getSchemaSmall(user, schema_path)
        properties = schema_json.get("properties", {})
        for field, field_data in properties.items():
            if field in exclusion_list:
                continue
            ref_path = None
            nested_fields = {}
            if "$ref" in field_data:
                ref_path = field_data["$ref"].strip("./")
            elif ("items" in field_data and "$ref" in field_data["items"]):
                ref_path = field_data["items"]["$ref"].strip("./")
            if ref_path:
                nested_fields = collectFields(schema_name, ref_path, seen_paths,False)
                field_dict[field] = {"nested":nested_fields}
            else:
                field_dict[field] = {}
                try:
                    field_dict[field]["description"]=field_data["description"]
                    field_dict[field]["type"]=field_data["type"]
                except:
                    pass
        return field_dict
    for schema_name, schema_info in schemas.items():
        path = schema_info["file_name"]
        seen = set()
        fields = collectFields(schema_name, path, seen,True)
        schemas[schema_name]["field_names"] = fields
    return schemas

def getCustomerDataMap(user,customer,bool=0):
    path=f"{customer}/data_map.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,0,path)
    try:
        st.session_state.data_map_sha=data["sha"] # called within edit activity
        st.session_state.data_map_md_sha=data["sha"]
        content=data["content"]
        decoded_content = base64.b64decode(content)
        data_map = json.loads(decoded_content.decode('utf-8'))
        if bool:
            st.session_state.saved_data_map=data_map
            data=makeRequest(req_type,d,user,0,f"{customer}/data_map.md") # stores the sha of the md file for later use
            
        return data_map
    except:
        data_map = {
                "last_modified_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_modified_user":st.session_state.user,
                "mapping":{}
            }
        return dict(data_map)

def getCustomerDataSources(user,customer):
    path=f"{customer}/data_sources.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,0,path,target="data_sources")
    try:
        st.session_state.data_sources_sha=data["sha"] # while we're here, grab the sha for PUT request
        content=data["content"]
        decoded_content = base64.b64decode(content)
        data_sources = json.loads(decoded_content.decode('utf-8'))
    except:
        data_sources = {
                    "files":{
                        "":{
                            "uploaded_at":"",
                            "file_type":"",
                            "attributes":[]
                        }
                    }
                }
    return data_sources
    
def updateGithub(user,customer,target,req_data,req_type="PUT"):
    if req_type=="PUT":
        data_str = json.dumps(req_data, indent=2)
        path=f"{customer}/{target}.json"
        sha=st.session_state[f"{target}_sha"]
    if req_type=="PUT MD":
        data_str=str(req_data)
        path=f"{customer}/{target}.md"
        sha=st.session_state.data_map_md_sha
    encoded_data = base64.b64encode(data_str.encode()).decode()  # convert to base64 encoding for GitHub API
    data={
        "committer":{
            "name":"James Anderson",
            "email":"james.anderson@dexcarehealth.com"
        },
        "message":"update from mapping tool",
        "sha":sha,
        "content":encoded_data,
        "branch":"main"
        }
    try:
        response=makeRequest(req_type,data,user,1,path,target=target)
        return response
    except Exception as e:
        return f"Failed to update: {customer}'s {target}. Error: {e}"
