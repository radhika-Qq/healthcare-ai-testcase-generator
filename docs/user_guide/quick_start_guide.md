# Quick Start Guide - Healthcare AI Test Case Generator

## Overview

This guide will help you get started with the Healthcare AI Test Case Generator in just a few minutes. You'll learn how to upload requirements, generate test cases, and export results.

## Prerequisites

- Python 3.8 or higher
- Google Cloud account (for AI features)
- Basic understanding of healthcare software testing

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/healthcare-ai-testcase-generator.git
cd healthcare-ai-testcase-generator
```

### Step 2: Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Access
```bash
# Set up Google AI API key
export GOOGLE_AI_API_KEY="your-api-key-here"

# Or set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

## Basic Usage

### 1. Upload Requirements Document

The system supports various document formats:
- **PDF**: Healthcare requirement specifications
- **Word**: .docx and .doc files
- **XML**: Structured healthcare specifications
- **HTML**: Web-based documentation

### 2. Parse Requirements

```python
from input_parsing import parse_healthcare_document

# Parse your healthcare document
result = parse_healthcare_document("path/to/your/requirements.pdf")

# View extracted requirements
print(f"Found {len(result['requirements'])} requirements")
for req in result['requirements'][:3]:  # Show first 3
    print(f"- {req['id']}: {req['description']}")
```

### 3. Generate Test Cases

```python
from test_case_generation import TestCaseGenerator

# Initialize test case generator
generator = TestCaseGenerator()

# Generate test cases
test_cases = generator.generate_test_cases(
    result['requirements'],
    result['compliance_mappings']
)

print(f"Generated {len(test_cases)} test cases")
```

### 4. Export Results

```python
from test_case_generation import ExportManager

# Initialize export manager
export_manager = ExportManager()

# Export to Excel
export_manager.export_test_cases(
    test_cases, 
    "output/test_cases.xlsx", 
    "excel"
)

# Export to Jira
export_manager.export_test_cases(
    test_cases, 
    "output/jira_import.json", 
    "jira",
    project_key="TEST",
    issue_type="Test"
)
```

## Complete Workflow Example

Here's a complete example that demonstrates the full workflow:

```python
#!/usr/bin/env python3
"""
Complete Healthcare AI Test Case Generator Workflow
"""

from input_parsing import parse_healthcare_document
from test_case_generation import TestCaseGenerator, ExportManager, TraceabilityMatrixGenerator

def main():
    print("🏥 Healthcare AI Test Case Generator - Complete Workflow")
    print("=" * 60)
    
    # Step 1: Parse healthcare document
    print("\n📄 Step 1: Parsing healthcare document...")
    try:
        result = parse_healthcare_document("examples/sample_requirements.pdf")
        print(f"✅ Successfully parsed document")
        print(f"   - Requirements found: {len(result['requirements'])}")
        print(f"   - Compliance mappings: {len(result['compliance_mappings'])}")
    except Exception as e:
        print(f"❌ Error parsing document: {e}")
        return
    
    # Step 2: Generate test cases
    print("\n🧪 Step 2: Generating test cases...")
    try:
        generator = TestCaseGenerator()
        test_cases = generator.generate_test_cases(
            result['requirements'],
            result['compliance_mappings']
        )
        print(f"✅ Successfully generated {len(test_cases)} test cases")
        
        # Show sample test case
        if test_cases:
            sample_tc = test_cases[0]
            print(f"   Sample test case: {sample_tc.title}")
            print(f"   - Type: {sample_tc.test_case_type.value}")
            print(f"   - Priority: {sample_tc.priority.value}")
            print(f"   - Steps: {len(sample_tc.test_steps)}")
    except Exception as e:
        print(f"❌ Error generating test cases: {e}")
        return
    
    # Step 3: Generate traceability matrix
    print("\n🔗 Step 3: Generating traceability matrix...")
    try:
        matrix_generator = TraceabilityMatrixGenerator()
        matrix_data = matrix_generator.generate_traceability_matrix(
            result['requirements'],
            test_cases,
            result['compliance_mappings']
        )
        print(f"✅ Successfully generated traceability matrix")
        print(f"   - Traceability items: {len(matrix_data['traceability_items'])}")
        
        # Show coverage summary
        coverage = matrix_data['matrix_views']['coverage_summary']
        print(f"   - Coverage: {coverage['coverage_percentage']}%")
    except Exception as e:
        print(f"❌ Error generating traceability matrix: {e}")
        return
    
    # Step 4: Export results
    print("\n📤 Step 4: Exporting results...")
    try:
        export_manager = ExportManager()
        
        # Export test cases to Excel
        excel_path = "output/test_cases.xlsx"
        success = export_manager.export_test_cases(test_cases, excel_path, "excel")
        if success:
            print(f"✅ Exported test cases to: {excel_path}")
        
        # Export traceability matrix
        matrix_path = "output/traceability_matrix.xlsx"
        success = matrix_generator.export_traceability_matrix(matrix_data, matrix_path, "excel")
        if success:
            print(f"✅ Exported traceability matrix to: {matrix_path}")
        
        # Export to JSON for integration
        json_path = "output/test_cases.json"
        success = export_manager.export_test_cases(test_cases, json_path, "json")
        if success:
            print(f"✅ Exported test cases to: {json_path}")
            
    except Exception as e:
        print(f"❌ Error exporting results: {e}")
        return
    
    print("\n🎉 Workflow completed successfully!")
    print("\nGenerated files:")
    print("  - output/test_cases.xlsx (Excel format)")
    print("  - output/traceability_matrix.xlsx (Traceability matrix)")
    print("  - output/test_cases.json (JSON format)")

if __name__ == "__main__":
    main()
```

## Advanced Features

### 1. Custom Compliance Standards

```python
from input_parsing import ComplianceMapper

# Add custom compliance standard
mapper = ComplianceMapper()
mapper.add_custom_standard(
    "CUSTOM_STD_001",
    "Custom Healthcare Standard",
    patterns=["custom requirement", "special validation"],
    evidence_required=["custom documentation", "validation records"]
)
```

### 2. Test Case Refinement

```python
# Refine test case using natural language
refined_tc = generator.refine_test_case(
    test_case,
    "Add negative test scenarios for invalid patient data input"
)
```

### 3. Compliance Validation

```python
from test_case_generation import ComplianceValidator

# Validate test case compliance
validator = ComplianceValidator()
report = validator.validate_test_case(test_case, ["FDA_21_CFR_820"])

print(f"Compliance score: {report.compliance_score}")
print(f"Overall compliance: {report.overall_compliance.value}")
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
```
Error: Google AI API key not found
Solution: Set GOOGLE_AI_API_KEY environment variable
```

#### 2. Document Format Not Supported
```
Error: Unsupported file format
Solution: Convert document to PDF, DOCX, XML, or HTML format
```

#### 3. Memory Issues with Large Documents
```
Error: Out of memory
Solution: Split large documents into smaller sections
```

### Getting Help

1. **Check Documentation**: Review the comprehensive API documentation
2. **Run Examples**: Try the provided example scripts
3. **Check Logs**: Enable debug logging for detailed error information
4. **Community Support**: Join our community discussions

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for more use cases
2. **Read Documentation**: Review the full API documentation
3. **Customize Configuration**: Modify settings in `config.py`
4. **Integrate with Tools**: Connect with your existing test management tools

## Support

- **Documentation**: [Full Documentation](docs/)
- **API Reference**: [API Documentation](docs/api_docs/)
- **Examples**: [Usage Examples](examples/)
- **Issues**: [GitHub Issues](https://github.com/your-username/healthcare-ai-testcase-generator/issues)

---

**Congratulations! You're now ready to use the Healthcare AI Test Case Generator. Start with the basic workflow and gradually explore the advanced features as you become more familiar with the system.**
