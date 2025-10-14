import requests as req
import json
import base64
import streamlit as st

#### Helper functions to build request ####

def makeUrl(user,repo,path):
    if not path:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    if path=="commit":
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

def makeRequest(req_type,d,user,write=0,path=""):
    repo="blank-app"
    url=makeUrl(user,repo,path)
    headers=makeHeaders(0)
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
        return json.loads(data_map)
    except:
        data_map = {
                "last_modified_time":"",
                "last_modified_user":"",
                "mapping":{}
            }
        return dict(data_map)

def getEntitiesSchema(user):
    path=""
    data=makeRequest(user,0,path)
    try:
        #parse data
        return 0
    except:
        return ""
    
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