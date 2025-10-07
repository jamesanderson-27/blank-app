
# convert mapping to markdown

def schemaToMarkdown(data_map):

    markdown="""
                ### Current Schema Mapping 

                **Department**
                - display_name
                    - primary = DataSource.Attribute
                    - secondary = 
                    - default = 
                - emr_id
                    - primary = DataSource.Attribute
                    - secondary = 
                    - default = DataSource.Attribute

                ***

                **Provider**
                - emr_id
                    - primary = DataSource.Attribute
                    - secondary = DataSource.Attribute
                    - default = 
                - npi
                    - primary = DataSource.Attribute
                    - secondary = 
                    - default = 
                - name
                    - primary = DataSource.Attribute
                    - secondary = 
                    - default = 
                """
    return markdown

