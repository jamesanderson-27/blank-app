import os
import streamlit as st
from utilities.handle_files import handleFiles
from utilities.handle_markdown import schemaToMarkdown
from utilities.map_data import saveFieldMapping,getIndex
from utilities.load_github_data import getCustomerList,getCustomerDataMap

user,auth_token="jamesanderson-27",os.environ.get('API_KEY') # AUTH_KEY is a github pat

####### View Customer Siderbar #######
with st.sidebar:
    st.title("View Customer Mapping")
    customer_list=getCustomerList(user,auth_token)
    try:
        idx=customer_list.index(view_customer)
    except:
        idx=0
    view_customer=st.selectbox("Select Customer",
                customer_list,
                key="view_customer",
                index=idx)
    st.divider()
    data_map = getCustomerDataMap(user,auth_token,view_customer) # calls customers/customer/data_map.json

####### Edit Customer Main #######
st.subheader("Edit Customer Mapping")
customer=st.selectbox("Select Customer",
                    customer_list,
                    key="customer",
                    index=0)

####### Schema Load #######
schemas={ # will be replaced when pulling schema dynamically
        "Provider":["emr_id","npi","name"],
        "Department":["display_name","emr_id"]
    }

####### Customer Load #######
data_sources={ # null key serves as dropdown default selection
        "":{
            "uploaded_at":"",
            "file_type":"",
            "attributes":[]
        }
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
                default_value=st.text_input("Value",key=f"{schema}_{field}_data_value")
                data_map=saveFieldMapping(data_map,
                                schema,
                                field,
                                primary_source,
                                primary_col,
                                secondary_source,
                                secondary_col,
                                default_value)  ## Save field mapping to data_map

if st.button("Save Mapping"):
        st.badge("Data mapping uploaded to GitHub.",color="blue")
        # response = updateGithub(user,auth_token,customer,"data_map",data_map)
        # update customer/data_map.md
        # update customer/data_sources.json

st.session_state[f"{customer}_data_map"]=data_map

with st.sidebar:
    try:
        if view_customer:
            st.markdown(schemaToMarkdown(st.session_state[f"{view_customer}_data_map"],view_customer),unsafe_allow_html=True)
        else:
            st.markdown("*Select a customer to view current mapping*")
    except:
        if view_customer and not customer: # view customer selected, edit customer unselected
            data_map = getCustomerDataMap(user,auth_token,view_customer) # want to display different data_maps
            st.markdown(schemaToMarkdown(data_map,view_customer),unsafe_allow_html=True)
        elif view_customer and (view_customer!=customer): # both customers selected
            data_map = getCustomerDataMap(user,auth_token,view_customer) # want to display different data_maps
            st.markdown(schemaToMarkdown(data_map,customer),unsafe_allow_html=True)
        elif view_customer and (view_customer==customer):# both customers selected
            st.markdown(schemaToMarkdown(data_map,customer),unsafe_allow_html=True) # want to display same data_map
        else:
            st.markdown("*Select a customer to view current mapping*")

## Style buttons

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