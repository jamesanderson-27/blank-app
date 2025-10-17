import os
import streamlit as st
from utilities.handle_files import handleFiles
from utilities.streamlit_helper import fieldMapper,customerLock,fileLock,sidebarMapping,housekeeping
from utilities.handle_github_data import getCustomerList,getCustomerDataMap,getCustomerDataSources,updateGithub

# Housekeeping
    # Maintenance items during app formalization:
        # 1. Create generic github user, set the username below
        # 2. Create GitHub PATs, set those in the streamlit env secrets

user="jamesanderson-27"
st.session_state.API_KEY=os.environ.get('API_KEY')
st.session_state.API_KEY_WRITE=os.environ.get('API_KEY_WRITE')
schemas=housekeeping() # there's a lot that needs to run on app initialization

####### View Customer (Sidebar) #######
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

####### Edit Customer (Main Tab) #######
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
        st.toast("Use ctrl F to find schema objects", icon=":material/search:", duration="infinite")
        st.divider()
        st.subheader("Map to DexCare Schema")
        for schema in sorted(list(schemas.keys())):                  
            if schema not in data_map["mapping"]:
                data_map["mapping"][schema]={}
            with st.expander(f"**{schema}**"):                        # drives mapping UI dropdowns
                for field in list(schemas[schema]["field_names"]): 
                    data_map=fieldMapper(field,data_sources,data_map,schema)
        st.session_state[f"{customer}_data_map"]=data_map             # stores field mapping in session
        if st.button("Save Mapping"):
            response=updateGithub(user,customer,"data_map",data_map)  # (TO DO - write to GitHub)

####### View Customer (Sidebar) #######
with st.sidebar:
    if view_customer:
        sidebarMapping(view_customer,customer,data_map)
    else:
        st.markdown("*Select a customer to view current mapping*")