
# convert mapping to markdown
import streamlit as st

def schemaToMarkdown(data_map,customer):
    md = []
    if customer:
        mapping = data_map.get("mapping", {})
        for category, fields in mapping.items():
            md.append(f"## {category}") # category is schema name (e.g. Provider)
            
            for field_name, field_data in fields.items():
                md.append(f"\n")
                md.append(f"**{category}.{field_name}**")

                # Build 2x6 table for body
                keys = list(field_data.keys())
                values = list(field_data.values())
                formatted_keys = [f"*<span style='font-size:12px; font-style:italic; font-weight:normal;'>{k.replace('_', ' ').title()}</small>*" for k in keys]
                formatted_values = [f"`null`" if v is None else f"`{v}`" for v in values]

                
                md.append("| " + " | ".join(formatted_keys) + " |")
                md.append("|" + ":-------:|" * len(formatted_keys))
                md.append("| " + " | ".join(formatted_values) + " |")
                md.append("")  # Blank line after table

    return "\n".join(md)


