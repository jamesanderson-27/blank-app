
# convert mapping to markdown

def schemaToMarkdown(data_map,customer):
    md = []
    if customer:
        md.append(f"# {customer.upper()} Mapping\n")
        mapping = data_map.get("mapping", {})
        for category, fields in mapping.items():
            md.append("---")
            md.append(f"## {category}")
            
            for field_name, field_data in fields.items():
                md.append(f"\n")
                md.append(f"**{category}.{field_name}**")

                # Build 2x6 table: one row for keys, one for values
                keys = list(field_data.keys())
                values = list(field_data.values())
                # Convert to title case and format keys
                formatted_keys = [f"*<span style='font-size:12px; font-style:italic; font-weight:normal;'>{k.replace('_', ' ').title()}</small>*" for k in keys]
                formatted_values = [f"`null`" if v is None else f"`{v}`" for v in values]

                # Header row
                md.append("| " + " | ".join(formatted_keys) + " |")
                # Divider row
                md.append("|" + ":-------:|" * len(formatted_keys))
                # Value row
                md.append("| " + " | ".join(formatted_values) + " |")
                md.append("")  # Blank line after table
    else:
        md.append(f"*Select a customer to view current mapping* \n")

    return "\n".join(md)


