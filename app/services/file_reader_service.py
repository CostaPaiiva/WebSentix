from __future__ import annotations

import io

from fastapi import UploadFile
from docx import Document
from pypdf import PdfReader

from app.config.settings import settings
from app.utils.text_cleaner import clean_text


class FileReaderError(Exception):
    """Erro ao ler arquivo enviado."""


class FileReaderService:
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

    def read_uploaded_file(self, uploaded_file: UploadFile | None) -> dict[str, object]:
        if uploaded_file is None:
            raise FileReaderError("Nenhum arquivo foi enviado.")

        filename = uploaded_file.filename or "arquivo_desconhecido"
        extension = self._get_extension(filename)

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise FileReaderError("Formato de arquivo não suportado. Use .txt, .pdf ou .docx.")

        if extension == ".txt":
            text = self._read_txt(uploaded_file)
        elif extension == ".pdf":
            text = self._read_pdf(uploaded_file)
        elif extension == ".docx":
            text = self._read_docx(uploaded_file)
        else:
            raise FileReaderError("Formato de arquivo inválido.")

        cleaned = clean_text(text)[: settings.max_content_chars]

        if len(cleaned.split()) < 3:
            raise FileReaderError("O arquivo não possui conteúdo textual suficiente para análise.")

        return {
            "filename": filename,
            "extension": extension,
            "text": cleaned,
            "raw_length": len(text),
            "cleaned_length": len(cleaned),
        }

    @staticmethod
    def _get_extension(filename: str) -> str:
        parts = filename.lower().rsplit(".", 1)
        if len(parts) != 2:
            raise FileReaderError("Não foi possível identificar a extensão do arquivo.")
        return f".{parts[1]}"

    @staticmethod
    def _read_txt(uploaded_file: UploadFile) -> str:
        try:
            raw = uploaded_file.file.read()
            uploaded_file.file.seek(0)
            return raw.decode("utf-8", errors="ignore")
        except Exception as exc:
            raise FileReaderError("Falha ao ler o arquivo TXT.") from exc

    @staticmethod
    def _read_pdf(uploaded_file: UploadFile) -> str:
        try:
            file_bytes = uploaded_file.file.read()
            uploaded_file.file.seek(0)
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()

            if not text:
                raise FileReaderError("Não foi possível extrair texto do PDF enviado.")

            return text
        except FileReaderError:
            raise
        except Exception as exc:
            raise FileReaderError("Falha ao ler o arquivo PDF.") from exc

    @staticmethod
    def _read_docx(uploaded_file: UploadFile) -> str:
        try:
            file_bytes = uploaded_file.file.read()
            uploaded_file.file.seek(0)
            document = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs).strip()

            if not text:
                raise FileReaderError("Não foi possível extrair texto do arquivo DOCX enviado.")

            return text
        except FileReaderError:
            raise
        except Exception as exc:
            raise FileReaderError("Falha ao ler o arquivo DOCX.") from exc
