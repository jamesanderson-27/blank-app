import streamlit as st
from utilities.handle_files import handleFiles

st.title("DexCare Data Mapping POC") 
st.write("*This is a mockup populated with hardcoded values.*")
st.divider()


####### Hardcoded data for POC #######
schemas={
        "Provider":["emr_id","npi","name"],
        "Department":["display_name","emr_id","is_active","specialty"]
    }
data_sources={ # will be populated with data during file loading, keep "" dict as dropdown placeholder
    "files":{
         "":{
            "uploaded_at":"",
            "attributes":[]
        }
    }
}
data_types = [
            "string",
            "numerical",
            "boolean"
        ]


####### File Upload Activity #######
st.subheader("Upload Files")

uploaded_files = st.file_uploader(
    "Choose one or more files",
    type=['csv', 'txt','json'],
    accept_multiple_files=True
)

data_sources_local=handleFiles(uploaded_files,data_sources)
st.write(data_sources_local)


# ingest file

# parse attributes

# store file and attribute data in data_sources

st.divider()


####### Data Mapping Activity #######
st.subheader("DexCare Schema")

for schema in sorted(list(schemas.keys())):
    with st.expander(schema):
        for field in sorted(list(schemas[schema])):
            with st.expander(field):
                st.write("**Description**")
                st.write("*This will be pulled dynamically from the DexCare Schema*")
                st.write("**Primary Source**")
                primary_data_source = st.selectbox("Source File",
                                            list(data_sources["files"].keys()),
                                            key=f"{schema}_{field}_primary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                primary_data_col = st.selectbox("Attribute",
                                            list(data_sources["files"][primary_data_source]["attributes"]),
                                            key=f"{schema}_{field}_primary_attribute",
                                            index=0) # load the existing mapping, index that option func
                st.write("**Secondary Source** (if primary attribute is null)")
                secondary_data_source = st.selectbox("Source File",
                                            list(data_sources["files"].keys()),
                                            key=f"{schema}_{field}_secondary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                secondary_data_col = st.selectbox("Attribute",
                                            list(data_sources["files"][secondary_data_source]["attributes"]),
                                            key=f"{schema}_{field}_secondary_attribute",
                                            index=0) # load the existing mapping, index that option func
                st.write("**Default** (if primary & secondary attributes are null)")
                data_type = st.selectbox("Data Type",
                                            data_types,
                                            key=f"{schema}_{field}_data_type",
                                            index=0) # load the existing mapping, index that option func
                default_value=st.text_input("Value",
                                            key=f"{schema}_{field}_data_value")

if st.button("Save"):
        st.success("Data mapping uploaded to github/repo/output")

st.markdown(""" 
    <style>
    div.stButton > button {
        background-color: #007BFF;
        color: white;
        padding: 10px 24px;
        font-size: 16px;
        border: none;
        border-radius: 5px;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    </style>
""", unsafe_allow_html=True) # Inject custom CSS to style the button