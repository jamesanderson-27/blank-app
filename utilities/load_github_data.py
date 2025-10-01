import requests as re
import streamlit as st
# Customer data load - called after a user selects a customer

def makeUrl(user,repo,path,customer=""):
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
    st.write(url)
    headers=makeHeaders(auth_token)
    response = re.get(url, headers=headers)
    return response.json()

def getCustomerList(user,auth_token):
    repo="blank-app" # will change when generic user is created
    customer_list=[""]
    data=makeRequest(user,auth_token,repo)
    for item in data:
        customer_list.append(item["name"])
    customer_list.remove("schema") # only show real customers
    return customer_list

def getCustomerDataMap(user,auth_token,customer):
    repo="blank-app"
    path=f"{customer}/output.json"
    data=makeRequest(user,auth_token,repo,path)
    return data

def getEntitiesSchema(user,auth_token,repo):
    repo="entities-schema"
    path=""
    data=makeRequest(user,auth_token,repo,path)
    pass