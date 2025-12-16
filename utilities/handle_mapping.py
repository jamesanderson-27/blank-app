import streamlit as st
from utilities.handle_github_data import getCustomerDataMap,updateGithub
from utilities.handle_markdown import schemaToMarkdown

def _keep_expanders_open(schema, field):
    """Helper function to keep expanders open when dropdowns are interacted with"""
    if 'schema_expander_states' in st.session_state:
        schema_key = f"schema_{schema}"
        st.session_state.schema_expander_states[schema_key] = True
    
    if 'field_expander_states' in st.session_state:
        # Keep both nested field expander and individual field expander open
        field_key = f"field_{schema}_{field.split('.')[0]}"  # For nested fields
        individual_field_key = f"individual_field_{schema}_{field}"
        st.session_state.field_expander_states[field_key] = True
        st.session_state.field_expander_states[individual_field_key] = True

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
    if ("mapping" not in data_map or
        schema not in data_map["mapping"] or
        field not in data_map["mapping"][schema] or
        key not in data_map["mapping"][schema][field]):
        return 0
    value = data_map["mapping"][schema][field][key]
    if value in list_options:
        return list_options.index(value)
    else:
        return 0
    
def saveFieldMapping(data_map,schema,field,file_a,a_attribute,
                     file_b,b_attribute,file_c,c_attribute,
                     fallback_value_type,fallback_value,
                     notes,logic,conditional_1,conditional_2,
                     result_1,result_2):
    if "mapping" not in data_map:
        data_map["mapping"] = {}
    if schema not in data_map["mapping"]:
        data_map["mapping"][schema] = {}
    if field not in data_map["mapping"][schema]:
        data_map["mapping"][schema][field] = {}
    new_mapping = {
        "file_a": file_a or "",
        "a_attribute": a_attribute or "",
        "file_b": file_b or "",
        "b_attribute": b_attribute or "",
        "file_c": file_c or "",
        "c_attribute":c_attribute or "",
        "fallback_value_type": fallback_value_type or "None",
        "fallback_value": fallback_value or "None",
        "notes": notes or "",
        "logic": logic or "",
        "conditional_1": conditional_1 or "",
        "conditional_2": conditional_2 or "",
        "result_1": result_1 or "",
        "result_2": result_2 or ""
    }
    if data_map["mapping"][schema][field]!=new_mapping: # Only update if mapping has changed
        data_map["mapping"][schema][field]=new_mapping
        st.session_state['data_map_changed'] = True
    return data_map

def fieldMapper(field,data_sources,data_map,schema,description,field_type):
    # Get or set default expander state for individual field
    individual_field_key = f"individual_field_{schema}_{field}"
    if individual_field_key not in st.session_state.get('field_expander_states', {}):
        if 'field_expander_states' not in st.session_state:
            st.session_state.field_expander_states = {}
        st.session_state.field_expander_states[individual_field_key] = False
    
    with st.expander(f"{schema}.*{field}*", expanded=st.session_state.field_expander_states[individual_field_key]):                        # field (e.g. abbreviation, externalIdentifiers)
        st.code(description,language=None,wrap_lines=True)
        col1,col2=st.columns(2)
        with col1:
            ## A File box
            idx=getIndex(st.session_state.saved_data_map,schema,field,st.session_state.saved_files,"file_a") # indexes currently mapped selection
            file_a=st.selectbox("File A", # Box title
                                        st.session_state.saved_files, # displays the attributes per data source
                                        key=f"{schema}_{field}_file_a", # streamlit global value (must be unique)
                                        index=idx, # load the existing mapping, index that option func
                                        on_change=lambda: _keep_expanders_open(schema, field)) # Keep expanders open on selection
            ## B File box
            idx=getIndex(st.session_state.saved_data_map,schema,field,st.session_state.saved_files,"file_b")
            file_b=st.selectbox("File B",
                                        st.session_state.saved_files,
                                        key=f"{schema}_{field}_file_b",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
            ## C File box
            idx=getIndex(st.session_state.saved_data_map,schema,field,st.session_state.saved_files,"file_c")
            file_c=st.selectbox("File C",
                                        st.session_state.saved_files,
                                        key=f"{schema}_{field}_file_c",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
            ## Fallback Type box
            if  field_type:
                list_options=["None",field_type]
            else:
                list_options=["None","string"]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"fallback_value_type")
            fallback_value_type=st.selectbox("Fallback Type",
                                        list_options,
                                        key=f"{schema}_{field}_fallback_value_type",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
        with col2:
            ## A File Attributes box
            # Cache file attributes to avoid repeated list conversions
            a_attrs_key = f"attrs_{file_a}"
            if a_attrs_key not in st.session_state:
                st.session_state[a_attrs_key] = list(data_sources["files"][file_a]["attributes"])
            list_options = st.session_state[a_attrs_key]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"a_attribute")
            a_attribute=st.selectbox("A Attribute",
                                        list_options,
                                        key=f"{schema}_{field}_a_attribute",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
            ## B File Attributes box
            b_attrs_key = f"attrs_{file_b}"
            if b_attrs_key not in st.session_state:
                st.session_state[b_attrs_key] = list(data_sources["files"][file_b]["attributes"])
            list_options = st.session_state[b_attrs_key]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"b_attribute")
            b_attribute=st.selectbox("B Attribute",
                                        list_options,
                                        key=f"{schema}_{field}_b_attribute",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
            ## C File Attributes box
            c_attrs_key = f"attrs_{file_b}"
            if c_attrs_key not in st.session_state:
                st.session_state[c_attrs_key] = list(data_sources["files"][file_b]["attributes"])
            list_options = st.session_state[c_attrs_key]
            idx=getIndex(st.session_state.saved_data_map,schema,field,list_options,"c_attribute")
            c_attribute=st.selectbox("C Attribute",
                                        list_options,
                                        key=f"{schema}_{field}_c_attribute",
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
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
                                        index=idx,
                                        on_change=lambda: _keep_expanders_open(schema, field))
            else: # if string type, display stored value as default
                try:
                    val=st.session_state.saved_data_map["mapping"][schema][field]["fallback_value"]
                except:
                    val=""
                fallback_value=st.text_input("Fallback Value",
                                             value=val,
                                             key=f"{schema}_{field}_data_value_c")
        ## Below Fallback Type and Value
        notes=st.text_area("notes",key=f"{schema}_{field}_notes")
        st.divider()
        if st.toggle("Complex Logic (if left untoggled, will default to simple fallbacks)",key=f"{schema}_{field}_complex_bool"):
            logic="complex"
            st.write("*Use valid conditional statements e.g. 'IF A OR B' or 'IF A AND NOT (B OR C)'. If the conditional statement evaluates to true, the value in its corresponding result will be used.*")            
            col3,col4=st.columns(2)
            with col3:
                conditional_1=st.text_input("Conditional 1",key=f"{schema}_{field}_conditional_1")
                conditional_2=st.text_input("Conditional 2",key=f"{schema}_{field}_conditional_2")
            with col4:
                result_1=st.text_input("Result 1",key=f"{schema}_{field}_result_1")
                result_2=st.text_input("Result 2",key=f"{schema}_{field}_result_2")
        else:
            logic="simple"
            conditional_1,conditional_2,result_1,result_2="","","",""
        data_map = saveFieldMapping(data_map,
                                    schema,
                                    field,
                                    file_a,
                                    a_attribute,
                                    file_b,
                                    b_attribute,
                                    file_c,
                                    c_attribute,
                                    fallback_value_type,
                                    fallback_value,
                                    notes,
                                    logic,
                                    conditional_1,
                                    conditional_2,
                                    result_1,
                                    result_2)
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