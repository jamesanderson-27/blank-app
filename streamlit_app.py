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

data_sources = {"":[],
                "Epic SER":["","emr_id","display_name","specialty","npi"],
                "Epic DEP":["","emr_id","display_name","specialty"],
                "CS_Providers":["","emrId","provider first name","provider last name","specialty","sub-specialties"],
                "CS_Departments":["","iuuid","department name","specialty"]
            }

data_types=["string",
            "numerical",
            "boolean"
        ]

## File Upload Activity
st.subheader("Upload Files")
st.write("*In the final state, the user will upload the source files.*")

for source in list(data_sources.keys())[1:]:
    st.markdown(f"File called **{source}** uploaded successfully. {int(len(data_sources[source]))} fields parsed.")

st.divider()

## Data Mapping Activity
st.subheader("DexCare Schema")

for schema in list(schemas.keys()):
    with st.expander(schema):
        for field in list(schemas[schema]):
            with st.expander(field):
                # Free text description
                description = st.text_area("Description", key=f"{schema}_{field}_description")
                st.write("**Primary Source**")
                primary_data_source = st.selectbox("Source File",
                                            list(data_sources.keys()),
                                            key=f"{schema}_{field}_primary_dropdown",
                                            index=0)
                primary_data_col = st.selectbox("Attribute",
                                            list(data_sources[primary_data_source]),
                                            key=f"{schema}_{field}_primary_attribute",
                                            index=0)
                st.write("**Secondary Source** (if the primary attribute is null)")
                secondary_data_source = st.selectbox("Source File",
                                            list(data_sources.keys()),
                                            key=f"{schema}_{field}_secondary_dropdown",
                                            index=0)
                secondary_data_col = st.selectbox("Attribute",
                                            list(data_sources[secondary_data_source]),
                                            key=f"{schema}_{field}_secondary_attribute",
                                            index=0)
                st.write("**Default** (if the primary & secondary attributes are null)")
                data_type = st.selectbox("Data Type",
                                            data_types,
                                            key=f"{schema}_{field}_data_type",
                                            index=0)
                default_value=st.text_input("Value",
                                            key=f"{schema}_{field}_data_value")


