# Importa a classe ContentExtractor do módulo app.services.content_extractor
from app.services.content_extractor import ContentExtractor


# Define uma função de teste chamada test_extract_relevant_text_removes_noise
def test_extract_relevant_text_removes_noise():
    # Cria uma string HTML simulando uma página com conteúdo relevante e ruído
    html = """
    <html>
        <body>
            <header>Menu principal</header>  <!-- Cabeçalho que deve ser ignorado -->
            <nav>Links do site</nav>          <!-- Navegação que deve ser ignorada -->
            <article>                         <!-- Conteúdo principal -->
                <h1>Título</h1>               <!-- Título do artigo -->
                <p>Este é um conteúdo relevante com várias frases. Ele deve ser extraído.</p>
                <p>O sistema precisa ignorar scripts e regiões de navegação.</p>
            </article>
            <script>console.log("teste")</script> <!-- Script que deve ser removido -->
        </body>
    </html>
    """

    # Cria uma instância da classe ContentExtractor
    extractor = ContentExtractor()

    # Chama o método _extract_relevant_text para extrair apenas o texto relevante do HTML
    text = extractor._extract_relevant_text(html)

    # Verifica se o texto extraído contém a parte relevante
    assert "conteúdo relevante" in text

    # Verifica se o texto extraído NÃO contém o código JavaScript
    assert "console.log" not in text

    # Verifica se o texto extraído NÃO contém o conteúdo da navegação
    assert "Links do site" not in text

