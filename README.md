# Healthcare AI Test Case Generator

A comprehensive AI-powered tool for generating compliant, traceable test cases from healthcare software requirements using Google Vertex AI and Gemini APIs.

## Project Overview

This project aims to streamline the test case generation process for healthcare software by:
- Parsing healthcare software requirements from various document formats
- Extracting functional and non-functional requirements with regulatory compliance mapping
- Generating detailed, traceable test cases that meet FDA, ISO 13485, IEC 62304, and GDPR standards
- Exporting test cases in formats compatible with enterprise tools (Jira, Azure DevOps)

## Project Structure

```
healthcare-ai-testcase-generator/
├── input_parsing/           # Input & Parsing Module
│   ├── __init__.py
│   ├── document_parser.py   # PDF, Word, XML parsing
│   ├── requirement_extractor.py  # AI-powered requirement extraction
│   ├── compliance_mapper.py # Regulatory compliance mapping
│   └── utils.py            # Helper functions
├── test_case_generation/    # Test Case Generation & Output Module
│   ├── __init__.py
│   ├── test_case_generator.py  # AI-powered test case generation
│   ├── compliance_validator.py # Compliance validation
│   ├── export_formats.py   # Jira, Azure DevOps, Excel export
│   └── traceability_matrix.py  # Traceability matrix generation
├── docs/                   # Documentation
│   ├── design_docs/
│   ├── api_docs/
│   └── prompts/
├── scripts/               # Deployment and integration helpers
│   ├── setup_environment.py
│   └── deploy.py
├── tests/                 # Unit and integration tests
├── examples/              # Example inputs and outputs
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## Features

### Input & Parsing Module
- **Document Processing**: Parse PDFs, Word documents, and XML healthcare specifications
- **Requirement Extraction**: AI-powered extraction of functional and non-functional requirements
- **Compliance Mapping**: Automatic identification of FDA, ISO 13485, IEC 62304, and GDPR clauses
- **Structured Output**: Convert parsed data to standardized JSON format

### Test Case Generation & Output Module
- **AI-Powered Generation**: Generate detailed test cases using Google Vertex AI
- **Compliance Integration**: Include regulatory standard references in test cases
- **Multiple Export Formats**: Support for JSON, Excel, Jira, and Azure DevOps formats
- **Traceability Matrix**: Generate comprehensive traceability documentation
- **Natural Language Refinement**: Allow prompt-based test case modifications

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/healthcare-ai-testcase-generator.git
   cd healthcare-ai-testcase-generator
   ```

2. **Set up the environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud credentials**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

4. **Run the example**
   ```bash
   python examples/basic_usage.py
   ```

## Development Branches

- `main`: Production-ready code
- `parsing-module`: Development branch for Input & Parsing Module
- `generation-module`: Development branch for Test Case Generation & Output Module

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue in the GitHub repository.

