# Data mapper - these are called after the customer completes data mapping
import streamlit as st

def saveFieldMapping(data_map,object,field,primary_data_source,primary_data_col,secondary_data_source,secondary_data_col,default_value):
    data_map["mapping"][object]={
        field:{
            "primary_data_source":primary_data_source,
            "primary_data_col":primary_data_col,
            "secondary_data_source":secondary_data_source,
            "secondary_data_col":secondary_data_col,
            "default_value":default_value
        }
    }
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
    
