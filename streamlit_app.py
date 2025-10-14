import os
import streamlit as st
from utilities.handle_files import handleFiles
from utilities.handle_markdown import schemaToMarkdown
from utilities.streamlit_helper import fieldMapper,styleButtons,customerLock,fileLock
from utilities.load_github_data import getCustomerList,getCustomerDataMap,updateGithub,getDataSources

# Housekeeping
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
        idx=customer_list.index(view_customer)
    except:
        idx=0

    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=idx)
    
    data_map = getCustomerDataMap(user,view_customer)
    st.divider()
    


####### Edit Customer Main #######
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

    ####### Schema Load ####### (TO DO)
    schemas={                      
            "Provider":["emr_id","npi","name"],
            "Department":["display_name","emr_id"]
        }
    
    ####### File Upload #######
    st.subheader("Upload Files")

    uploaded_files = st.file_uploader("Choose one or more files",
                                    type=['csv', 'txt','json'],
                                    accept_multiple_files=True,
                                    disabled=st.session_state.file_locked)
    
    data_sources=getDataSources(user,customer,1)                      # load previous files
    data_sources=handleFiles(uploaded_files,data_sources)             # upload new files

    if len(list(data_sources["files"].keys())[1:])>0:
        st.write("Uploaded files")

    for file in list(data_sources["files"].keys())[1:]:               # skips null key
        n_attributes=len(data_sources["files"][file]["attributes"])   # counts attributes per file
        st.write(f"*{file}* has {n_attributes} attributes.")          

    if st.button("Save Files"):                                       # saves data_sources to github
        fileLock()                                                    # locks file upload activity
        st.rerun()

    if st.session_state.file_locked:                                  # User continues to mapping

        st.divider()

        ####### Data Mapping #######
        st.subheader("Map to DexCare Schema")

        for schema in sorted(list(schemas.keys())):                  
            if schema not in data_map["mapping"]:
                data_map["mapping"][schema]={}

            with st.expander(schema):                                 # drives mapping UI dropdowns
                for field in sorted(list(schemas[schema])): 
                    data_map=fieldMapper(field,data_sources,data_map,schema)  

        st.session_state[f"{customer}_data_map"]=data_map             # stores field mapping in session

        if st.button("Save"):
            response = updateGithub(user,customer,"data_map",data_map)
            # update customer/data_map.md
            # update customer/data_sources.json

####### View Customer Siderbar #######
with st.sidebar:
    toggle_state = st.toggle("",label_visibility="collapsed")
    if toggle_state:
        st.badge("Draft Mapping",color="red")

        try:
            if view_customer:
                st.markdown(schemaToMarkdown(st.session_state[f"{view_customer}_data_map"],view_customer),unsafe_allow_html=True)

        except:
            if view_customer and not customer:      # view customer selected, edit customer unselected
                data_map = getCustomerDataMap(user,view_customer)
                st.markdown(schemaToMarkdown(data_map,view_customer),unsafe_allow_html=True)

            elif view_customer and (view_customer!=customer):       # different customers selected
                data_map = getCustomerDataMap(user,view_customer)
                st.markdown(schemaToMarkdown(data_map,customer),unsafe_allow_html=True)

            elif view_customer and (view_customer==customer):       # same customers selected
                st.markdown(schemaToMarkdown(data_map,customer),unsafe_allow_html=True)
    else:
        st.badge("Current Mapping",color="grey")
        if view_customer:
            st.markdown(schemaToMarkdown(getCustomerDataMap(user,view_customer),view_customer),unsafe_allow_html=True)

    if not view_customer:
        st.markdown("*Select a customer to view current mapping*")
            
