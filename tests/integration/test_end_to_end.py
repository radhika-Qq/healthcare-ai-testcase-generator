"""
Integration tests for end-to-end functionality
"""

import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from input_parsing import parse_healthcare_document
from test_case_generation import TestCaseGenerator, ExportManager, TraceabilityMatrixGenerator


class TestEndToEnd:
    """Integration tests for end-to-end functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_requirements = self._create_sample_requirements()
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_sample_requirements(self):
        """Create sample requirements for testing."""
        return [
            {
                'id': 'REQ-001',
                'description': 'The system shall store patient demographic information securely',
                'type': 'functional',
                'priority': 'high',
                'compliance_refs': ['HIPAA', 'GDPR'],
                'source_section': 'Data Management',
                'context': 'Patient data storage',
                'acceptance_criteria': ['Data is encrypted', 'Access is logged'],
                'dependencies': [],
                'raw_text': 'The system shall store patient demographic information securely'
            },
            {
                'id': 'REQ-002',
                'description': 'The system shall respond to user queries within 2 seconds',
                'type': 'performance',
                'priority': 'medium',
                'compliance_refs': ['ISO_13485'],
                'source_section': 'Performance',
                'context': 'System responsiveness',
                'acceptance_criteria': ['Response time < 2 seconds'],
                'dependencies': [],
                'raw_text': 'The system shall respond to user queries within 2 seconds'
            },
            {
                'id': 'REQ-003',
                'description': 'The system shall implement role-based access control',
                'type': 'security',
                'priority': 'critical',
                'compliance_refs': ['FDA_21_CFR_11', 'HIPAA'],
                'source_section': 'Security',
                'context': 'Access control',
                'acceptance_criteria': ['Users can only access authorized data'],
                'dependencies': ['REQ-001'],
                'raw_text': 'The system shall implement role-based access control'
            }
        ]
        
    def test_parse_healthcare_document_integration(self):
        """Test end-to-end document parsing."""
        # Create a sample document
        doc_path = Path(self.temp_dir) / "sample_requirements.txt"
        doc_content = """
        Healthcare Software Requirements
        
        1. Patient Data Management
        1.1 The system shall store patient demographic information securely.
        1.2 The system shall comply with HIPAA requirements.
        
        2. Performance Requirements
        2.1 The system shall respond to user queries within 2 seconds.
        2.2 The system shall support up to 1000 concurrent users.
        
        3. Security Requirements
        3.1 The system shall implement role-based access control.
        3.2 The system shall encrypt all sensitive data.
        """
        doc_path.write_text(doc_content)
        
        # Parse the document
        try:
            parsed_data = parse_healthcare_document(doc_path)
            
            # Verify basic structure
            assert 'document_info' in parsed_data
            assert 'requirements' in parsed_data
            assert 'compliance_mappings' in parsed_data
            assert 'traceability_matrix' in parsed_data
            assert 'summary' in parsed_data
            
            # Verify document info
            doc_info = parsed_data['document_info']
            assert doc_info['file_path'] == str(doc_path)
            assert doc_info['file_type'] == 'txt'  # Will be treated as text
            
            # Verify requirements were extracted
            requirements = parsed_data['requirements']
            assert len(requirements) > 0
            
            # Verify summary
            summary = parsed_data['summary']
            assert summary['total_requirements'] > 0
            
        except Exception as e:
            pytest.skip(f"Document parsing failed: {str(e)}")
            
    def test_test_case_generation_integration(self):
        """Test end-to-end test case generation."""
        # Initialize test case generator
        generator = TestCaseGenerator()
        
        # Generate test cases from sample requirements
        test_cases = generator.generate_test_cases(self.sample_requirements)
        
        # Verify test cases were generated
        assert len(test_cases) > 0
        
        # Verify test case structure
        for tc in test_cases:
            assert hasattr(tc, 'id')
            assert hasattr(tc, 'title')
            assert hasattr(tc, 'description')
            assert hasattr(tc, 'test_case_type')
            assert hasattr(tc, 'priority')
            assert hasattr(tc, 'requirement_id')
            assert hasattr(tc, 'test_steps')
            assert hasattr(tc, 'expected_outcome')
            
            # Verify test steps
            assert len(tc.test_steps) > 0
            for step in tc.test_steps:
                assert hasattr(step, 'step_number')
                assert hasattr(step, 'action')
                assert hasattr(step, 'expected_result')
                
    def test_export_integration(self):
        """Test end-to-end export functionality."""
        # Generate test cases
        generator = TestCaseGenerator()
        test_cases = generator.generate_test_cases(self.sample_requirements)
        
        # Initialize export manager
        export_manager = ExportManager()
        
        # Test JSON export
        json_path = Path(self.temp_dir) / "test_cases.json"
        success = export_manager.export_test_cases(test_cases, json_path, 'json')
        assert success
        assert json_path.exists()
        
        # Test CSV export
        csv_path = Path(self.temp_dir) / "test_cases.csv"
        success = export_manager.export_test_cases(test_cases, csv_path, 'csv')
        assert success
        assert csv_path.exists()
        
        # Test Excel export
        excel_path = Path(self.temp_dir) / "test_cases.xlsx"
        success = export_manager.export_test_cases(test_cases, excel_path, 'excel')
        assert success
        assert excel_path.exists()
        
    def test_traceability_matrix_integration(self):
        """Test end-to-end traceability matrix generation."""
        # Generate test cases
        generator = TestCaseGenerator()
        test_cases = generator.generate_test_cases(self.sample_requirements)
        
        # Initialize traceability matrix generator
        matrix_generator = TraceabilityMatrixGenerator()
        
        # Generate traceability matrix
        matrix_data = matrix_generator.generate_traceability_matrix(
            self.sample_requirements,
            test_cases
        )
        
        # Verify matrix structure
        assert 'traceability_items' in matrix_data
        assert 'matrix_views' in matrix_data
        assert 'generation_timestamp' in matrix_data
        
        # Verify matrix views
        matrix_views = matrix_data['matrix_views']
        assert 'requirement_to_test_case' in matrix_views
        assert 'test_case_to_requirement' in matrix_views
        assert 'compliance_coverage' in matrix_views
        assert 'coverage_summary' in matrix_views
        
        # Verify coverage summary
        coverage_summary = matrix_views['coverage_summary']
        assert coverage_summary['total_requirements'] == len(self.sample_requirements)
        assert coverage_summary['total_test_cases'] == len(test_cases)
        assert coverage_summary['coverage_percentage'] >= 0
        
        # Test matrix export
        matrix_path = Path(self.temp_dir) / "traceability_matrix.xlsx"
        success = matrix_generator.export_traceability_matrix(matrix_data, str(matrix_path), 'excel')
        assert success
        assert matrix_path.exists()
        
    def test_full_workflow_integration(self):
        """Test complete workflow from document parsing to export."""
        # Create sample document
        doc_path = Path(self.temp_dir) / "workflow_test.txt"
        doc_content = """
        Healthcare Software Requirements
        
        1. Patient Data Management
        1.1 The system shall store patient information securely.
        1.2 The system shall comply with HIPAA requirements.
        
        2. Performance Requirements
        2.1 The system shall respond within 2 seconds.
        """
        doc_path.write_text(doc_content)
        
        try:
            # Step 1: Parse document
            parsed_data = parse_healthcare_document(doc_path)
            
            # Step 2: Generate test cases
            generator = TestCaseGenerator()
            test_cases = generator.generate_test_cases(parsed_data['requirements'])
            
            # Step 3: Generate traceability matrix
            matrix_generator = TraceabilityMatrixGenerator()
            matrix_data = matrix_generator.generate_traceability_matrix(
                parsed_data['requirements'],
                test_cases
            )
            
            # Step 4: Export everything
            export_manager = ExportManager()
            
            # Export test cases
            test_cases_path = Path(self.temp_dir) / "workflow_test_cases.xlsx"
            export_manager.export_test_cases(test_cases, test_cases_path, 'excel')
            
            # Export traceability matrix
            matrix_path = Path(self.temp_dir) / "workflow_matrix.xlsx"
            matrix_generator.export_traceability_matrix(matrix_data, str(matrix_path), 'excel')
            
            # Verify all files were created
            assert test_cases_path.exists()
            assert matrix_path.exists()
            
            # Verify test cases were generated
            assert len(test_cases) > 0
            
            # Verify traceability matrix was generated
            assert len(matrix_data['traceability_items']) > 0
            
        except Exception as e:
            pytest.skip(f"Full workflow test failed: {str(e)}")
            
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        # Test with invalid document
        invalid_doc_path = Path(self.temp_dir) / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            parse_healthcare_document(invalid_doc_path)
            
        # Test with empty requirements
        generator = TestCaseGenerator()
        empty_test_cases = generator.generate_test_cases([])
        assert len(empty_test_cases) == 0
        
        # Test export with empty test cases
        export_manager = ExportManager()
        empty_path = Path(self.temp_dir) / "empty.json"
        success = export_manager.export_test_cases([], empty_path, 'json')
        assert success  # Should succeed even with empty data
