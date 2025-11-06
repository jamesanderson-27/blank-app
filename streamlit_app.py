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
    
    # Only initialize view_customer if not already set
    if 'view_customer' not in st.session_state:
        st.session_state.view_customer = ""
    
    try:
        idx=customer_list.index(st.session_state.view_customer)
    except:
        idx=0
    
    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=idx)
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
    if view_customer: # Only render sidebar mapping if a customer is selecteds
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
    
    # Load data_sources once when customer is locked
    if 'data_sources' not in st.session_state:
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
        
        if 'mapping_initialized' not in st.session_state:
            for schema in sorted(list(schemas.keys())):                # Build the map once, not every run                  
                if schema not in st.session_state.data_map["mapping"]:
                    st.session_state.data_map["mapping"][schema]={}
            st.session_state.mapping_initialized = True
        
        # Initialize lazy loading state tracking
        if 'loaded_schemas' not in st.session_state:
            st.session_state.loaded_schemas = set()
        if 'loaded_fields' not in st.session_state:
            st.session_state.loaded_fields = set()
        
        for schema in sorted(list(schemas.keys())):
            # Create a button-based lazy loading system
            col1, col2 = st.columns([3, 1])
            
            with col1:
                schema_expander = st.expander(f"**{schema}**")
            
            with col2:
                load_button_key = f"load_schema_{schema}"
                if st.button(f"Load {schema}", key=load_button_key, disabled=schema in st.session_state.loaded_schemas):
                    st.session_state.loaded_schemas.add(schema)
                    st.rerun()
            
            with schema_expander:
                if schema in st.session_state.loaded_schemas:
                    for field in schemas[schema]["field_names"].keys():
                        if schemas[schema]["field_names"][field].get("nested",False):
                            # For nested fields, create another level of lazy loading
                            field_id = f"{schema}_{field}"
                            
                            field_col1, field_col2 = st.columns([3, 1])
                            with field_col1:
                                field_expander = st.expander(f"{schema}.*{field}*")
                            
                            with field_col2:
                                field_load_key = f"load_field_{field_id}"
                                if st.button(f"Load", key=field_load_key, disabled=field_id in st.session_state.loaded_fields):
                                    st.session_state.loaded_fields.add(field_id)
                                    st.rerun()
                            
                            with field_expander:
                                if field_id in st.session_state.loaded_fields:
                                    for nested_field in schemas[schema]["field_names"][field]["nested"].keys():
                                        description=schemas[schema]["field_names"][field]["nested"][nested_field].get("description","")
                                        field_type=schemas[schema]["field_names"][field]["nested"][nested_field].get("type","")
                                        if not ((f"{field}.{nested_field}" in st.session_state.exclusion_list) or (nested_field=="description")):
                                            st.session_state.data_map=fieldMapper(f"{field}.{nested_field}",
                                                                                  st.session_state.data_sources,
                                                                                  st.session_state.data_map,
                                                                                  schema,
                                                                                  description,
                                                                                  field_type)
                                else:
                                    st.info(f"Click 'Load' to show {field} mapping fields")
                        else:
                            description=schemas[schema]["field_names"][field].get("description","")
                            field_type=schemas[schema]["field_names"][field].get("type","")
                            st.session_state.data_map=fieldMapper(field,
                                                                  st.session_state.data_sources,
                                                                  st.session_state.data_map,
                                                                  schema,
                                                                  description,
                                                                  field_type)
                else:
                    st.info(f"Click 'Load {schema}' to show mapping fields for this schema")
        if st.button("Save Mapping"):
            mapLock(user,customer)