import os
import streamlit as st
from utilities.handle_markdown import styleButtons
from utilities.handle_github import getEntitiesSchema

def housekeeping():
    st.session_state.user="jamesanderson-27" # Change to generic CX user (when created)
    st.session_state.API_KEY=os.environ.get('API_KEY') # set in streamlit settings' secrets
    st.session_state.API_KEY_WRITE=os.environ.get('API_KEY_WRITE') # set in streamlit settings' secrets
    st.set_page_config(layout="wide")
    st.logo("DexCare_logo.jpg",size="large")
    styleButtons()
    if 'data_map_sha' not in st.session_state:
        st.session_state.data_map_sha=''
    if 'data_sources_sha' not in st.session_state:
        st.session_state.data_sources_sha=''
    if 'customer_locked' not in st.session_state:
        st.session_state.customer_locked = False
    if 'file_locked' not in st.session_state:
        st.session_state.file_locked = False
    if 'saved_data_map' not in st.session_state:
        st.session_state.saved_data_map={}

<<<<<<< HEAD
def createExclusion():
    st.session_state.exclusion_list=[
        "adventCustom",
        "businessLineName",
        "businessUnitName",
        "visitTypes",
        "visitTypeOverrides",
        "visitTypeDepartmentOverrides",
        "address.externalIdentifiers",
        "cmsContent.sections",
        "phone.vanityNumber",
        "phone.isSmsEnabled",
        "phone.notificationsEnabled",
        "policies.externalIdentifiers",
        "ratingDistribution",
        "specialties.externalIdentifiers",
        "exclusionVisitTypeListMdm",
        "excludedVisitTypes",
        "extended",
        "brandRefs",
        "departments",
        "careTeamClinicianIdentifiers",
        "careTeamIds",
        "departmentIds",
        "departmentPrimaryId"
    ]

def loadSchemas():
    schemas={
            "Provider":{
                "file_name":"clinicianIngest.json",
                "field_names":{}
            },                 
            "Department":{
                "file_name":"departmentIngest.json",
                "field_names":{}
            },
            "Location":{
                "file_name":"locationIngest.json",
                "field_names":{}
            }
        }
    createExclusion()
    schemas=getEntitiesSchema(schemas,st.session_state.exclusion_list)
    return schemas
=======
def getIndex(data_map,schema,field,attributes,data_source_type):
    try:
        value=data_map["mapping"][schema][field][data_source_type]
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
            index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"primary_source") # indexes currently mapped selection
            primary_source=st.selectbox("Primary File",
                                        list(attributes), # displays the attributes per data source
                                        key=f"{schema}_{field}_primary_source", # streamlit global value (must be unique)
                                        index=index) # load the existing mapping, index that option func
            index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"secondary_source")
            secondary_source=st.selectbox("Secondary File",
                                        list(attributes),
                                        key=f"{schema}_{field}_secondary_source",
                                        index=index)
            #index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"fallback_value_type")
            fallback_value_type=st.selectbox("Fallback Type",
                                        ["None","String","Boolean"],
                                        key=f"{schema}_{field}_fallback_value_type",
                                        index=index)
        with col2:
            index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"primary_attribute")
            primary_attribute=st.selectbox("Primary Attribute",
                                        list(data_sources["files"][primary_source]["attributes"]),
                                        key=f"{schema}_{field}_primary_attribute",
                                        index=index) # load the existing mapping, index that option func
            index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"secondary_attribute")
            secondary_attribute=st.selectbox("Secondary Attribute",
                                        list(data_sources["files"][secondary_source]["attributes"]),
                                        key=f"{schema}_{field}_secondary_attribute",
                                        index=index) # load the existing mapping, index that option func
            #index=getIndex(st.session_state.saved_data_map,schema,field,attributes,"fallback_value")
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

def sidebarMapping(view_customer,customer,data_map,user):
    toggle_state = st.toggle("",label_visibility="collapsed") # controls which data map shows (toggle current/draft)
    if toggle_state:
        st.badge("Draft Mapping",color="red")
        if not st.session_state.file_locked:
            st.markdown("*No draft in progress*")
            st.write("a")
        elif view_customer!=customer:
            st.markdown(schemaToMarkdown(getCustomerDataMap(user,view_customer)),unsafe_allow_html=True)
            st.write("b")
        elif view_customer==customer:
            st.markdown(schemaToMarkdown(data_map),unsafe_allow_html=True)
            st.write("c")
    else: 
        st.badge("Saved Mapping",color="grey")
        st.markdown(schemaToMarkdown(getCustomerDataMap(user,view_customer)),unsafe_allow_html=True)
        st.write("d")
>>>>>>> e1ba637c1339214eb6596770902f00626bcdbe4f
