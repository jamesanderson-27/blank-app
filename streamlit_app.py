import streamlit as st
from utilities.handle_files import handleFiles
from utilities.map_data import saveFieldMapping,getIndex
from utilities.load_github_data import getCustomerList,getEntitiesSchema,getCustomerDataMap
from streamlit_markmap import markmap
import re
import streamlit.components.v1 as components

st.title("DexCare Data Mapping") 

####### Customer Selection Activity #######
st.subheader("Select Customer")

user="jamesanderson-27" # will change to generic user
auth_token=""# needed for private repos / better rate limits

customer_list=getCustomerList(user,auth_token) # requests github for current customers
customer=st.selectbox("Customer",customer_list,key="customer",index=0)

st.divider()


####### Customer Load #######
data_sources={ # keep "" dict as dropdown placeholder
        "":{
            "uploaded_at":"",
            "file_type":"",
            "attributes":[]
        }
    }

if customer:
    data_map = getCustomerDataMap(user,auth_token,customer) # pull existing data_map
    st.write(data_map)


####### Schema Load #######
schemas={
        "Provider":["emr_id","npi","name"],
        "Department":["display_name","emr_id"]
    }


####### File Upload Activity #######
st.subheader("Upload Files")

uploaded_files = st.file_uploader(
    "Choose one or more files",
    type=['csv', 'txt','json'],
    accept_multiple_files=True
)

data_sources=handleFiles(uploaded_files,data_sources)
for file in list(data_sources.keys())[1:]:
    n_attributes=len(data_sources[file]["attributes"])
    st.write(f"*{file}* has {n_attributes} attributes.")

# store file and attribute data in data_sources

st.divider()


####### Data Mapping Activity #######
st.subheader("Map to DexCare Schema")

#try:
    #ass #load data map
#except:
    #data_map={} # instatiate new data map
data_map={
    "last_modified_time":"",
    "last_modified_user":"",
    "schema":{}
}
    

for schema in sorted(list(schemas.keys())):
    with st.expander(schema):
        for field in sorted(list(schemas[schema])):
            with st.expander(field):
                st.write("**Description**")
                st.write("*This will be pulled dynamically from the DexCare Schema*")
                
                attributes=data_sources.keys()

                st.write("**Primary Source**")
                index=getIndex(data_map,field,attributes,"primary_source_attribute")
                primary_data_source = st.selectbox("Source File",
                                            list(attributes),
                                            key=f"{schema}_{field}_primary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                primary_data_col = st.selectbox("Attribute",
                                            list(data_sources[primary_data_source]["attributes"]),
                                            key=f"{schema}_{field}_primary_attribute",
                                            index=0) # load the existing mapping, index that option func
                st.write("**Secondary Source** (if primary attribute is null)")
                index=getIndex(data_map,field,attributes,"secondary_source_attribute")
                secondary_data_source = st.selectbox("Source File",
                                            list(attributes),
                                            key=f"{schema}_{field}_secondary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                secondary_data_col = st.selectbox("Attribute",
                                            list(data_sources[secondary_data_source]["attributes"]),
                                            key=f"{schema}_{field}_secondary_attribute",
                                            index=0) # load the existing mapping, index that option func
                st.write("**Default** (if primary & secondary attributes are null)")
                default_value=st.text_input("Value",
                                            key=f"{schema}_{field}_data_value")
            data_map=saveFieldMapping(data_map,
                                    field,
                                    primary_data_source,
                                    primary_data_col,
                                    secondary_data_source,
                                    secondary_data_col,
                                    default_value)  ## Save field mapping to data_map

if st.button("Save Mapping to GitHub",key="data_map_save"):
        st.success(f"Data mapping uploaded to repo")
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

# To fix later
# 1. The steps must be completed in order
    # if you upload more files after partially completing mapping steps
    # your mapping will be wiped out.

markdown="""
[Provider](##Provider)
- [emr_id](###emr_id)
- [test](###test)
## Provider
### emr_id
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value
### npi
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value
### npi
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value
### npi
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value
### npi
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value
### test
- Primary: data_source.attribute
- Secondary: data_source.attribute
- Default: default_value

"""

import streamlit as st
import pandas as pd

# --- Sample data ---
data = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Diana", "Edward"],
    "role": ["Engineer", "Designer", "Engineer", "Manager", "Engineer"],
    "location": ["NY", "CA", "TX", "NY", "CA"]
})

# --- Sidebar ---
with st.sidebar:
    st.header("🔍 Search for a schema field")
    # Field to search
    search_field = st.selectbox("Select a schema object:", data.columns.tolist())
    # Get unique values in that field
    field_values = data[search_field].dropna().astype(str).unique().tolist()
    # Free text input (not filtered yet)
    search_text = st.text_input("Start typing...")
    # Filter suggestions based on input
    suggestions = [v for v in field_values if search_text.lower() in v.lower()] if search_text else []
    # Show suggestions in a selectbox if any
    selected_value = st.selectbox("Suggestions", suggestions) if suggestions else None
    # Show results
    if selected_value:
        results = data[data[search_field].astype(str).str.lower() == selected_value.lower()]
        st.markdown("### 🔎 Match Found:")
        for i, row in results.iterrows():
            st.markdown(f"- **{row['name']}** — {row['role']} ({row['location']})")
    elif search_text:
        st.info("No exact match selected yet. Start typing to see suggestions.")



