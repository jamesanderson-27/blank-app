import streamlit as st

st.title("DexCare Data Mapping POC")
st.write("*This is a mockup populated with hardcoded values.*")

st.divider()

### HARDCODED DATA FOR POC
# Define your list of field names
schemas={
        "Provider":["emr_id","npi","name"],
        "Department":["display_name","emr_id","is_active","specialty"]
    }

field_names = [
               "display_name",
               "emr_id",
               "is_active",
               "specialty"
            ]

data_sources = {
                "":[],
                "Epic SER":["","emr_id","display_name","specialty","npi"],
                "Epic DEP":["","emr_id","display_name","specialty"],
                "CS_Providers":["","emrId","provider first name","provider last name","specialty","sub-specialties"],
                "CS_Departments":["","iuuid","department name","specialty"]
            }

data_types = [
            "string",
            "numerical",
            "boolean"
        ]   

## File Upload Activity
st.subheader("Upload Files")
st.write("File Requirements")
st.write("* format must be .json, .txt, or .csv")
st.write("* another requirement")

# File uploader
uploaded_file = st.file_uploader("Choose a file")

# Process the uploaded file
if uploaded_file is not None:
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size, "bytes")
    
    # Example: if it's a text file
    if uploaded_file.type == "text/plain":
        content = uploaded_file.read().decode("utf-8")
        st.text_area("File content", content, height=200)

for source in list(data_sources.keys())[1:]:
    st.markdown(f"File called **{source}** uploaded successfully. {int(len(data_sources[source]))} fields parsed.")

st.divider()

## Data Mapping Activity
st.subheader("DexCare Schema")

for schema in sorted(list(schemas.keys())):
    with st.expander(schema):
        for field in sorted(list(schemas[schema])):
            with st.expander(field):
                # Free text description
                st.write("**Description**")
                st.write("*This will be pulled dynamically from the DexCare Schema*")
                st.write("**Primary Source**")
                primary_data_source = st.selectbox("Source File",
                                            list(data_sources.keys()),
                                            key=f"{schema}_{field}_primary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                primary_data_col = st.selectbox("Attribute",
                                            list(data_sources[primary_data_source]),
                                            key=f"{schema}_{field}_primary_attribute",
                                            index=0) # load the existing mapping, index that option func
                st.write("**Secondary Source** (if primary attribute is null)")
                secondary_data_source = st.selectbox("Source File",
                                            list(data_sources.keys()),
                                            key=f"{schema}_{field}_secondary_dropdown",
                                            index=0) # load the existing mapping, index that option func
                secondary_data_col = st.selectbox("Attribute",
                                            list(data_sources[secondary_data_source]),
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

# Inject custom CSS to style the button
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
""", unsafe_allow_html=True)