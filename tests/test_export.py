import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.export import to_excel_bytes, to_pdf_bytes, to_word_bytes

SAMPLE_RECORDS = [
    {"id": "1001", "name": "Prime LLC", "country": "US"},
    {"id": "1002", "name": "Nikon Corp", "country": "DE"},
]


def test_excel_export_produces_nonempty_bytes():
    data = to_excel_bytes(SAMPLE_RECORDS)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_word_export_produces_nonempty_bytes():
    data = to_word_bytes(SAMPLE_RECORDS)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pdf_export_produces_nonempty_bytes():
    data = to_pdf_bytes(SAMPLE_RECORDS)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_exports_handle_empty_records():
    assert len(to_excel_bytes([])) > 0
    assert len(to_word_bytes([])) > 0
    assert len(to_pdf_bytes([])) > 0
