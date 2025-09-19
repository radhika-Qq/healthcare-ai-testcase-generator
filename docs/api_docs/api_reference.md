# API Reference

This document provides detailed API reference for the Healthcare AI Test Case Generator.

## Input & Parsing Module

### DocumentParser

The `DocumentParser` class handles parsing of various document formats.

#### Methods

##### `parse_document(file_path: Union[str, Path]) -> Dict[str, Any]`

Parse a healthcare document and extract structured content.

**Parameters:**
- `file_path`: Path to the document file

**Returns:**
- Dictionary containing parsed content and metadata

**Raises:**
- `FileNotFoundError`: If document not found
- `ValueError`: If unsupported file format

**Example:**
```python
from input_parsing import DocumentParser

parser = DocumentParser()
parsed_doc = parser.parse_document("requirements.pdf")
```

##### `extract_clean_text(parsed_doc: Dict[str, Any]) -> str`

Extract clean, machine-readable text from parsed document.

**Parameters:**
- `parsed_doc`: Parsed document dictionary

**Returns:**
- Clean text content

##### `extract_hierarchy(parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]`

Extract hierarchical structure from parsed document.

**Parameters:**
- `parsed_doc`: Parsed document dictionary

**Returns:**
- List of hierarchical elements with levels

### RequirementExtractor

The `RequirementExtractor` class extracts requirements from parsed documents using AI.

#### Methods

##### `__init__(api_key: Optional[str] = None, project_id: Optional[str] = None)`

Initialize the requirement extractor.

**Parameters:**
- `api_key`: Google AI API key
- `project_id`: Google Cloud project ID

##### `extract_requirements(parsed_doc: Dict[str, Any]) -> List[Requirement]`

Extract requirements from parsed document.

**Parameters:**
- `parsed_doc`: Parsed document dictionary

**Returns:**
- List of extracted requirements

##### `summarize_requirements(requirements: List[Requirement]) -> Dict[str, Any]`

Summarize extracted requirements into standardized format.

**Parameters:**
- `requirements`: List of extracted requirements

**Returns:**
- Summary dictionary

### ComplianceMapper

The `ComplianceMapper` class maps requirements to compliance standards.

#### Methods

##### `map_requirement_to_compliance(requirement_text: str, requirement_id: str) -> List[ComplianceMapping]`

Map a requirement to applicable compliance standards.

**Parameters:**
- `requirement_text`: The requirement text to analyze
- `requirement_id`: Unique identifier for the requirement

**Returns:**
- List of compliance mappings

##### `generate_traceability_matrix(requirements: List[Any], mappings: List[ComplianceMapping]) -> Dict[str, Any]`

Generate a traceability matrix linking requirements to compliance standards.

**Parameters:**
- `requirements`: List of requirements
- `mappings`: List of compliance mappings

**Returns:**
- Traceability matrix dictionary

## Test Case Generation Module

### TestCaseGenerator

The `TestCaseGenerator` class generates test cases from requirements.

#### Methods

##### `__init__(api_key: Optional[str] = None, project_id: Optional[str] = None)`

Initialize the test case generator.

**Parameters:**
- `api_key`: Google AI API key
- `project_id`: Google Cloud project ID

##### `generate_test_cases(requirements: List[Dict[str, Any]], compliance_mappings: List[Dict[str, Any]] = None) -> List[TestCase]`

Generate test cases from requirements.

**Parameters:**
- `requirements`: List of parsed requirements
- `compliance_mappings`: Optional compliance mappings

**Returns:**
- List of generated test cases

##### `refine_test_case(test_case: TestCase, refinement_prompt: str) -> TestCase`

Refine test case based on natural language prompt.

**Parameters:**
- `test_case`: Test case to refine
- `refinement_prompt`: Natural language refinement instruction

**Returns:**
- Refined test case

### ComplianceValidator

The `ComplianceValidator` class validates test cases against compliance standards.

#### Methods

##### `validate_test_case(test_case: Any, compliance_refs: List[str]) -> ComplianceValidationReport`

Validate a test case against compliance standards.

**Parameters:**
- `test_case`: Test case to validate
- `compliance_refs`: List of compliance references

**Returns:**
- Compliance validation report

##### `generate_compliance_summary(validation_reports: List[ComplianceValidationReport]) -> Dict[str, Any]`

Generate summary of compliance validation across multiple test cases.

**Parameters:**
- `validation_reports`: List of validation reports

**Returns:**
- Compliance summary dictionary

### ExportManager

The `ExportManager` class handles export of test cases to various formats.

#### Methods

##### `export_test_cases(test_cases: List[Any], output_path: Union[str, Path], format_type: str = 'json', **kwargs) -> bool`

Export test cases to specified format.

**Parameters:**
- `test_cases`: List of test cases to export
- `output_path`: Path for output file
- `format_type`: Export format (json, excel, csv, jira, azure_devops)
- `**kwargs`: Additional format-specific parameters

**Returns:**
- True if export successful, False otherwise

### TraceabilityMatrixGenerator

The `TraceabilityMatrixGenerator` class generates traceability matrices.

#### Methods

##### `generate_traceability_matrix(requirements: List[Any], test_cases: List[Any], compliance_mappings: List[Any] = None) -> Dict[str, Any]`

Generate comprehensive traceability matrix.

**Parameters:**
- `requirements`: List of requirements
- `test_cases`: List of test cases
- `compliance_mappings`: Optional compliance mappings

**Returns:**
- Traceability matrix dictionary

##### `export_traceability_matrix(matrix_data: Dict[str, Any], output_path: str, format_type: str = 'excel') -> bool`

Export traceability matrix to file.

**Parameters:**
- `matrix_data`: Traceability matrix data
- `output_path`: Path for output file
- `format_type`: Export format (excel, csv, json)

**Returns:**
- True if export successful, False otherwise

## Data Classes

### Requirement

Represents a structured requirement.

```python
@dataclass
class Requirement:
    id: str
    description: str
    type: RequirementType
    priority: Priority
    source_section: str
    compliance_refs: List[str]
    context: str
    acceptance_criteria: List[str]
    dependencies: List[str]
    raw_text: str
```

### TestCase

Represents a complete test case.

```python
@dataclass
class TestCase:
    id: str
    title: str
    description: str
    test_case_type: TestCaseType
    priority: TestCasePriority
    requirement_id: str
    compliance_refs: List[str]
    test_steps: List[TestStep]
    prerequisites: List[str]
    test_data: Optional[Dict[str, Any]] = None
    expected_outcome: str = ""
    pass_criteria: List[str] = None
    fail_criteria: List[str] = None
    estimated_duration: Optional[int] = None
    created_date: str = ""
    last_modified: str = ""
```

### TestStep

Represents an individual test step.

```python
@dataclass
class TestStep:
    step_number: int
    action: str
    expected_result: str
    data_inputs: Optional[Dict[str, Any]] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
```

## Enums

### RequirementType

```python
class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    USABILITY = "usability"
    RELIABILITY = "reliability"
```

### TestCaseType

```python
class TestCaseType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPLIANCE = "compliance"
```

### Priority

```python
class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

## Utility Functions

### `parse_healthcare_document(file_path: Union[str, Path], api_key: Optional[str] = None) -> Dict[str, Any]`

Main function to parse a healthcare document and extract requirements.

**Parameters:**
- `file_path`: Path to the healthcare document
- `api_key`: Optional API key for AI services

**Returns:**
- Dictionary containing parsed document and extracted requirements

**Example:**
```python
from input_parsing import parse_healthcare_document

# Parse document and extract requirements
result = parse_healthcare_document("requirements.pdf")
requirements = result['requirements']
compliance_mappings = result['compliance_mappings']
```

## Error Handling

The API uses standard Python exceptions:

- `FileNotFoundError`: When document files are not found
- `ValueError`: When invalid parameters are provided
- `ImportError`: When required dependencies are missing
- `Exception`: For general errors with descriptive messages

## Configuration

The system can be configured using environment variables or the `config.py` file:

- `GOOGLE_AI_API_KEY`: Google AI API key
- `GOOGLE_CLOUD_PROJECT_ID`: Google Cloud project ID
- `DEFAULT_EXPORT_FORMAT`: Default export format
- `LOG_LEVEL`: Logging level

## Examples

### Basic Usage

```python
from input_parsing import parse_healthcare_document
from test_case_generation import TestCaseGenerator, ExportManager

# Parse document
result = parse_healthcare_document("requirements.pdf")

# Generate test cases
generator = TestCaseGenerator()
test_cases = generator.generate_test_cases(result['requirements'])

# Export test cases
export_manager = ExportManager()
export_manager.export_test_cases(test_cases, "output.xlsx", "excel")
```

### Advanced Usage with Compliance

```python
from input_parsing import parse_healthcare_document
from test_case_generation import TestCaseGenerator, ComplianceValidator, ExportManager

# Parse document
result = parse_healthcare_document("requirements.pdf")

# Generate test cases
generator = TestCaseGenerator()
test_cases = generator.generate_test_cases(
    result['requirements'],
    result['compliance_mappings']
)

# Validate compliance
validator = ComplianceValidator()
for tc in test_cases:
    report = validator.validate_test_case(tc, tc.compliance_refs)
    print(f"Compliance score: {report.compliance_score}")

# Export with compliance validation
export_manager = ExportManager()
export_manager.export_test_cases(test_cases, "compliant_tests.xlsx", "excel")
```
