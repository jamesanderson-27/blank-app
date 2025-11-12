import os
import streamlit as st
from utilities.handle_markdown import styleButtons
from utilities.handle_github_data import getEntitiesSchema

def housekeeping():
    st.session_state.user="jamesanderson-27" # Change to generic CX user (when created)
    st.session_state.API_KEY=os.environ.get('API_KEY') # set in streamlit settings' secrets
    st.session_state.API_KEY_WRITE=os.environ.get('API_KEY_WRITE') # set in streamlit settings' secrets
    st.logo("DexCare_logo.jpg",size="large")
    styleButtons()
    setValidationConfig()
    if 'data_map_sha' not in st.session_state:
        st.session_state.data_map_sha=''
    if 'data_map_md_sha' not in st.session_state:
        st.session_state.data_map_md_sha=''
    if 'data_sources_sha' not in st.session_state:
        st.session_state.data_sources_sha=''
    if 'customer_locked' not in st.session_state:
        st.session_state.customer_locked = False
    if 'file_locked' not in st.session_state:
        st.session_state.file_locked = False
    if 'exclusion_list' not in st.session_state:
        st.session_state.exclusion_list=[]
    if 'saved_data_map' not in st.session_state:
        st.session_state.saved_data_map={}

@st.cache_data
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
        "vanityNumber",
        "isSmsEnabled",
        "notificationsEnabled",
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
        "departmentPrimaryId",
        "address.externalIdentifiers",
        "fax",
        "insurances.isReturningPatientEnabled",
        "insurances.isNewPatientEnabled",
        "insurances.externalIdentifiers",
        "phone.externalIdentifiers",
        "phone.isPrimary",
        "phone.isExternal"
    ]

@st.cache_data
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

def setValidationConfig():
    st.session_state.validation_config = {
    "string": {
        "validation": lambda x: isinstance(x, str),
        "default_fallback": ""
    },
    "boolean": {
        "validation": lambda x: x in ["True", "False", True, False],
        "default_fallback": "True"
    },
    "object": {
        "validation": lambda x: True,  # add JSON validation
        "default_fallback": "{}"
    },
    "array": {
        "validation": lambda x: True,  # add array validation
        "default_fallback": "[]"
    },
    "number": {
        "validation": lambda x: isinstance(x, (int, float)) or str(x).replace('.', '').isdigit(),
        "default_fallback": 0
    }
}
