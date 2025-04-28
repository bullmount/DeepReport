from typing import List, Tuple, Optional

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


def estrai_sezioni_markdown_e_indice_assegnata(tutte_le_sezioni: List[Section],
                                               sezione_assegnata: Optional[Section] = None,
                                               include_assegnata: bool = False) -> Tuple[int, str]:
    markdown_lines = []
    indice_assegnata = None

    for i, sezione in enumerate(tutte_le_sezioni, start=1):
        if sezione_assegnata and sezione.nome == sezione_assegnata.nome and sezione.descrizione == sezione_assegnata.descrizione:
            indice_assegnata = i
            if not include_assegnata:
                continue
        markdown_lines.append(f"**Sezione numero {i}**\nTitolo: {sezione.nome}\nDescrizione: {sezione.descrizione}")

    markdown_output = "\n\n".join(markdown_lines)
    return indice_assegnata, markdown_output


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
