import streamlit as st

st.title("DexCare Data Mapping POC")
st.divider()

# Define your list of field names
field_names = ["Provider.emr_id",
               "Provider.npi",
               "Provider.name",
               "Department.display_name",
               "Department.emr_id",
               "Department.is_active",
               "Department.specialty"
               ]

# Define dropdown options
data_sources = {"":[],
                "Epic SER":["","emr_id","display_name","specialty","npi"],
                "Epic DEP":["","emr_id","display_name","specialty"],
                "CS_Providers":["","emrId","provider first name","provider last name","specialty","sub-specialties"],
                "CS_Departments":["","iuuid","department name","specialty"],}

data_types=["string","numerical","boolean"]

# Loop through each field name
for field in field_names:
    st.header(field)

    # Free text description
    description = st.text_area("Description", key=f"{field}_description")

    st.badge("Primary Source", color="green")
    primary_data_source = st.selectbox("Source File",
                                  list(data_sources.keys()),
                                  key=f"{field}_primary_dropdown",
                                  index=0)
    primary_data_col = st.selectbox("Attribute",
                                  list(data_sources[primary_data_source]),
                                  key=f"{field}_primary_attribute",
                                  index=0)
    
    st.badge("Secondary Source", color="blue")
    secondary_data_source = st.selectbox("Source File",
                                  list(data_sources.keys()),
                                  key=f"{field}_secondary_dropdown",
                                  index=0)
    secondary_data_col = st.selectbox("Attribute",
                                  list(data_sources[secondary_data_source]),
                                  key=f"{field}_secondary_attribute",
                                  index=0)

    st.badge("Default", color="grey")
    data_type = st.selectbox("Data Type",
                                  data_types,
                                  key=f"{field}_data_type",
                                  index=0)
    default_value=st.text_input("Value",
                                key=f"{field}_data_value")

    st.divider()


