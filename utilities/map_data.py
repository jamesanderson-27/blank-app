# Data mapper - these are called after the customer completes data mapping
import streamlit as st

def saveFieldMapping(data_map,schema,field,primary_source,primary_col,secondary_source,secondary_col,default_value):
    data_map["mapping"][schema][field]["primary_source"]=primary_source
    data_map["mapping"][schema][field]["primary_col"]=primary_col
    data_map["mapping"][schema][field]["secondary_source"]=secondary_source
    data_map["mapping"][schema][field]["secondary_col"]=secondary_col
    data_map["mapping"][schema][field]["default_value"]=default_value

    return data_map
    
def getIndex(data_map,object,field,attributes,data_source_type):
    # data_source_type either = primary_source_attribute or secondary_source_attribute
    # if the loaded data_map has a value for that attribute - source combo, use that
    try:
        value=data_map["mapping"][object][field][data_source_type]
        return attributes.index(value)
    # if it doesn't have a value for that attribute - source combo, use 0
    except:
        return 0
    
def lock():
    st.session_state.locked=True
    return 1
