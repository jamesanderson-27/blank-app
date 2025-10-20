import json
import base64
import requests as req
import streamlit as st

#### Helper functions to build requests ####
def makeUrl(user,repo,path):
    if not path: # used by getCustomerList()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    elif repo=="entities-schema": # used by getEntitiesSchema()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/packages/entities-schema-ingest/schema/{path}"
    elif path=="commit": # used by updateGitHub()
        url=f"https://api.github.com/repos/{user}/{repo}/git/commits"
    else: # used by getCustomerDataSources() and getCustomerDataMap()
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers/{path}"
    return url
    
def makeHeaders(write):
    if write: # used by updateGitHub()
        auth_token=st.session_state.API_KEY_WRITE
    else:
        auth_token=st.session_state.API_KEY
    headers = {"Authorization": "Bearer "+str(auth_token),
               "Accept": "application/vnd.github+json",
               "sha": str(st.session_state.data_map_sha)}
    return headers

def makeRequest(req_type,d,user,write=0,path="",repo="blank-app"):
    url=makeUrl(user,repo,path)
    headers=makeHeaders(write)
    try:
        if req_type=="GET":
            response = req.get(url, headers=headers)
            return response.json()
        if req_type=="PUT": # used by updateGitHub()
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

def getCustomerDataMap(user,customer,bool=0):
    if f"{customer}_current_data_map" not in st.session_state:
        st.session_state[f"{customer}_current_data_map"]={}
    path=f"{customer}/data_map.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,0,path)
    try:
        if bool:
            st.session_state.data_map_sha=data["sha"] # used by getCustomerDatamap() called within edit activity
        content=data["content"]
        decoded_content = base64.b64decode(content)
        data_map = decoded_content.decode('utf-8')
        st.session_state[f"{customer}_current_data_map"]=json.loads(data_map)
        return json.loads(data_map)
    except:
        data_map = {
                "last_modified_time":"",
                "last_modified_user":"",
                "mapping":{}
            }
        return dict(data_map)

def getSchemaSmall(user,path):
    data=makeRequest("GET","",user,0,path,"entities-schema")
    content=data["content"]
    decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
    field_json = json.loads(decoded_content.decode('utf-8'))
    return field_json

@st.cache_data
def getEntitiesSchema(schemas,exclusion_list):
    user = "DexCare"
    def collectFields(schema_name, schema_path, seen_paths):
        if schema_path in seen_paths:
            return {}
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
            elif "items" in field_data and "$ref" in field_data["items"]:
                ref_path = field_data["items"]["$ref"].strip("./")
            if ref_path:
                nested_fields = collectFields(schema_name, ref_path, seen_paths)
                field_dict[field] = nested_fields
            else:
                field_dict[field] = {}
        return field_dict
    for schema_name, schema_info in schemas.items():
        path = schema_info["file_name"]
        seen = set()
        fields = collectFields(schema_name, path, seen)
        schemas[schema_name]["field_names"] = fields
    return schemas

@st.cache_data
def getCustomerDataSources(user,customer,bool=0):
    path=f"{customer}/data_sources.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,0,path)
    if bool: # dynamic add to grab sha
        try:
            st.session_state.data_sources_sha=data["sha"] # while we're here, grab the sha for PUT request
        except:
            pass
    try:
        content=data["content"]
        decoded_content = base64.b64decode(content)
        data_sources = decoded_content.decode('utf-8')
        return json.loads(data_sources)
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
        return dict(data_sources)
    
def updateGithub(user,customer,target,req_data):
    req_type="PUT"
    json_string = json.dumps(req_data).encode('utf-8')
    encoded_data = base64.b64encode(json_string) # convert to base64 encoding for GitHub API
    data={
        "message":"update from mapping tool",
        "committer":{
            "name":"James Anderson",
            "email":"james.anderson@dexcarehealth.com"
            },
            "tree":str(st.session_state.data_map_sha),
        "content":encoded_data
        }
    path="commit"
    try:
        data=makeRequest(req_type,data,user,1,path)
        return data
    except Exception as e:
        st.badge(f""Failed to update: {customer}'s {target}. Error: {e}",color="red")
