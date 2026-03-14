import io

from fastapi import UploadFile

from app.services.file_reader_service import FileReaderService


def test_read_txt_file():
    service = FileReaderService()
    fake_file = UploadFile(filename="teste.txt", file=io.BytesIO(b"Este e um texto simples para analise."))

    result = service.read_uploaded_file(fake_file)

    assert result["filename"] == "teste.txt"
    assert "texto simples" in result["text"]
