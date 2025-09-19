"""
Unit tests for Document Parser module
"""

import pytest
from pathlib import Path
import tempfile
import os
from input_parsing.document_parser import DocumentParser


class TestDocumentParser:
    """Test cases for DocumentParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DocumentParser()
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_parser_initialization(self):
        """Test parser initialization."""
        assert self.parser is not None
        assert hasattr(self.parser, 'supported_formats')
        assert '.pdf' in self.parser.supported_formats
        assert '.docx' in self.parser.supported_formats
        assert '.xml' in self.parser.supported_formats
        
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_document("nonexistent_file.pdf")
            
    def test_parse_unsupported_format(self):
        """Test parsing unsupported file format."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")
        
        with pytest.raises(ValueError):
            self.parser.parse_document(test_file)
            
    def test_extract_clean_text(self):
        """Test clean text extraction."""
        parsed_doc = {
            'content': [
                {'type': 'text', 'text': 'Hello world'},
                {'type': 'paragraph', 'text': 'This is a test'},
                {'type': 'html_element', 'text': 'HTML content'},
                {'type': 'table', 'data': [['col1', 'col2'], ['val1', 'val2']]}
            ]
        }
        
        clean_text = self.parser.extract_clean_text(parsed_doc)
        
        assert 'Hello world' in clean_text
        assert 'This is a test' in clean_text
        assert 'HTML content' in clean_text
        assert 'col1 | col2' in clean_text
        
    def test_extract_hierarchy(self):
        """Test hierarchy extraction."""
        parsed_doc = {
            'content': [
                {'type': 'paragraph', 'text': 'Heading 1', 'style': 'Heading 1'},
                {'type': 'paragraph', 'text': 'Normal text', 'style': 'Normal'},
                {'type': 'html_element', 'tag': 'h2', 'text': 'Heading 2'}
            ]
        }
        
        hierarchy = self.parser.extract_hierarchy(parsed_doc)
        
        assert len(hierarchy) > 0
        assert any(item['level'] > 0 for item in hierarchy)
        
    def test_parse_text_file_as_sample(self):
        """Test parsing a text file as a sample document."""
        # Create a sample text file
        test_file = Path(self.temp_dir) / "sample.txt"
        test_content = """
        Healthcare Software Requirements
        
        1. Patient Data Management
        1.1 The system shall store patient information securely.
        1.2 The system shall comply with HIPAA requirements.
        
        2. Clinical Workflow
        2.1 The system shall integrate with EHR systems.
        2.2 The system shall provide real-time alerts.
        """
        test_file.write_text(test_content)
        
        # Test that the parser can handle text files (even though not in supported formats)
        # This tests the error handling
        with pytest.raises(ValueError):
            self.parser.parse_document(test_file)
            
    def test_supported_formats(self):
        """Test supported formats list."""
        expected_formats = ['.pdf', '.docx', '.doc', '.xml', '.html']
        assert self.parser.supported_formats == expected_formats
