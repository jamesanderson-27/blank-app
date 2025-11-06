import streamlit as st
from utilities.handle_github_data import getCustomerDataMap,updateGithub
from utilities.handle_markdown import schemaToMarkdown

def clearFieldMapperCache():
    """Clear cached data when file structure changes"""
    # Clear file attribute caches
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('attrs_') or key.startswith('mapper_cache_')]
    for key in keys_to_remove:
        del st.session_state[key]
    
    # Force sidebar refresh
    st.session_state['force_sidebar_refresh'] = True

def customerLock(user,customer=""):
    st.session_state.customer_locked=True
    try:
        data=getCustomerDataMap(user,customer,1) # calls to a customer/data_map.json
        st.session_state.data_map_sha=data["sha"] # stores the sha of the github file for later use
    except:
        pass

def fileLock(user,customer):
    st.session_state.file_locked=True
    response=updateGithub(user,customer,"data_sources",st.session_state.data_sources)

def mapLock(user,customer):
    st.session_state.map_locked=True
    response=updateGithub(user,customer,"data_map",st.session_state.data_map)
    response=updateGithub(user,customer,"data_map",schemaToMarkdown(st.session_state.data_map),req_type="PUT MD")

def getIndex(data_map,schema,field,list_options,key):
    # Early return if data structure doesn't exist
    if ("mapping" not in data_map or 
        schema not in data_map["mapping"] or 
        field not in data_map["mapping"][schema] or 
        key not in data_map["mapping"][schema][field]):
        return 0
    
    value = data_map["mapping"][schema][field][key]
    
    # Use faster 'in' check before index lookup
    if value in list_options:
        return list_options.index(value)
    else:
        return 0
    
def saveFieldMapping(data_map,schema,field,primary_file,primary_attribute,secondary_file,secondary_attribute,fallback_value_type,fallback_value):
    if "mapping" not in data_map:
        data_map["mapping"] = {}
    if schema not in data_map["mapping"]:
        data_map["mapping"][schema] = {}
    if field not in data_map["mapping"][schema]:
        data_map["mapping"][schema][field] = {}
    
    mapping = data_map["mapping"][schema][field]
    
    # Batch update all values to reduce state mutations
    new_mapping = {
        "primary_file": primary_file or "",
        "primary_attribute": primary_attribute or "",
        "secondary_file": secondary_file or "",
        "secondary_attribute": secondary_attribute or "",
        "fallback_value_type": fallback_value_type or "None"
    }
    
    # Handle fallback value validation
    if fallback_value_type in st.session_state.validation_config: 
        config = st.session_state.validation_config[fallback_value_type]
        if config["validation"](fallback_value): 
            new_mapping["fallback_value"] = fallback_value
        else:                                                       # if the user enters a nonvalid typ
            new_mapping["fallback_value"] = config["default_fallback"]
    else:
        new_mapping["fallback_value"] = fallback_value or ""
    
    # Only update if values have actually changed
    if mapping != new_mapping:
        mapping.update(new_mapping)
        st.session_state['data_map_changed'] = True
    
    return data_map

def fieldMapper(field,data_sources,data_map,schema,description,field_type):
    with st.expander(f"{schema}.*{field}*"):                        # field (e.g. abbreviation, externalIdentifiers)
        st.code(description,language=None,wrap_lines=True)
        
        # Cache frequently used data to avoid repeated list conversions
        cache_key = f"mapper_cache_{hash(str(data_sources['files'].keys()))}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = {
                'saved_files': list(data_sources["files"].keys()),
                'validation_keys': list(st.session_state.validation_config.keys())
            }
        
        cached_data = st.session_state[cache_key]
        saved_files = cached_data['saved_files']
        validation_keys = cached_data['validation_keys']
        
        col1,col2=st.columns(2)
        with col1:
            ## Primary File box
            idx=getIndex(st.session_state.saved_data_map,schema,field,saved_files,"primary_file") # indexes currently mapped selection
            primary_file=st.selectbox("Primary File", # Box title
                                        saved_files, # displays the attributes per data source
                                        key=f"{schema}_{field}_primary_file", # streamlit global value (must be unique)
                                        index=idx) # load the existing mapping, index that option func
            ## Secondary File box
            idx=getIndex(st.session_state.saved_data_map,schema,field,saved_files,"secondary_file")
            secondary_file=st.selectbox("Secondary File",
                                        saved_files,
                                        key=f"{schema}_{field}_secondary_file",
                                        index=idx)
            ## Fallback Type box
            if not field_type:
                list_options=validation_keys  # Use cached validation keys
            else:
                list_options=["None",field_type]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"fallback_value_type")
            fallback_value_type=st.selectbox("Fallback Type",
                                        list_options,
                                        key=f"{schema}_{field}_fallback_value_type",
                                        index=idx)
        with col2:
            ## Primary Attributes box
            # Cache file attributes to avoid repeated list conversions
            primary_attrs_key = f"attrs_{primary_file}"
            if primary_attrs_key not in st.session_state:
                st.session_state[primary_attrs_key] = list(data_sources["files"][primary_file]["attributes"])
            
            list_options = st.session_state[primary_attrs_key]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"primary_attribute")
            primary_attribute=st.selectbox("Primary Attribute",
                                        list_options,
                                        key=f"{schema}_{field}_primary_attribute",
                                        index=idx)
            ## Secondary Attributes box
            secondary_attrs_key = f"attrs_{secondary_file}"
            if secondary_attrs_key not in st.session_state:
                st.session_state[secondary_attrs_key] = list(data_sources["files"][secondary_file]["attributes"])
            
            list_options = st.session_state[secondary_attrs_key]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"secondary_attribute")
            secondary_attribute=st.selectbox("Secondary Attribute",
                                        list_options,
                                        key=f"{schema}_{field}_secondary_attribute",
                                        index=idx)
            ## Fallback Value box
            if fallback_value_type=="None": # if none type, lock the fallback value box
                fallback_value=st.text_input("Fallback Value",
                                        disabled=True,
                                        key=f"{schema}_{field}_data_value_b")
            elif fallback_value_type=="boolean": # if boolean type, display true/false
                list_options=["True","False"] 
                idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"fallback_value")
                fallback_value=st.selectbox("Fallback Value",
                                        list_options,
                                        key=f"{schema}_{field}_data_value_a",
                                        index=idx)
            else: # if string type, display stored value as default
                try:
                    val=st.session_state.saved_data_map["mapping"][schema][field]["fallback_value"]
                except:
                    val=""
                fallback_value=st.text_input("Fallback Value",
                                             value=val,
                                             key=f"{schema}_{field}_data_value_c")
        data_map = saveFieldMapping(data_map,
                                    schema,
                                    field,
                                    primary_file,
                                    primary_attribute,
                                    secondary_file,
                                    secondary_attribute,
                                    fallback_value_type,
                                    fallback_value)
    return data_map

def sidebarMapping(view_customer,customer,data_map,user):
    toggle_state = st.toggle("",label_visibility="collapsed") # controls which data map shows (toggle saved/draft)
    if toggle_state:
        st.badge("Draft Mapping",color="red")
        if (not st.session_state.file_locked) or (view_customer!=customer):
            st.markdown("*No draft in progress*")
        elif view_customer==customer:
            draft_cache_key = f"draft_markdown_{customer}"
            # Only regenerate markdown if data has changed or cache doesn't exist
            if (draft_cache_key not in st.session_state or 
                st.session_state.get('data_map_changed', False) or
                st.session_state.get('force_sidebar_refresh', False)):
                
                st.session_state[draft_cache_key] = schemaToMarkdown(data_map)
                st.session_state['data_map_changed'] = False
                st.session_state['force_sidebar_refresh'] = False
                
            st.markdown(st.session_state[draft_cache_key],unsafe_allow_html=True)
    else: 
        st.badge("Saved Mapping",color="grey")
        cache_key = f"saved_mapping_{view_customer}"
        markdown_cache_key = f"saved_markdown_{view_customer}"
        
        if cache_key not in st.session_state:
            st.session_state[cache_key] = getCustomerDataMap(user,view_customer)
        
        if markdown_cache_key not in st.session_state:
            st.session_state[markdown_cache_key] = schemaToMarkdown(st.session_state[cache_key])
        
        st.markdown(st.session_state[markdown_cache_key],unsafe_allow_html=True)
