# Data mapper - these are called after the customer completes data mapping

def saveFieldMapping(data_map,field,primary_data_source,primary_data_col,secondary_data_source,secondary_data_col,default_value):
    data_map["schema"][field]={
        "primary_data_source":primary_data_source,
        "primary_data_col":primary_data_col,
        "secondary_data_source":secondary_data_source,
        "secondary_data_col":secondary_data_col,
        "default_value":default_value
    }
    return data_map
