
# convert mapping to markdown
import streamlit as st

def schemaToMarkdown(data_map): ## Chat GPT credit
    md = []
    try:
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
                formatted_values = [f"``" if v is None else f"`{v}`" for v in values]
                md.append("| " + " | ".join(formatted_keys) + " |")
                md.append("|" + ":-------:|" * len(formatted_keys))
                md.append("| " + " | ".join(formatted_values) + " |")
                md.append("")  # Blank line after table

        return "\n".join(md)
    except:
        return "Could not load markdown: schemaToMarkdown failure."


def styleButtons():
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