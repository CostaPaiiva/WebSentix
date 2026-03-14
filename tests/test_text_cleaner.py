from app.utils.text_cleaner import clean_text, split_sentences  # Importa funções utilitárias para limpar texto e dividir em sentenças


def test_clean_text_removes_html_and_extra_spaces():  # Testa se a função clean_text remove HTML e espaços extras
    raw = " <p>Olá&nbsp;&nbsp;mundo</p> \n\n <b>teste</b> "  # Texto bruto com tags HTML e espaços desnecessários
    cleaned = clean_text(raw)  # Aplica a limpeza no texto
    assert cleaned == "Olá mundo teste"  # Verifica se o resultado está correto após a limpeza


def test_split_sentences_basic():  # Testa se a função split_sentences divide corretamente em sentenças
    text = "Olá mundo. Tudo bem? Sim!"  # Texto de exemplo com três frases
    parts = split_sentences(text)  # Divide o texto em sentenças

    assert len(parts) == 3  # Verifica se foram identificadas 3 sentenças
    assert parts[0] == "Olá mundo."  # Verifica se a primeira sentença foi extraída corretamente
