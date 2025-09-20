# Input & Parsing Module Prompts

This document contains the AI prompts used in the Input & Parsing Module for extracting and processing healthcare software requirements.

## Document Parsing Prompts

### PDF Document Parsing
```
Extract all functional and non-functional requirements from the following healthcare software specification document, identifying key entities, conditions, and expected behaviors with context.

Focus on:
- Patient safety requirements
- Data privacy and security requirements
- Regulatory compliance requirements
- Medical device functionality
- Clinical workflow integration
- Risk management requirements

Document content: [DOCUMENT_TEXT]
```

### Word Document Parsing
```
Parse the following healthcare software requirements document and extract structured information including:

1. Requirement identification numbers
2. Requirement descriptions
3. Requirement types (functional, non-functional, performance, security, compliance)
4. Priority levels
5. Compliance references (FDA, ISO, IEC, GDPR)
6. Acceptance criteria
7. Dependencies

Document content: [DOCUMENT_TEXT]
```

### XML Healthcare Specification Parsing
```
Convert the following XML healthcare specification into clean, machine-readable text while preserving hierarchy and semantics.

Extract:
- Requirement elements with attributes
- Hierarchical structure
- Compliance references
- Data types and constraints
- Validation rules

XML content: [XML_CONTENT]
```

## Requirement Extraction Prompts

### Functional Requirements Extraction
```
Extract all functional requirements from the following healthcare software specification, identifying:

1. System behaviors and capabilities
2. User interactions and workflows
3. Data processing requirements
4. Integration requirements
5. Business logic requirements

For each requirement, provide:
- Unique requirement ID
- Clear, testable description
- Input/output specifications
- Preconditions and postconditions
- Success criteria

Requirements text: [REQUIREMENTS_TEXT]
```

### Non-Functional Requirements Extraction
```
Extract all non-functional requirements from the following healthcare software specification, identifying:

1. Performance requirements (response time, throughput, scalability)
2. Security requirements (authentication, authorization, encryption)
3. Usability requirements (user interface, accessibility)
4. Reliability requirements (availability, fault tolerance)
5. Compliance requirements (regulatory standards)

For each requirement, provide:
- Requirement ID
- Measurable criteria
- Performance metrics
- Compliance references
- Validation methods

Requirements text: [REQUIREMENTS_TEXT]
```

### Compliance Requirements Extraction
```
Identify regulatory clauses related to FDA, ISO 13485, IEC 62304, and GDPR from the following input documents for traceability linking.

Extract:
1. Specific regulatory references
2. Compliance requirements
3. Evidence requirements
4. Validation criteria
5. Audit trail requirements

For each compliance requirement, provide:
- Regulatory standard and clause
- Requirement description
- Evidence needed
- Traceability level
- Implementation guidance

Document content: [DOCUMENT_TEXT]
```

## Data Standardization Prompts

### Requirement Summarization
```
Summarize each requirement into a concise, standardized format suitable for test case creation, including priority and compliance references if present.

For each requirement, provide:
1. Standardized requirement ID (REQ-XXX format)
2. Concise description (max 200 words)
3. Requirement type classification
4. Priority level (critical, high, medium, low)
5. Compliance references
6. Testability criteria
7. Dependencies

Requirements: [REQUIREMENTS_LIST]
```

### JSON Structure Generation
```
Return parsed data as a structured JSON object containing requirement ID, description, type, and compliance attributes.

JSON structure should include:
- requirements: array of requirement objects
- compliance_mappings: array of compliance mappings
- traceability_matrix: requirement to compliance mapping
- summary: statistical summary

Requirements data: [PARSED_DATA]
```

## Healthcare-Specific Processing Prompts

### Patient Safety Requirements
```
Extract patient safety requirements from the following healthcare software specification, focusing on:

1. Risk mitigation requirements
2. Safety validation requirements
3. Error prevention requirements
4. Emergency response requirements
5. Clinical decision support requirements

For each safety requirement, identify:
- Safety classification level
- Risk factors addressed
- Mitigation strategies
- Validation requirements
- Monitoring criteria

Document content: [DOCUMENT_TEXT]
```

### Data Privacy Requirements
```
Extract data privacy and protection requirements from the following healthcare software specification, focusing on:

1. Personal health information (PHI) protection
2. Data encryption requirements
3. Access control requirements
4. Audit logging requirements
5. Consent management requirements

For each privacy requirement, identify:
- Data types protected
- Protection mechanisms
- Compliance standards
- Access controls
- Audit requirements

Document content: [DOCUMENT_TEXT]
```

### Medical Device Integration
```
Extract medical device integration requirements from the following healthcare software specification, focusing on:

1. Device communication protocols
2. Data exchange standards (HL7, FHIR, DICOM)
3. Device safety requirements
4. Interoperability requirements
5. Device management requirements

For each integration requirement, identify:
- Device types supported
- Communication protocols
- Data formats
- Safety considerations
- Compliance requirements

Document content: [DOCUMENT_TEXT]
```

## Quality Assurance Prompts

### Requirement Validation
```
Validate the following extracted requirements for completeness, clarity, and testability:

1. Check for missing information
2. Verify requirement clarity
3. Ensure testability
4. Validate compliance references
5. Check for conflicts or contradictions

For each requirement, provide:
- Validation status
- Issues identified
- Recommendations for improvement
- Completeness score

Requirements: [EXTRACTED_REQUIREMENTS]
```

### Consistency Checking
```
Check the following requirements for consistency and coherence:

1. Terminology consistency
2. Priority alignment
3. Compliance reference accuracy
4. Dependency validation
5. Conflict identification

For each issue found, provide:
- Issue description
- Severity level
- Recommended resolution
- Impact assessment

Requirements: [REQUIREMENTS_LIST]
```

## Error Handling Prompts

### Document Parsing Error Recovery
```
The following document parsing encountered errors. Attempt to recover and extract as much information as possible:

1. Identify recoverable sections
2. Extract partial requirements
3. Flag problematic areas
4. Suggest manual review needs
5. Provide partial results

Error details: [ERROR_INFO]
Document content: [DOCUMENT_TEXT]
```

### Requirement Extraction Fallback
```
The AI-based requirement extraction failed. Use rule-based extraction to identify requirements:

1. Look for requirement patterns
2. Extract key phrases
3. Identify compliance references
4. Generate basic requirement structure
5. Flag for manual review

Document content: [DOCUMENT_TEXT]
```

## Integration Prompts

### API Integration
```
Integrate with the following healthcare API to extract requirements:

1. Authenticate with the API
2. Retrieve requirement documents
3. Parse API responses
4. Extract requirement data
5. Format for processing

API endpoint: [API_ENDPOINT]
Authentication: [AUTH_INFO]
```

### Database Integration
```
Extract requirements from the following healthcare database:

1. Connect to database
2. Query requirement tables
3. Extract requirement data
4. Parse structured data
5. Format for processing

Database connection: [DB_CONNECTION]
Query: [SQL_QUERY]
```

These prompts are designed to work with various AI models and can be customized based on specific healthcare domain requirements and compliance standards.

