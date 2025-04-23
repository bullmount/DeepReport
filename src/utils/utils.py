from deep_report_state import Section
from datetime import datetime
import locale

def get_current_date():
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    # return datetime.now().strftime("%B %d, %Y")
    return datetime.now().strftime("%d %B %Y")

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
{section.contenuto if section.contenuto else '[Non ancora scritto]'}

"""
    return formatted_str
