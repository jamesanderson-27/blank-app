import requests as re

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
    response = re.get(url, headers=headers)
    return response.json()

#### Individual requests to github ####

def getCustomerList(user,auth_token):
    repo="blank-app" # will change when generic user is created
    customer_list=[""]
    data=makeRequest(user,auth_token,repo)
    for item in data:
        customer_list.append(item["name"])
    customer_list.remove("schema") # only show real customers
    return customer_list

def getCustomerDataMap(user,auth_token,customer):
    import base64
    repo="blank-app"  # will change when generic user is created
    path=f"{customer}/data_map.json"
    data=makeRequest(user,auth_token,repo,path)
    content=data["content"]
    decoded_content = base64.b64decode(content)  # Decode Base64 to bytes
    data_map = decoded_content.decode('utf-8')
    return data_map

def getEntitiesSchema(user,auth_token,repo):
    repo="entities-schema"
    path=""
    data=makeRequest(user,auth_token,repo,path)
    pass
