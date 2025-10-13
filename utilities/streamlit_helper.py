import streamlit as st
from utilities.load_github_data import getCustomerDataMap
    
def customerLock(user,customer=""):
    st.session_state.customer_locked=True
    data=getCustomerDataMap(user,customer,1)
    try:
        st.session_state.data_map_sha=data["sha"] # store the github file's sha
    except:
        pass

def fileLock():
    st.session_state.file_locked=True


def styleButtons():
    st.markdown("""
        <style>
        /* Target buttons using their class */
        div.stButton > button {
            background-color: #add8e6; /* Light blue */
            color: black;
            border: none;
            padding: 0.5em 1em;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            background-color: #87ceeb; /* Sky blue on hover */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transform: translateY(-2px);
        }

        div.stButton > button:active {
            background-color: #4682b4; /* Steel blue on click */
            transform: translateY(1px);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)

def getIndex(data_map,object,field,attributes,data_source_type):
    # data_source_type either = primary_source_attribute or secondary_source_attribute
    # if the loaded data_map has a value for that attribute - source combo, use that
    try:
        value=data_map["mapping"][object][field][data_source_type]
        return attributes.index(value)
    # if it doesn't have a value for that attribute - source combo, use 0
    except:
        return 0
    
def saveFieldMapping(data_map,schema,field,primary_source,primary_col,secondary_source,secondary_col,default_value):
    if field not in data_map["mapping"][schema]:
        data_map["mapping"][schema][field]={}
    data_map["mapping"][schema][field]["primary_source"]=primary_source
    data_map["mapping"][schema][field]["primary_col"]=primary_col
    data_map["mapping"][schema][field]["secondary_source"]=secondary_source
    data_map["mapping"][schema][field]["secondary_col"]=secondary_col
    data_map["mapping"][schema][field]["default_value"]=default_value

    return data_map

def fieldMapper(field,data_sources,data_map,schema):
    with st.expander(field):
        st.write("**Description**")
        st.write("*This will be pulled dynamically from the DexCare Schema*")
        attributes=data_sources.keys()
        st.write("**Primary Source**")
        index=getIndex(data_map,schema,field,attributes,"primary_source_attribute")
        primary_source = st.selectbox("Source File",
                                    list(attributes),
                                    key=f"{schema}_{field}_primary_dropdown",
                                    index=index) # load the existing mapping, index that option func
        index=getIndex(data_map,schema,field,attributes,"primary_col")
        primary_col = st.selectbox("Attribute",
                                    list(data_sources[primary_source]["attributes"]),
                                    key=f"{schema}_{field}_primary_attribute",
                                    index=index) # load the existing mapping, index that option func
        st.write("**Secondary Source** (if primary attribute is null)")
        index=getIndex(data_map,schema,field,attributes,"secondary_source_attribute")
        secondary_source = st.selectbox("Source File",
                                    list(attributes),
                                    key=f"{schema}_{field}_secondary_dropdown",
                                    index=index) # load the existing mapping, index that option func
        index=getIndex(data_map,schema,field,attributes,"secondary_col")
        secondary_col = st.selectbox("Attribute",
                                    list(data_sources[secondary_source]["attributes"]),
                                    key=f"{schema}_{field}_secondary_attribute",
                                    index=index) # load the existing mapping, index that option func
        st.write("**Default** (if primary & secondary attributes are null)")
        default_value=st.text_input("Value",key=f"{schema}_{field}_data_value")
        data_map = saveFieldMapping(data_map,
                                    schema,
                                    field,
                                    primary_source,
                                    primary_col,
                                    secondary_source,
                                    secondary_col,
                                    default_value)
    return data_map