import requests as req
import json
import streamlit as st

#### Helper functions to build request ####

def makeUrl(user,repo,path):
    if not path:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    else:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers/{path}"
    return url
    
def makeHeaders(auth_token):
    headers = {"Authorization": "Bearer "+str(auth_token),"Accept": "application/vnd.github+json"}
    return headers

def makeRequest(req_type,d,user,auth_token,path=""):
    repo="blank-app"
    url=makeUrl(user,repo,path)
    headers=makeHeaders(auth_token)
    try:
        if req_type=="GET":
            response = req.get(url, headers=headers)
            return response.json()
        if req_type=="PUT":
            response = req.put(url, headers=headers,json=d)
            return response.json()
    except:
        st.badge(f"GitHub request to {url} failed")
        return ""
        

#### Individual requests to github ####

def getCustomerList(user,auth_token):
    customer_list=[""]
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,auth_token)
    try:
        for item in data:
            customer_list.append(item["name"])
        customer_list.remove("schema") # only show real customers
        return customer_list
    except:
        return ""

def getCustomerDataMap(req_type,d,user,auth_token,customer):
    import base64
    path=f"{customer}/data_map.json"
    req_type,d="GET",None
    data=makeRequest(req_type,d,user,auth_token,path)
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

def getEntitiesSchema(user,auth_token):
    path=""
    data=makeRequest(user,auth_token,path)
    try:
        #parse data
        return 0
    except:
        return ""
    
def updateGithub(user,auth_token,customer,target,req_data):
    req_type="PUT"
    json_string = json.dumps(req_data).encode('utf-8')
    base64 = base64.b64encode(json_string)
    data={
        "message":"update from mapping tool",
        "committer":{
            "name":"James Anderson",
            "email":"james.anderson@dexcarehealth.com"
            },
        "content":base64
        } # convert request data to base64 encoding
    path=f"{customer}/{target}.json"
    try:
        data=makeRequest(req_type,data,user,auth_token,path)
    except Exception as e:
        st.badge(e,color="red")