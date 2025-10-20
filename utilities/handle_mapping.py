import streamlit as st
from utilities.handle_github_data import getCustomerDataMap
from utilities.handle_markdown import schemaToMarkdown
    
def customerLock(user,customer=""):
    st.session_state.customer_locked=True
    try:
        data=getCustomerDataMap(user,customer,1) # calls to a customer/data_map.json
        st.session_state.data_map_sha=data["sha"] # stores the sha of the github file for later use
    except:
        pass

def fileLock():
    st.session_state.file_locked=True
    # update customer/data_sources.json (TO DO)

def getIndex(data_map,object,field,attributes,data_source_type):
    try:
        value=data_map["mapping"][object][field][data_source_type]
        return attributes.index(value)
    except:
        return 0
    
def saveFieldMapping(data_map,schema,field,primary_source,primary_attribute,secondary_source,secondary_attribute,fallback_value_type,fallback_value):
    if field not in data_map["mapping"][schema]:
        data_map["mapping"][schema][field]={}
    data_map["mapping"][schema][field]["primary_file"]=primary_source
    data_map["mapping"][schema][field]["primary_attribute"]=primary_attribute
    data_map["mapping"][schema][field]["secondary_file"]=secondary_source
    data_map["mapping"][schema][field]["secondary_attribute"]=secondary_attribute
    data_map["mapping"][schema][field]["fallback_value_type"]=fallback_value_type
    data_map["mapping"][schema][field]["fallback_value"]=fallback_value
    return data_map

def fieldMapper(field,data_sources,data_map,schema):
    with st.expander(f"{schema}.*{field}*"): # schema field name; e.g. abbreviation, externalIdentifiers, etc...
        attributes=data_sources["files"].keys()
        col1,col2=st.columns(2)
        index=0
        with col1:
            #index=getIndex(data_map,schema,field,attributes,"primary_source") # indexes currently mapped selection
            primary_source=st.selectbox("Primary File",
                                        list(attributes), # displays the attributes per data source
                                        key=f"{schema}_{field}_primary_source", # streamlit global value (must be unique)
                                        index=index) # load the existing mapping, index that option func
            #index=getIndex(data_map,schema,field,attributes,"secondary_source")
            secondary_source=st.selectbox("Secondary File",
                                        list(attributes),
                                        key=f"{schema}_{field}_secondary_source",
                                        index=index)
            #index=getIndex(data_map,schema,field,attributes,"fallback_value_type")
            fallback_value_type=st.selectbox("Fallback Type",
                                        ["None","String","Boolean"],
                                        key=f"{schema}_{field}_fallback_value_type",
                                        index=index)
        with col2:
            #index=getIndex(data_map,schema,field,attributes,"primary_attribute")
            primary_attribute=st.selectbox("Primary Attribute",
                                        list(data_sources["files"][primary_source]["attributes"]),
                                        key=f"{schema}_{field}_primary_attribute",
                                        index=index) # load the existing mapping, index that option func
            #index=getIndex(data_map,schema,field,attributes,"secondary_attribute")
            secondary_attribute=st.selectbox("Secondary Attribute",
                                        list(data_sources["files"][secondary_source]["attributes"]),
                                        key=f"{schema}_{field}_secondary_attribute",
                                        index=index) # load the existing mapping, index that option func
            #index=getIndex(data_map,schema,field,attributes,"fallback_value")
            if fallback_value_type=="Boolean":
                fallback_value=st.selectbox("Fallback Value",
                                        ["True","False"],
                                        key=f"{schema}_{field}_data_value_a",
                                        index=index)
            if fallback_value_type=="None":
                fallback_value=st.selectbox("Fallback Value",
                                        [None],
                                        disabled=True,
                                        key=f"{schema}_{field}_data_value_b",
                                        index=index)
            if fallback_value_type=="String":
                fallback_value=st.text_input("Fallback Value",key=f"{schema}_{field}_data_value_c")
        data_map = saveFieldMapping(data_map,
                                    schema,
                                    field,
                                    primary_source,
                                    primary_attribute,
                                    secondary_source,
                                    secondary_attribute,
                                    fallback_value_type,
                                    fallback_value)
    return data_map

def sidebarMapping(view_customer,customer,data_map):
    toggle_state = st.toggle("",label_visibility="collapsed") # controls which data map shows (toggle current/draft)
    if toggle_state:
        st.badge("Draft Mapping",color="red")
        if not st.session_state.file_locked:
            st.markdown("*No draft in progress*")
            pass
        elif view_customer==customer:
            st.markdown(schemaToMarkdown(data_map),unsafe_allow_html=True)
        else:
            st.markdown(schemaToMarkdown(st.session_state[f"{view_customer}_current_data_map"]),unsafe_allow_html=True)
    else: 
        st.badge("Current Mapping",color="grey")
        st.markdown(schemaToMarkdown(st.session_state[f"{view_customer}_current_data_map"]),unsafe_allow_html=True)
