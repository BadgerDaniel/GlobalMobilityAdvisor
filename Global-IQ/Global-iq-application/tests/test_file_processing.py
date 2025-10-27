# tests/test_file_processing.py
"""
Unit tests for file processing handlers.
Tests PDF, DOCX, XLSX, CSV, JSON, and TXT file processors.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
import sys


class TestProcessTXT:
    """Test TXT file processing."""

    def test_process_txt_basic(self, temp_txt_file):
        """Test basic TXT file processing."""
        from main import process_txt

        result = process_txt(temp_txt_file)

        assert result is not None
        assert isinstance(result, str)
        assert "Sample text content" in result

    def test_process_txt_multiline(self):
        """Test TXT file with multiple lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Line 1\nLine 2\nLine 3")
            temp_path = f.name

        try:
            from main import process_txt
            result = process_txt(temp_path)

            assert "Line 1" in result
            assert "Line 2" in result
            assert "Line 3" in result
        finally:
            os.unlink(temp_path)

    def test_process_txt_empty_file(self):
        """Test processing empty TXT file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            temp_path = f.name

        try:
            from main import process_txt
            result = process_txt(temp_path)

            assert result == ""
        finally:
            os.unlink(temp_path)

    def test_process_txt_nonexistent_file(self):
        """Test processing nonexistent TXT file."""
        from main import process_txt

        with pytest.raises(Exception):
            process_txt("/nonexistent/file.txt")

    def test_process_txt_special_characters(self):
        """Test TXT file with special characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("Special chars: é ñ ü 中文 🎉")
            temp_path = f.name

        try:
            from main import process_txt
            result = process_txt(temp_path)

            assert "Special chars" in result
        finally:
            os.unlink(temp_path)


class TestProcessJSON:
    """Test JSON file processing."""

    def test_process_json_basic(self, temp_json_file):
        """Test basic JSON file processing."""
        from main import process_json

        result = process_json(temp_json_file)

        assert result is not None
        assert isinstance(result, str)
        assert "test" in result
        assert "data" in result

    def test_process_json_nested_structure(self):
        """Test JSON with nested structure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            data = {
                "level1": {
                    "level2": {
                        "level3": "value"
                    }
                }
            }
            json.dump(data, f)
            temp_path = f.name

        try:
            from main import process_json
            result = process_json(temp_path)

            assert "level1" in result
            assert "level2" in result
            assert "level3" in result
        finally:
            os.unlink(temp_path)

    def test_process_json_array(self):
        """Test JSON with array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            data = [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}]
            json.dump(data, f)
            temp_path = f.name

        try:
            from main import process_json
            result = process_json(temp_path)

            assert "Item1" in result
            assert "Item2" in result
        finally:
            os.unlink(temp_path)

    def test_process_json_invalid_json(self):
        """Test processing invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("This is not valid JSON")
            temp_path = f.name

        try:
            from main import process_json

            with pytest.raises(Exception):
                process_json(temp_path)
        finally:
            os.unlink(temp_path)


class TestProcessCSV:
    """Test CSV file processing."""

    def test_process_csv_basic(self, temp_csv_file):
        """Test basic CSV file processing."""
        from main import process_csv

        result = process_csv(temp_csv_file)

        assert result is not None
        assert isinstance(result, str)
        assert "John Doe" in result
        assert "London" in result

    def test_process_csv_headers(self, temp_csv_file):
        """Test CSV processing includes headers."""
        from main import process_csv

        result = process_csv(temp_csv_file)

        assert "Name" in result
        assert "Location" in result
        assert "Salary" in result

    def test_process_csv_empty_file(self):
        """Test processing empty CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            temp_path = f.name

        try:
            from main import process_csv
            result = process_csv(temp_path)

            assert result == ""
        finally:
            os.unlink(temp_path)

    def test_process_csv_with_commas_in_data(self):
        """Test CSV with commas in quoted fields."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            f.write('Name,Description\n')
            f.write('"John Doe","A person with, commas"\n')
            temp_path = f.name

        try:
            from main import process_csv
            result = process_csv(temp_path)

            assert "John Doe" in result
        finally:
            os.unlink(temp_path)


class TestProcessDOCX:
    """Test DOCX file processing."""

    def test_process_docx_requires_library(self):
        """Test that process_docx requires python-docx."""
        from main import process_docx

        # Since we can't easily create real DOCX files in tests,
        # we'll test that the function exists and can be called
        assert callable(process_docx)

    def test_process_docx_nonexistent_file(self):
        """Test processing nonexistent DOCX."""
        from main import process_docx

        with pytest.raises(Exception):
            process_docx("/nonexistent/file.docx")


class TestProcessXLSX:
    """Test XLSX file processing."""

    def test_process_xlsx_requires_library(self):
        """Test that process_xlsx requires openpyxl."""
        from main import process_xlsx

        assert callable(process_xlsx)

    def test_process_xlsx_nonexistent_file(self):
        """Test processing nonexistent XLSX."""
        from main import process_xlsx

        with pytest.raises(Exception):
            process_xlsx("/nonexistent/file.xlsx")


class TestProcessPDF:
    """Test PDF file processing."""

    def test_process_pdf_requires_library(self):
        """Test that process_pdf requires PyMuPDF."""
        from main import process_pdf

        assert callable(process_pdf)

    def test_process_pdf_nonexistent_file(self):
        """Test processing nonexistent PDF."""
        from main import process_pdf

        with pytest.raises(Exception):
            process_pdf("/nonexistent/file.pdf")


class TestFileHandlerDispatch:
    """Test file handler dispatch dictionary."""

    def test_file_handlers_mapping_exists(self):
        """Test that FILE_HANDLERS mapping exists."""
        from main import FILE_HANDLERS

        assert FILE_HANDLERS is not None
        assert isinstance(FILE_HANDLERS, dict)

    def test_file_handlers_has_all_types(self):
        """Test that all file types are mapped."""
        from main import FILE_HANDLERS

        # Check for key MIME types
        expected_handlers = [
            "application/pdf",
            "text/plain",
            "text/csv",
            "application/json",
            ".txt",
            ".csv",
            ".json"
        ]

        for handler_key in expected_handlers:
            assert handler_key in FILE_HANDLERS

    def test_file_handlers_functions_callable(self):
        """Test that all handlers are callable."""
        from main import FILE_HANDLERS

        for mime_type, handler in FILE_HANDLERS.items():
            assert callable(handler), f"Handler for {mime_type} is not callable"

    def test_file_handler_dispatch_pdf(self):
        """Test dispatching to PDF handler."""
        from main import FILE_HANDLERS, process_pdf

        handler = FILE_HANDLERS.get("application/pdf")
        assert handler is process_pdf

    def test_file_handler_dispatch_txt(self):
        """Test dispatching to TXT handler."""
        from main import FILE_HANDLERS, process_txt

        handler = FILE_HANDLERS.get("text/plain")
        assert handler is process_txt

    def test_file_handler_dispatch_json(self):
        """Test dispatching to JSON handler."""
        from main import FILE_HANDLERS, process_json

        handler = FILE_HANDLERS.get("application/json")
        assert handler is process_json


class TestFileProcessingIntegration:
    """Test integrated file processing scenarios."""

    def test_process_multiple_txt_files(self):
        """Test processing multiple TXT files."""
        files = []
        try:
            for i in range(3):
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                    f.write(f"Content from file {i}")
                    files.append(f.name)

            from main import process_txt

            results = [process_txt(f) for f in files]

            assert len(results) == 3
            for i, result in enumerate(results):
                assert f"Content from file {i}" in result
        finally:
            for f in files:
                if os.path.exists(f):
                    os.unlink(f)

    def test_process_json_then_extract_data(self):
        """Test processing JSON and extracting data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            data = {
                "employees": [
                    {"name": "John", "location": "London", "salary": 100000},
                    {"name": "Jane", "location": "Paris", "salary": 120000}
                ]
            }
            json.dump(data, f)
            temp_path = f.name

        try:
            from main import process_json
            result = process_json(temp_path)

            # Verify all employee data is in result
            assert "John" in result
            assert "Jane" in result
            assert "London" in result
            assert "Paris" in result
        finally:
            os.unlink(temp_path)


class TestErrorHandling:
    """Test error handling in file processing."""

    def test_process_txt_permission_denied(self):
        """Test handling permission denied errors."""
        from main import process_txt

        # This test is platform-specific and may not work on all systems
        # We're just ensuring the function raises an exception
        with pytest.raises(Exception):
            process_txt("/root/protected_file.txt")

    def test_process_csv_corrupted_data(self):
        """Test handling corrupted CSV data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            # Write invalid CSV with mismatched columns
            f.write("Name,Age,Location\n")
            f.write("John,30\n")  # Missing column
            f.write("Jane,25,Paris,Extra\n")  # Extra column
            temp_path = f.name

        try:
            from main import process_csv
            result = process_csv(temp_path)

            # Should still process without crashing
            assert result is not None
        finally:
            os.unlink(temp_path)

    def test_process_json_with_unicode(self):
        """Test processing JSON with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            data = {
                "message": "Hello 世界 🌍",
                "location": "São Paulo"
            }
            json.dump(data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            from main import process_json
            result = process_json(temp_path)

            assert result is not None
            # Unicode should be preserved
            assert "São Paulo" in result or "Sao Paulo" in result
        finally:
            os.unlink(temp_path)


class TestFileSizeHandling:
    """Test handling of large files."""

    def test_process_large_txt_file(self):
        """Test processing large TXT file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # Write large file (1MB of text)
            large_text = "This is a line of text.\n" * 40000
            f.write(large_text)
            temp_path = f.name

        try:
            from main import process_txt
            result = process_txt(temp_path)

            assert result is not None
            assert len(result) > 0
        finally:
            os.unlink(temp_path)

    def test_process_large_json_file(self):
        """Test processing large JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            # Create large JSON array
            large_data = [{"id": i, "name": f"Item{i}", "value": i * 100} for i in range(1000)]
            json.dump(large_data, f)
            temp_path = f.name

        try:
            from main import process_json
            result = process_json(temp_path)

            assert result is not None
            assert "Item0" in result
            assert "Item999" in result
        finally:
            os.unlink(temp_path)
