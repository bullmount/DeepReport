from search_system import SearchSystem



def test_fetch_pdf():
    # url = 'https://www.regione.marche.it/portals/0/Lavoro_Formazione_Professionale/Osservatorio%20Lavoro/Report%20Annuale%202024.pdf'
    # url = "https://politichecoesione.governo.it/media/msmpbnmk/s3_regione-marche_2014-2020.pdf"
    # url = "https://www.regione.marche.it/portals/0/Lavoro_Formazione_Professionale/Osservatorio%20Lavoro/Report%20annuale%202023.pdf"
    # url = "https://www.regione.marche.it/portals/0/Lavoro_Formazione_Professionale/Osservatorio%20Lavoro/Report%20Annuale%202022.pdf"
    url="https://www.regione.marche.it/In-Primo-Piano/ComunicatiStampa?id=27728"
    markdown_text = SearchSystem._fetch_raw_content(url)
    assert markdown_text is not None
    #todo: remove
    with open("pdf_converted.md", "w", encoding="utf-8") as md_file:
        md_file.write(markdown_text)

