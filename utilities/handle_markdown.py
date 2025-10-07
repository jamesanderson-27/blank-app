
# convert mapping to markdown

def schemaToMarkdown(data_map):

    markdown = ""
    for entity, fields in data_map.items():
        markdown += f"## {entity}\n"
        for field in fields:
            markdown += f"- {field}\n"
        markdown += "\n"
    return markdown

