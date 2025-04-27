import demjson3
from typing import Type, TypeVar, Optional, Union, Dict, Any, List
from pydantic import BaseModel
import re
import json
import ast

T = TypeVar('T', bound=BaseModel)

def escape_newlines_in_quotes(s: str) -> str:
    pattern = re.compile(r'(?<!\\)"((?:[^"\\]|\\.)*?)(?<!\\)"', flags=re.DOTALL)

    def _repl(match: re.Match) -> str:
        # match.group(1) è il contenuto interno a "…"
        inner = match.group(1)
        # eseguo la sostituzione
        inner_escaped = inner.replace('\n', '\\n')
        inner_escaped = inner_escaped.replace('\\"', "'")
        # ricostruisco il blocco con le virgolette
        return f'"{inner_escaped}"'

    # Applico la sostituzione a tutta la stringa
    return pattern.sub(_repl, s)


def strip_thinking_tokens(text: str) -> str:
    while "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>") + len("</think>")
        text = text[:start] + text[end:]
    return text


def _correggi_json(str_json: str) -> str:
    try:
        str_json = escape_newlines_in_quotes(str_json)
        struttura = ast.literal_eval(str_json)
        return json.dumps(struttura, indent=2, ensure_ascii=False)
    except:
        pass
    json.loads(str_json)
    return str_json

def extract_json(text: str) -> Optional[str]:
    json_string = strip_thinking_tokens(text)
    json_string = _extract_valid_json(json_string) # json_string.replace("```json", "").replace("```","")
    return json_string

def parse_model(model_class: Type[T], json_string_original: str) -> T:
    json_string = strip_thinking_tokens(json_string_original)
    json_string = _extract_valid_json(json_string) # json_string.replace("```json", "").replace("```","")
    try:
        # Pydantic v2
        queries_obj = model_class.model_validate_json(json_string)
    except :
        # Pydantic v1
        try:
            queries_obj = model_class.parse_raw(json_string)
        except:
            print("Errore di decodifica JSON----------------")
            print(json_string)
            print("----------------------------------------")
            raise #todo: remove

    return queries_obj



def _extract_valid_json(text: str, max_attempts: int = 5) -> Optional[str]:
    cleaned_text = text.strip()

    # Prova con il parsing diretto (potrebbe funzionare se il testo è già un JSON valido)
    try:
        cleaned_text = _correggi_json(cleaned_text)
        return cleaned_text
    except json.JSONDecodeError:
        pass

    strategies = [
        _extract_with_regex,
        _extract_with_balanced_parser,
        _extract_with_markdown_code_blocks,
        _extract_with_line_based_approach,
        _extract_with_fuzzy_matching
    ]

    # Limita i tentativi al numero di strategie disponibili
    attempts = min(max_attempts, len(strategies))

    # Prova ogni strategia in sequenza
    for i in range(attempts):
        result = strategies[i](cleaned_text)
        if result is not None:
            return result

    return None


def _extract_with_regex(text: str) -> Optional[str]:
    """Estrae JSON usando pattern regex per oggetti e array."""
    # Pattern per oggetti JSON con gestione nidificata
    json_patterns = [
        # Oggetti JSON
        r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}',
        # Array JSON
        r'\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]))*\]'
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for potential_json in matches:
            try:
                potential_json = _correggi_json(potential_json)
                return potential_json
            except json.JSONDecodeError:
                continue

    return None


def _extract_with_balanced_parser(text: str) -> Optional[str]:
    """Estrae JSON usando un parser che bilancia parentesi e gestisce le stringhe correttamente."""
    candidates = []

    # Cerca entrambi i tipi di aperture JSON
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start_index = text.find(start_char)
        if start_index == -1:
            continue

        stack = []
        in_string = False
        escape_next = False

        for i, char in enumerate(text[start_index:]):
            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == start_char:
                stack.append(char)
            elif char == end_char:
                if stack and stack[-1] == start_char:
                    stack.pop()
                    if not stack:  # Abbiamo trovato una struttura JSON completa
                        potential_json = text[start_index:start_index + i + 1]
                        try:
                            potential_json = _correggi_json(potential_json)
                            candidates.append((start_index, potential_json))
                        except json.JSONDecodeError:
                            pass

    # Restituisci il JSON che inizia prima nel testo
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    return None


def _extract_with_markdown_code_blocks(text: str) -> str:
    """Cerca JSON in blocchi di codice markdown."""
    # Cerca JSON in blocchi di codice markdown
    code_block_patterns = [
        r'```(?:json)?\s*([\s\S]*?)```',  # Markdown code blocks
        r'`([\s\S]*?)`'  # Inline code blocks
    ]

    for pattern in code_block_patterns:
        matches = re.findall(pattern, text)
        for code_content in matches:
            code_content = code_content.strip()
            try:
                if code_content.startswith('{') or code_content.startswith('['):
                    code_content = _correggi_json(code_content)
                    return code_content
            except json.JSONDecodeError:
                continue

    return None


def _extract_with_line_based_approach(text: str) -> Optional[str]:
    """
    Cerca JSON analizzando il testo riga per riga,
    identificando dove può iniziare e finire un JSON.
    """
    lines = text.split('\n')

    for i in range(len(lines)):
        line = lines[i].strip()
        # Cerca linee che potrebbero iniziare un JSON
        if line.startswith('{') or line.startswith('['):
            for j in range(i, len(lines)):
                end_line = lines[j].strip()
                if (line.startswith('{') and end_line.endswith('}')) or \
                        (line.startswith('[') and end_line.endswith(']')):
                    # Potenziale blocco JSON trovato
                    potential_json = '\n'.join(lines[i:j + 1])
                    try:
                        potential_json = _correggi_json(potential_json)
                        return potential_json
                    except json.JSONDecodeError:
                        # Prova a rimuovere commenti o testo in eccesso
                        cleaned = re.sub(r'//.*$|/\*[\s\S]*?\*/', '', potential_json, flags=re.MULTILINE)
                        try:
                            cleaned = _correggi_json(cleaned)
                            return cleaned
                        except json.JSONDecodeError:
                            continue

    return None


def _extract_with_fuzzy_matching(text: str) -> Optional[str]:
    """
    Approccio fuzzy per JSON malformati: cerca di correggere errori comuni
    come virgole finali, virgolette non corrispondenti, ecc.
    """
    json_like_patterns = [
        # Oggetti JSON
        r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}',
        # Array JSON
        r'\[(?:[^\[\]]|(?:\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]))*\]'
    ]

    for pattern in json_like_patterns:
        matches = re.findall(pattern, text)
        for potential_json in matches:
            try:
                data =  demjson3.decode(potential_json)
                json_string = json.dumps(data)
                return json_string
            except json.JSONDecodeError:
                continue

    return None


