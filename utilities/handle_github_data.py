import requests as req
import json
import base64
import streamlit as st

#### Helper functions to build request ####

def makeUrl(user,repo,path):
    if not path:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    elif repo=="entities-schema":
        url=f"https://api.github.com/repos/{user}/{repo}/contents/packages/entities-schema-ingest/schema/{path}"
    elif path=="commit":
        url=f"https://api.github.com/repos/{user}/{repo}/git/commits"        
    else:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers/{path}"
    return url
    
def makeHeaders(write):
    if write:
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
        if req_type=="PUT":
            response = req.put(url, headers=headers,json=d)
            return response.json()
    except Exception as e:
        st.badge(f"GitHub request failed: {e}.",color="red")
        return ""
        

#### requests to github ####
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
        return ""

def getCustomerDataMap(user,customer,bool=0):
    if f"{customer}_current_data_map" not in st.session_state:
        st.session_state[f"{customer}_current_data_map"]={}
    path=f"{customer}/data_map.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,0,path)
    if bool: # dynamic add to grab sha
        try:
            st.session_state.data_map_sha=data["sha"] # while we're here, grab the sha for PUT request
        except:
            pass
    try:
        content=data["content"]
        decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
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

@st.cache_data
def getEntitiesSchema():
    st.session_state.count+=1
    user="DexCare"
    schemas={
                "Provider":{
                    "file_name":"clinicianIngest.json",
                    "field_names":[]
                },                 
                "Department":{
                    "file_name":"departmentIngest.json",
                    "field_names":[]
                }
            }
    exclusion_list=[]
    # for schema in schemas
    for schema in schemas:
        path=schemas[schema]["file_name"]
        data=makeRequest("GET","",user,0,path,"entities-schema")
        content=data["content"]
        decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
        field_json = json.loads(decoded_content.decode('utf-8'))
        for field in field_json["properties"]:
            if field in exclusion_list:
                pass
            else:
                schemas[schema]["field_names"].append(field)
    return schemas

        # iterate through the json and add each field name to the list
            # exclusion list fsor field names
            # if the field has an $ref, call to that file and add those field names

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
        decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
        data_sources = decoded_content.decode('utf-8')
        return json.loads(data_sources)
    except:
        data_sources = {
                    "files":{
                        "<file_name>":{
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
    encoded_data = base64.b64encode(json_string) # convert to base64 encoding
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
        st.badge(f"Error: {e}",color="red")
        return "failure"