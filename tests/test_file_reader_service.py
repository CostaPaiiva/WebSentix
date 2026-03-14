import io  # Importa o módulo io, usado para criar objetos de arquivo em memória

from fastapi import UploadFile  # Importa a classe UploadFile do FastAPI, que simula arquivos enviados em requisições

from app.services.file_reader_service import FileReaderService  # Importa o serviço responsável por ler arquivos


def test_read_txt_file():  # Define uma função de teste para verificar a leitura de arquivos .txt
    service = FileReaderService()  # Cria uma instância do serviço de leitura de arquivos

    # Cria um arquivo falso em memória usando UploadFile e io.BytesIO
    fake_file = UploadFile(
        filename="teste.txt", 
        file=io.BytesIO(b"Este e um texto simples para analise.")
    )

    # Chama o método do serviço para ler o conteúdo do arquivo falso
    result = service.read_uploaded_file(fake_file)

    # Verifica se o nome do arquivo retornado é o mesmo que foi definido
    assert result["filename"] == "teste.txt"

    # Verifica se o texto extraído contém a frase esperada
    assert "texto simples" in result["text"]
