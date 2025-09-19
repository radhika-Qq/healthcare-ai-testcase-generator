# Test Case Generation & Output Module Prompts

This document contains the AI prompts used in the Test Case Generation & Output Module for creating compliant, traceable test cases from healthcare requirements.

## Test Case Generation Prompts

### Basic Test Case Generation
```
Generate detailed test cases including Case ID, title, description, step-by-step actions, expected results, and priority based on the provided healthcare requirement input.

For each test case, include:
1. Unique test case ID (TC-XXX format)
2. Descriptive title
3. Detailed description
4. Test case type (positive, negative, boundary, integration, performance, security, usability, compliance)
5. Priority level (critical, high, medium, low)
6. Step-by-step test actions
7. Expected results for each step
8. Prerequisites and test data requirements
9. Pass/fail criteria
10. Estimated duration

Requirement: [REQUIREMENT_DETAILS]
```

### Healthcare-Specific Test Case Generation
```
Generate healthcare-specific test cases for the following requirement, ensuring compliance with FDA, ISO, and other regulatory standards:

Focus on:
1. Patient safety validation
2. Data privacy and security testing
3. Regulatory compliance verification
4. Medical device functionality testing
5. Clinical workflow validation
6. Audit trail verification
7. Risk management validation

For each test case, include:
- Healthcare-specific test scenarios
- Compliance validation steps
- Safety verification procedures
- Data protection testing
- Regulatory requirement validation

Requirement: [HEALTHCARE_REQUIREMENT]
Compliance References: [COMPLIANCE_REFS]
```

### Positive Test Case Generation
```
Generate positive test cases for the following healthcare requirement, ensuring all valid scenarios are covered:

1. Happy path scenarios
2. Valid input combinations
3. Expected system behaviors
4. Success criteria validation
5. Performance under normal conditions

For each positive test case, include:
- Clear test objectives
- Step-by-step actions
- Expected outcomes
- Success validation criteria
- Test data requirements

Requirement: [REQUIREMENT_DETAILS]
```

### Negative Test Case Generation
```
Generate negative test cases for the following healthcare requirement, ensuring proper error handling and edge cases:

1. Invalid input scenarios
2. Boundary value testing
3. Error condition handling
4. Security violation attempts
5. Compliance violation scenarios

For each negative test case, include:
- Error condition description
- Invalid input data
- Expected error responses
- Error handling validation
- Recovery procedures

Requirement: [REQUIREMENT_DETAILS]
```

### Boundary Value Testing
```
Generate boundary value test cases for the following healthcare requirement, focusing on:

1. Minimum and maximum values
2. Edge case scenarios
3. Limit testing
4. Threshold validation
5. Range boundary testing

For each boundary test case, include:
- Boundary value identification
- Test scenarios at limits
- Expected behavior validation
- Edge case handling
- Performance impact assessment

Requirement: [REQUIREMENT_DETAILS]
```

## Compliance-Focused Test Case Generation

### FDA Compliance Test Cases
```
Generate test cases that ensure compliance with FDA 21 CFR 820 (Quality System Regulation) for the following requirement:

Focus on:
1. Design controls validation
2. Risk management verification
3. Design review compliance
4. Verification and validation testing
5. Corrective and preventive action testing

For each test case, include:
- FDA compliance validation steps
- Evidence collection procedures
- Audit trail verification
- Quality system requirements
- Regulatory documentation

Requirement: [REQUIREMENT_DETAILS]
FDA References: [FDA_REFS]
```

### ISO 13485 Compliance Test Cases
```
Generate test cases that ensure compliance with ISO 13485 (Medical Devices Quality Management) for the following requirement:

Focus on:
1. Quality management system validation
2. Risk management verification
3. Design and development compliance
4. Production and service provision testing
5. Management review validation

For each test case, include:
- ISO compliance validation steps
- Quality system requirements
- Process validation procedures
- Documentation requirements
- Continuous improvement validation

Requirement: [REQUIREMENT_DETAILS]
ISO References: [ISO_REFS]
```

### IEC 62304 Compliance Test Cases
```
Generate test cases that ensure compliance with IEC 62304 (Medical Device Software) for the following requirement:

Focus on:
1. Software life cycle process validation
2. Software safety classification testing
3. Software risk management verification
4. Software development process testing
5. Software maintenance validation

For each test case, include:
- IEC compliance validation steps
- Software safety requirements
- Risk management procedures
- Development process validation
- Maintenance requirements

Requirement: [REQUIREMENT_DETAILS]
IEC References: [IEC_REFS]
```

### GDPR Compliance Test Cases
```
Generate test cases that ensure compliance with GDPR (General Data Protection Regulation) for the following requirement:

Focus on:
1. Data protection by design validation
2. Privacy impact assessment testing
3. Consent management verification
4. Data subject rights testing
5. Data breach response validation

For each test case, include:
- GDPR compliance validation steps
- Privacy protection procedures
- Data subject rights verification
- Consent management testing
- Data breach response validation

Requirement: [REQUIREMENT_DETAILS]
GDPR References: [GDPR_REFS]
```

## Test Case Refinement Prompts

### Natural Language Refinement
```
Refine the following test case based on the natural language instruction:

Original Test Case: [TEST_CASE_DETAILS]
Refinement Instruction: [REFINEMENT_PROMPT]

Provide the refined test case with:
1. Updated test steps
2. Modified expected results
3. Adjusted test data
4. Updated pass/fail criteria
5. Revised duration estimates

Ensure the refined test case maintains:
- Compliance with healthcare standards
- Traceability to requirements
- Testability and clarity
- Regulatory compliance
```

### Priority Adjustment
```
Adjust the priority of the following test case based on the healthcare requirement priority and compliance requirements:

Test Case: [TEST_CASE_DETAILS]
Requirement Priority: [REQUIREMENT_PRIORITY]
Compliance Level: [COMPLIANCE_LEVEL]

Consider:
1. Patient safety impact
2. Regulatory compliance criticality
3. Business impact
4. Risk assessment
5. Compliance requirements

Provide updated priority with justification.
```

### Test Case Enhancement
```
Enhance the following test case by adding additional test scenarios:

Original Test Case: [TEST_CASE_DETAILS]
Enhancement Request: [ENHANCEMENT_REQUEST]

Add:
1. Additional test steps
2. More comprehensive test data
3. Edge case scenarios
4. Negative test cases
5. Performance test cases

Ensure enhancements maintain:
- Test case coherence
- Compliance requirements
- Traceability
- Testability
```

## Export Format Prompts

### Jira Export Format
```
Format the following test cases for Jira import:

Test Cases: [TEST_CASES_LIST]
Jira Configuration:
- Project Key: [PROJECT_KEY]
- Issue Type: [ISSUE_TYPE]
- Custom Fields: [CUSTOM_FIELDS]

For each test case, create:
1. Jira issue summary
2. Detailed description with test steps
3. Priority mapping
4. Labels and components
5. Custom field values
6. Compliance references

Ensure Jira compatibility and proper formatting.
```

### Azure DevOps Export Format
```
Format the following test cases for Azure DevOps import:

Test Cases: [TEST_CASES_LIST]
Azure DevOps Configuration:
- Organization: [ORGANIZATION]
- Project: [PROJECT]
- Work Item Type: [WORK_ITEM_TYPE]

For each test case, create:
1. Work item title and description
2. Test case steps
3. Priority and severity mapping
4. Tags and categories
5. Custom field values
6. Compliance references

Ensure Azure DevOps compatibility and proper formatting.
```

### Excel Export Format
```
Format the following test cases for Excel export:

Test Cases: [TEST_CASES_LIST]
Excel Configuration:
- Include traceability matrix
- Include compliance mapping
- Include summary statistics

Create worksheets:
1. Test Cases (detailed view)
2. Summary (statistics)
3. Traceability Matrix
4. Compliance Mapping

Ensure proper formatting, formulas, and data validation.
```

## Traceability Matrix Prompts

### Requirement-to-Test-Case Mapping
```
Create a traceability matrix mapping requirements to test cases:

Requirements: [REQUIREMENTS_LIST]
Test Cases: [TEST_CASES_LIST]

For each mapping, include:
1. Requirement ID and description
2. Associated test case IDs
3. Traceability level (direct, indirect, related)
4. Coverage status (covered, partial, not covered)
5. Compliance references
6. Evidence requirements

Ensure comprehensive coverage and clear traceability.
```

### Compliance Traceability Matrix
```
Create a compliance traceability matrix linking requirements, test cases, and compliance standards:

Requirements: [REQUIREMENTS_LIST]
Test Cases: [TEST_CASES_LIST]
Compliance Standards: [COMPLIANCE_STANDARDS]

For each compliance standard, include:
1. Standard name and version
2. Applicable requirements
3. Associated test cases
4. Compliance validation steps
5. Evidence requirements
6. Audit trail information

Ensure regulatory compliance and audit readiness.
```

## Quality Assurance Prompts

### Test Case Validation
```
Validate the following test cases for quality and completeness:

Test Cases: [TEST_CASES_LIST]

Check for:
1. Test case completeness
2. Step clarity and testability
3. Expected result accuracy
4. Compliance coverage
5. Traceability accuracy
6. Priority alignment

For each issue found, provide:
- Issue description
- Severity level
- Recommended fix
- Impact assessment
```

### Compliance Validation
```
Validate the following test cases for regulatory compliance:

Test Cases: [TEST_CASES_LIST]
Compliance Standards: [COMPLIANCE_STANDARDS]

Check for:
1. Regulatory requirement coverage
2. Compliance validation steps
3. Evidence collection procedures
4. Audit trail requirements
5. Documentation completeness

For each compliance issue, provide:
- Compliance gap description
- Regulatory requirement
- Recommended test case updates
- Evidence requirements
```

## Error Handling Prompts

### Test Case Generation Error Recovery
```
The test case generation encountered errors. Attempt to recover and generate as many test cases as possible:

Error Details: [ERROR_INFO]
Requirements: [REQUIREMENTS_LIST]

Recovery strategy:
1. Identify recoverable requirements
2. Generate basic test cases
3. Flag problematic areas
4. Suggest manual review
5. Provide partial results

Ensure maximum coverage with available data.
```

### Export Format Error Handling
```
The export to [FORMAT] encountered errors. Attempt to recover and export in alternative formats:

Error Details: [ERROR_INFO]
Test Cases: [TEST_CASES_LIST]

Recovery options:
1. Export to alternative format
2. Fix formatting issues
3. Provide manual export instructions
4. Generate partial export
5. Suggest format-specific solutions

Ensure data integrity and usability.
```

These prompts are designed to work with various AI models and can be customized based on specific healthcare domain requirements, compliance standards, and export format needs.
