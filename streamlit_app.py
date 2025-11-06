import streamlit as st
from utilities.handle_files import handleFiles
from utilities.housekeeping import housekeeping,loadSchemas
from utilities.handle_mapping import fieldMapper,customerLock,fileLock,mapLock,sidebarMapping,clearFieldMapperCache
from utilities.handle_github_data import getCustomerList,getCustomerDataMap,getCustomerDataSources

####### Run on app launch #######
housekeeping() # env variables, button styling, secret reading
if 'schemas' not in st.session_state:
    st.session_state.schemas = None
user=st.session_state.user
if 'customer_list' not in st.session_state:
    st.session_state.customer_list = getCustomerList(user)
customer_list = st.session_state.customer_list

####### View Customer (Sidebar) #######
with st.sidebar:
    st.title("View Customer Mapping")
    if 'view_customer' not in st.session_state:
        st.session_state.view_customer = ""
        idx=0
    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=customer_list.index(st.session_state.view_customer))
    st.divider()

####### Edit Customer #######
st.subheader("Edit Customer Mapping")
customer=st.selectbox("Select Customer",
                    customer_list,
                    key="customer",
                    index=0,
                    disabled=st.session_state.customer_locked)

if not st.session_state.customer_locked:
    if 'current_customer' not in st.session_state or st.session_state.current_customer != customer:
        st.session_state.data_map = getCustomerDataMap(user,customer)
        st.session_state.current_customer = customer
        
with st.sidebar:
    if view_customer: # Only render sidebar mapping if a customer is selected
        sidebarMapping(view_customer,customer,st.session_state.data_map,st.session_state.user)
    else:
        st.markdown("*Select a customer to view current mapping*")

if st.button("Save Customer"):
    customerLock(user,customer)
    st.rerun()
    
if st.session_state.customer_locked:
    st.divider()

    ####### File Upload #######
    st.subheader("Upload Files")
    if 'data_sources' not in st.session_state: # Load data_sources once when customer is locked
        st.session_state.data_sources=getCustomerDataSources(user,customer)
    
    uploaded_files = st.file_uploader("Choose one or more files",
                                    type=['csv', 'txt','json'],
                                    accept_multiple_files=True,
                                    disabled=st.session_state.file_locked)
    
    if not st.session_state.file_locked and uploaded_files:                
        st.session_state.data_sources=handleFiles(uploaded_files)             # allows upload of new files
        clearFieldMapperCache()  # Clear cached data when files change
    if len(list(st.session_state.data_sources["files"].keys())[1:])>0:
        st.write("Uploaded files")
    for file in list(st.session_state.data_sources["files"].keys())[1:]:               # shows user each file and
        n_attributes=len(st.session_state.data_sources["files"][file]["attributes"])   # its number of attributes
        st.write(f"*{file}* has {n_attributes} attributes.")          
    if st.button("Save Files"):                                       # saves data_sources to github
        fileLock(user,customer)
        st.rerun()

    ####### Data Mapping #######
    if st.session_state.file_locked:                                  # User continues to mapping
        if st.session_state.schemas is None:
            st.session_state.schemas = loadSchemas()
        schemas = st.session_state.schemas
        
        st.toast("Use ctrl F to find schema objects", icon=":material/search:", duration="infinite")
        st.divider()
        st.subheader("Map to DexCare Schema")
        
        # Initialize mapping structure once
        if 'mapping_initialized' not in st.session_state:
            for schema in sorted(list(schemas.keys())):                # Build the map once, not every run                  
                if schema not in st.session_state.data_map["mapping"]:
                    st.session_state.data_map["mapping"][schema]={}
            st.session_state.mapping_initialized = True
        
        for schema in sorted(list(schemas.keys())):
            with st.expander(f"**{schema}**"):
                processed_fields = set() # Group nested fields under their parent field expanders
                
                for field in schemas[schema]["field_names"].keys():
                    if field in processed_fields:
                        continue
                        
                    field_data = schemas[schema]["field_names"][field]
                    
                    if field_data.get("nested", False):
                        
                        with st.expander(f"{schema}.*{field}*"): # Handle nested fields grouped under parent
                            for nested_field in field_data["nested"].keys():
                                if nested_field != "description" and f"{field}.{nested_field}" not in st.session_state.exclusion_list:
                                    nested_data = field_data["nested"][nested_field]
                                    description = nested_data.get("description", "No description listed in entities-schema")
                                    field_type = nested_data.get("type", "")
                                    
                                    st.session_state.data_map = fieldMapper(
                                        f"{field}.{nested_field}",
                                        st.session_state.data_sources,
                                        st.session_state.data_map,
                                        schema,
                                        description,
                                        field_type
                                    )
                    else:
                        # Handle regular fields
                        description = field_data.get("description", "")
                        field_type = field_data.get("type", "")
                        
                        st.session_state.data_map = fieldMapper(
                            field,
                            st.session_state.data_sources,
                            st.session_state.data_map,
                            schema,
                            description,
                            field_type
                        )
                    
                    processed_fields.add(field)
        if st.button("Save Mapping"):
            mapLock(user,customer)
