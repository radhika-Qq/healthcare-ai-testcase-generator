"""
Basic Usage Example for Healthcare AI Test Case Generator

This example demonstrates how to use the healthcare AI test case generator
to parse requirements and generate test cases.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from input_parsing import parse_healthcare_document
from test_case_generation import TestCaseGenerator, ExportManager, TraceabilityMatrixGenerator
import json


def main():
    """Main example function."""
    print("Healthcare AI Test Case Generator - Basic Usage Example")
    print("=" * 60)
    
    # Example 1: Parse a healthcare document
    print("\n1. Parsing Healthcare Document")
    print("-" * 30)
    
    # Create a sample requirement document
    sample_doc_path = create_sample_requirement_document()
    
    try:
        # Parse the document (without AI for this example)
        parsed_data = parse_healthcare_document(sample_doc_path)
        
        print(f"✓ Parsed document: {parsed_data['document_info']['file_path']}")
        print(f"✓ Found {len(parsed_data['requirements'])} requirements")
        print(f"✓ Generated {len(parsed_data['compliance_mappings'])} compliance mappings")
        
        # Display requirements summary
        summary = parsed_data['summary']
        print(f"\nRequirements Summary:")
        print(f"  - Total requirements: {summary['total_requirements']}")
        print(f"  - By type: {summary['by_type']}")
        print(f"  - By priority: {summary['by_priority']}")
        print(f"  - Compliance references: {summary['compliance_refs']}")
        
    except Exception as e:
        print(f"✗ Error parsing document: {str(e)}")
        return
    
    # Example 2: Generate test cases
    print("\n2. Generating Test Cases")
    print("-" * 30)
    
    try:
        # Initialize test case generator
        tc_generator = TestCaseGenerator()
        
        # Generate test cases from requirements
        test_cases = tc_generator.generate_test_cases(
            parsed_data['requirements'],
            parsed_data['compliance_mappings']
        )
        
        print(f"✓ Generated {len(test_cases)} test cases")
        
        # Display test case details
        for i, tc in enumerate(test_cases[:3], 1):  # Show first 3 test cases
            print(f"\nTest Case {i}:")
            print(f"  - ID: {tc.id}")
            print(f"  - Title: {tc.title}")
            print(f"  - Type: {tc.test_case_type.value}")
            print(f"  - Priority: {tc.priority.value}")
            print(f"  - Steps: {len(tc.test_steps)}")
            print(f"  - Compliance Refs: {tc.compliance_refs}")
            
    except Exception as e:
        print(f"✗ Error generating test cases: {str(e)}")
        return
    
    # Example 3: Export test cases
    print("\n3. Exporting Test Cases")
    print("-" * 30)
    
    try:
        # Initialize export manager
        export_manager = ExportManager()
        
        # Export to different formats
        output_dir = Path("examples/output")
        output_dir.mkdir(exist_ok=True)
        
        # Export to JSON
        json_path = output_dir / "test_cases.json"
        success = export_manager.export_test_cases(test_cases, json_path, 'json')
        if success:
            print(f"✓ Exported to JSON: {json_path}")
        
        # Export to Excel
        excel_path = output_dir / "test_cases.xlsx"
        success = export_manager.export_test_cases(test_cases, excel_path, 'excel')
        if success:
            print(f"✓ Exported to Excel: {excel_path}")
        
        # Export to CSV
        csv_path = output_dir / "test_cases.csv"
        success = export_manager.export_test_cases(test_cases, csv_path, 'csv')
        if success:
            print(f"✓ Exported to CSV: {csv_path}")
            
    except Exception as e:
        print(f"✗ Error exporting test cases: {str(e)}")
        return
    
    # Example 4: Generate traceability matrix
    print("\n4. Generating Traceability Matrix")
    print("-" * 30)
    
    try:
        # Initialize traceability matrix generator
        matrix_generator = TraceabilityMatrixGenerator()
        
        # Generate traceability matrix
        matrix_data = matrix_generator.generate_traceability_matrix(
            parsed_data['requirements'],
            test_cases,
            parsed_data['compliance_mappings']
        )
        
        print(f"✓ Generated traceability matrix")
        print(f"  - Traceability items: {len(matrix_data['traceability_items'])}")
        print(f"  - Matrix views: {len(matrix_data['matrix_views'])}")
        
        # Display coverage summary
        coverage_summary = matrix_data['matrix_views']['coverage_summary']
        print(f"\nCoverage Summary:")
        print(f"  - Total requirements: {coverage_summary['total_requirements']}")
        print(f"  - Total test cases: {coverage_summary['total_test_cases']}")
        print(f"  - Covered requirements: {coverage_summary['covered_requirements']}")
        print(f"  - Coverage percentage: {coverage_summary['coverage_percentage']}%")
        
        # Export traceability matrix
        matrix_path = output_dir / "traceability_matrix.xlsx"
        success = matrix_generator.export_traceability_matrix(matrix_data, str(matrix_path), 'excel')
        if success:
            print(f"✓ Exported traceability matrix: {matrix_path}")
            
    except Exception as e:
        print(f"✗ Error generating traceability matrix: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("✓ Basic usage example completed successfully!")
    print(f"✓ Check the 'examples/output' directory for exported files")
    
    # Clean up sample file
    if sample_doc_path.exists():
        sample_doc_path.unlink()


def create_sample_requirement_document() -> Path:
    """Create a sample healthcare requirement document for testing."""
    sample_content = """
    Healthcare Software Requirements Specification
    
    1. Patient Data Management
    1.1 The system shall store patient demographic information including name, date of birth, and medical record number.
    1.2 The system shall encrypt all patient data in accordance with HIPAA requirements.
    1.3 The system shall maintain an audit trail of all patient data access.
    
    2. Clinical Workflow
    2.1 The system shall support electronic health record (EHR) integration per HL7 FHIR standards.
    2.2 The system shall validate clinical data entry against medical terminology standards.
    2.3 The system shall provide real-time alerts for critical patient conditions.
    
    3. Security and Compliance
    3.1 The system shall implement role-based access control for healthcare providers.
    3.2 The system shall comply with FDA 21 CFR 820 for medical device software.
    3.3 The system shall support electronic signatures per FDA 21 CFR 11.
    3.4 The system shall meet ISO 13485 quality management requirements.
    
    4. Performance Requirements
    4.1 The system shall respond to user queries within 2 seconds under normal load.
    4.2 The system shall support up to 1000 concurrent users.
    4.3 The system shall maintain 99.9% uptime availability.
    
    5. Usability Requirements
    5.1 The system shall provide an intuitive user interface for healthcare providers.
    5.2 The system shall support accessibility standards per ADA guidelines.
    5.3 The system shall provide context-sensitive help and documentation.
    """
    
    # Create sample document file
    sample_path = Path("examples/sample_requirements.txt")
    sample_path.parent.mkdir(exist_ok=True)
    
    with open(sample_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)
        
    return sample_path


if __name__ == "__main__":
    main()

