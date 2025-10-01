import requests as re

# Customer data load - called after a user selects a customer

def makeUrl(user,repo):
    url=f"https://api.github.com/repos/{user}/{repo}/contents/customers"
    return url
    
def makeHeaders(auth_token):
    headers = {
        "Authorization": auth_token
        }
    return headers

def makeRequest(user,auth_token,repo):
    url=makeUrl(user,repo)
    headers=makeHeaders(auth_token)
    response = re.get(url, headers=headers)
    return response.json()

def getCustomerList(user,auth_token,repo):
    customer_list=[""]
    data=makeRequest(user,auth_token,repo)
    for item in data:
        customer_list.append(item["name"])
    customer_list.remove("schema") # only show real customers
    return customer_list
    