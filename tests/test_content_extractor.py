from app.services.content_extractor import ContentExtractor


def test_extract_relevant_text_removes_noise():
    html = """
    <html>
        <body>
            <header>Menu principal</header>
            <nav>Links do site</nav>
            <article>
                <h1>Título</h1>
                <p>Este é um conteúdo relevante com várias frases. Ele deve ser extraído.</p>
                <p>O sistema precisa ignorar scripts e regiões de navegação.</p>
            </article>
            <script>console.log("teste")</script>
        </body>
    </html>
    """
    extractor = ContentExtractor()
    text = extractor._extract_relevant_text(html)

    assert "conteúdo relevante" in text
    assert "console.log" not in text
    assert "Links do site" not in text
