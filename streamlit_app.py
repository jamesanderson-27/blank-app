import streamlit as st
from utilities.handle_files import handleFiles
from utilities.housekeeping import housekeeping,loadSchemas
from utilities.handle_mapping import fieldMapper,customerLock,fileLock,sidebarMapping
from utilities.handle_github_data import getCustomerList,getCustomerDataMap,getCustomerDataSources,updateGithub

housekeeping() # there's a lot that needs to run on app launch
schemas=loadSchemas()

####### View Customer (Sidebar) #######
with st.sidebar:
    st.title("View Customer Mapping")
    user=st.session_state.user
    customer_list=getCustomerList(user)
    try:
        idx=customer_list.index(view_customer) # type: ignore
    except:
        idx=0
    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=idx)
    st.divider()

####### Edit Customer (Main Tab) #######
st.subheader("Edit Customer Mapping")

customer=st.selectbox("Select Customer",
                    customer_list,
                    key="customer",
                    index=0,
                    disabled=st.session_state.customer_locked)
st.session_state.data_map = getCustomerDataMap(user,customer)
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
    st.session_state.data_sources=getCustomerDataSources(user,customer)              # loads previous files                   
    st.session_state.data_sources=handleFiles(uploaded_files,st.session_state.data_sources)             # allows upload of new files
    if len(list(st.session_state.data_sources["files"].keys())[1:])>0:
        st.write("Uploaded files")
    for file in list(st.session_state.data_sources["files"].keys())[1:]:               # shows user each file and
        n_attributes=len(st.session_state.data_sources["files"][file]["attributes"])   # its number of attributes
        st.write(f"*{file}* has {n_attributes} attributes.")          
    if st.button("Save Files"):                                       # saves data_sources to github
        fileLock()
        response=updateGithub(user,customer,"data_sources",st.session_state.data_sources)
        st.rerun()

    ####### Data Mapping #######
    if st.session_state.file_locked:                                  # User continues to mapping
        st.toast("Use ctrl F to find schema objects", icon=":material/search:", duration="infinite")
        st.divider()
        st.subheader("Map to DexCare Schema")
        for schema in sorted(list(schemas.keys())):                  
            if schema not in st.session_state.data_map["mapping"]:
                st.session_state.data_map["mapping"][schema]={}
            with st.expander(f"**{schema}**"):                        # drives mapping UI dropdowns
                for field in schemas[schema]["field_names"].keys():
                    if schemas[schema]["field_names"][field].keys():  # shows nested fields (e.g. address_line_1) under fields (e.g. address)                    
                            with st.expander(f"{schema}.*{field}*"):
                                for nested_field in schemas[schema]["field_names"][field].keys():
                                    if not (f"{field}.{nested_field}" in st.session_state.exclusion_list):
                                        st.session_state.data_map=fieldMapper(f"{field}.{nested_field}",st.session_state.data_sources,st.session_state.data_map,schema)
                    else:
                        st.session_state.data_map=fieldMapper(field,st.session_state.data_sources,st.session_state.data_map,schema)
        if st.button("Save Mapping"):
            response=updateGithub(user,customer,"data_map",st.session_state.data_map)

####### View Customer (Sidebar) #######
with st.sidebar:
    if view_customer:
        sidebarMapping(view_customer,customer,st.session_state.data_map,st.session_state.user)
    else:
        st.markdown("*Select a customer to view current mapping*")