from deep_report_state import Section


def get_config_value(value):
    """
    Helper function to handle both string and enum cases of configuration values
    """
    return value if isinstance(value, str) else value.value


def format_sections(sections: list[Section]) -> str:
    """ Format a list of sections into a string """
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
{'=' * 60}
Section {idx}: {section.nome}
{'=' * 60}
Description:
{section.descrizione}
Requires Research: 
{section.ricerca}

Content:
{section.contenuto if section.contenuto else '[Not yet written]'}

"""
    return formatted_str
