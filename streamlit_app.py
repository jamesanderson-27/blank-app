import streamlit as st
import os
from utilities.handle_files import handleFiles
from utilities.map_data import saveFieldMapping,getIndex
from utilities.load_github_data import getCustomerList,getCustomerDataMap
from utilities.handle_markdown import schemaToMarkdown
st.title("DexCare Data Mapping") 

####### Customer Selection #######
st.subheader("Select Customer")
user,auth_token="jamesanderson-27",os.environ.get('API_KEY')
customer_list=getCustomerList(user,auth_token) # API_KEY set in Streamlit app's settings
customer=st.selectbox("Customer",
                      customer_list,
                      key="customer",
                      index=0) # Displays those customers in a dropdown
st.divider()

####### Customer Load #######
data_sources={ # null key serves as dropdown default selection
        "":{
            "uploaded_at":"",
            "file_type":"",
            "attributes":[]
        }
    }

data_map = getCustomerDataMap(user,auth_token,customer) # pulls existing data_map or returns blank map

####### Schema Load #######
schemas={ # will be replaced when pulling schema dynamically
        "Provider":["emr_id","npi","name"],
        "Department":["display_name","emr_id"]
    }

####### File Upload #######
st.subheader("Upload Files")
uploaded_files = st.file_uploader("Choose one or more files",
                                  type=['csv', 'txt','json'],
                                  accept_multiple_files=True)
data_sources=handleFiles(uploaded_files,data_sources) # reads file and extracts attributes
for file in list(data_sources.keys())[1:]: # skips null key
    n_attributes=len(data_sources[file]["attributes"]) # counts attributes per file
    st.write(f"*{file}* has {n_attributes} attributes.") # writes to screen
st.divider()


####### Data Mapping #######
st.subheader("Map to DexCare Schema")
for schema in sorted(list(schemas.keys())):
    data_map["mapping"][schema]={}
    with st.expander(schema):
        for field in sorted(list(schemas[schema])):
            data_map["mapping"][schema][field]={}
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
                default_value=st.text_input("Value",
                                            key=f"{schema}_{field}_data_value")
                data_map=saveFieldMapping(data_map,
                                schema,
                                field,
                                primary_source,
                                primary_col,
                                secondary_source,
                                secondary_col,
                                default_value)  ## Save field mapping to data_map
if st.button("Save Mapping to GitHub",key="data_map_save"):
        st.success(f"Data mapping uploaded to repo")
        # update customer/data_map.json
        # update customer/data_map.md
        # update customer/data_sources.json
        st.write(data_map)

st.markdown(""" 
    <style>
    div.stButton > button {
        background-color: #007BFF;color: white;padding: 10px 24px;
        font-size: 16px;border: none;border-radius: 5px;
    } 
            div.stButton > button:hover {
        background-color: #0056b3;color: white;}
    </style>
""", unsafe_allow_html=True)

####### Sidebar Markdown 
with st.sidebar:
    st.markdown(schemaToMarkdown(data_map,customer),unsafe_allow_html=True)

