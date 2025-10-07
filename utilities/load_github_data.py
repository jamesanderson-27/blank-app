import requests as re
import streamlit as st

#### Helper functions to build request ####

def makeUrl(user,repo,path):
    if not path:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    else:
        url=f"https://api.github.com/repos/{user}/{repo}/contents/customers/{path}"
    return url
    
def makeHeaders(auth_token):
    headers = {"Authorization": auth_token,"Accept": "application/vnd.github+json"}
    return headers

def makeRequest(user,auth_token,repo,path=""):
    url=makeUrl(user,repo,path)
    headers=makeHeaders(auth_token)
    try:
        response = re.get(url, headers=headers)
        return response.json()
    except:
        st.badge("Could not load github data",color="red")
        
    

#### Individual requests to github ####

def getCustomerList(user,auth_token):
    repo="blank-app" # will change when generic user is created
    customer_list=[""]
    data=makeRequest(user,auth_token,repo)
    if data:
        for item in data:
            customer_list.append(item["name"])
        customer_list.remove("schema") # only show real customers
        return customer_list
    else:
        return ""

def getCustomerDataMap(user,auth_token,customer):
    import base64
    repo="blank-app"  # will change when generic user is created
    path=f"{customer}/data_map.json"
    data=makeRequest(user,auth_token,repo,path)
    if not data:
        content=data["content"]
        decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
        data_map = decoded_content.decode('utf-8')
        return data_map
    else:
        return ""

def getEntitiesSchema(user,auth_token,repo):
    repo="entities-schema"
    path=""
    data=makeRequest(user,auth_token,repo,path)
    if not data:
        pass
    else:
        return ""
