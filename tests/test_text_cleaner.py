from app.utils.text_cleaner import clean_text, split_sentences


def test_clean_text_removes_html_and_extra_spaces():
    raw = " <p>Olá&nbsp;&nbsp;mundo</p> \n\n <b>teste</b> "
    cleaned = clean_text(raw)
    assert cleaned == "Olá mundo teste"


def test_split_sentences_basic():
    text = "Olá mundo. Tudo bem? Sim!"
    parts = split_sentences(text)

    assert len(parts) == 3
    assert parts[0] == "Olá mundo."
