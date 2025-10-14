import os
import streamlit as st
from utilities.handle_files import handleFiles
from utilities.streamlit_helper import styleButtons,fieldMapper,customerLock,fileLock,sidebarMapping
from utilities.handle_github_data import getCustomerList,getCustomerDataMap,getCustomerDataSources,updateGithub

# Housekeeping
    # Maintenance items during app finalization:
        # 1. Create generic github user, set the username below
        # 2. Create GitHub PATs, set those in the streamlit env ssecrets
user="jamesanderson-27" 
st.session_state.API_KEY=os.environ.get('API_KEY') 
st.session_state.API_KEY_WRITE=os.environ.get('API_KEY_WRITE')
styleButtons()

# State Management
if "data_map_sha" not in st.session_state:
    st.session_state.data_map_sha=""
if 'customer_locked' not in st.session_state:
    st.session_state.customer_locked = False
if 'file_locked' not in st.session_state:
    st.session_state.file_locked = False

####### View Customer Sidebar #######
with st.sidebar:
    st.title("View Customer Mapping")
    customer_list=getCustomerList(user)
    try:
        idx=customer_list.index(view_customer) # type: ignore
    except:
        idx=0
    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=idx)
    data_map = getCustomerDataMap(user,view_customer)
    st.divider()

####### Edit Customer Main Tab #######
st.subheader("Edit Customer Mapping")
customer=st.selectbox("Select Customer",
                    customer_list,
                    key="customer",
                    index=0,
                    disabled=st.session_state.customer_locked)
if st.button("Save Customer"):
    customerLock(user,customer)
    st.rerun()
if st.session_state.customer_locked:
    st.divider()

    ####### File Upload #######
    st.subheader("Upload Files")
    uploaded_files = st.file_uploader("Choose one or more files",
                                    type=['csv', 'txt','json'],
                                    accept_multiple_files=True,
                                    disabled=st.session_state.file_locked)
    data_sources=getCustomerDataSources(user,customer,1)              # loads previous files                   
    data_sources=handleFiles(uploaded_files,data_sources)             # allows upload of new files
    if len(list(data_sources["files"].keys())[1:])>0:
        st.write("Uploaded files")
    for file in list(data_sources["files"].keys())[1:]:               # shows user each file and
        n_attributes=len(data_sources["files"][file]["attributes"])   # its number of attributes
        st.write(f"*{file}* has {n_attributes} attributes.")          
    if st.button("Save Files"):                                       # saves data_sources to github
        fileLock()                                                    # locks file upload activity
        st.rerun()

    ####### Data Mapping #######
    if st.session_state.file_locked:                                  # User continues to mapping
        st.divider()
        st.subheader("Map to DexCare Schema")
        schemas={"Provider":["emr_id","npi","name"],                  # (TO DO - pull from ingest schema)
             "Department":["display_name","emr_id"]
            }
        for schema in sorted(list(schemas.keys())):                  
            if schema not in data_map["mapping"]:
                data_map["mapping"][schema]={}
            with st.expander(schema):                                 # drives mapping UI dropdowns
                for field in sorted(list(schemas[schema])): 
                    data_map=fieldMapper(field,data_sources,data_map,schema)  
        st.session_state[f"{customer}_data_map"]=data_map             # stores field mapping in session
        if st.button("Save"):
            response=updateGithub(user,customer,"data_map",data_map)  # (TO DO - write to GitHub)

####### View Customer Siderbar #######
with st.sidebar:
    toggle_state = st.toggle("",label_visibility="collapsed")
    sidebarMapping(toggle_state,view_customer,customer,user,data_map)
    if not view_customer:
        st.markdown("*Select a customer to view current mapping*")