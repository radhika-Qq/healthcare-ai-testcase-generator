"""
Unit tests for Compliance Validator module
"""

import pytest
from test_case_generation.compliance_validator import (
    ComplianceValidator, 
    ComplianceCheck, 
    ComplianceValidationReport,
    ComplianceLevel,
    ValidationResult
)
from test_case_generation.test_case_generator import TestCase, TestStep, TestCaseType, TestCasePriority


class TestComplianceValidator:
    """Test cases for ComplianceValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ComplianceValidator()
        
    def test_validator_initialization(self):
        """Test validator initialization."""
        assert self.validator is not None
        assert hasattr(self.validator, 'validation_rules')
        assert hasattr(self.validator, 'compliance_requirements')
        
    def test_validate_test_case_fda_compliance(self):
        """Test FDA compliance validation."""
        # Create test case with FDA compliance references
        test_case = TestCase(
            id="TC-001",
            title="FDA Compliance Test",
            description="Test case for FDA 21 CFR 820 compliance validation",
            test_case_type=TestCaseType.COMPLIANCE,
            priority=TestCasePriority.HIGH,
            requirement_id="REQ-001",
            compliance_refs=["FDA_21_CFR_820"],
            test_steps=[
                TestStep(
                    step_number=1,
                    action="Verify design controls documentation",
                    expected_result="Design controls are properly documented"
                )
            ],
            prerequisites=["System is configured"],
            expected_outcome="FDA compliance validated"
        )
        
        # Validate test case
        report = self.validator.validate_test_case(test_case, ["FDA_21_CFR_820"])
        
        # Verify validation report
        assert isinstance(report, ComplianceValidationReport)
        assert report.test_case_id == "TC-001"
        assert report.overall_compliance in [ComplianceLevel.FULLY_COMPLIANT, 
                                           ComplianceLevel.PARTIALLY_COMPLIANT,
                                           ComplianceLevel.NON_COMPLIANT]
        assert 0 <= report.compliance_score <= 100
        assert len(report.checks) > 0
        assert isinstance(report.recommendations, list)
        
    def test_validate_test_case_iso_compliance(self):
        """Test ISO 13485 compliance validation."""
        test_case = TestCase(
            id="TC-002",
            title="ISO Compliance Test",
            description="Test case for ISO 13485 quality management compliance",
            test_case_type=TestCaseType.COMPLIANCE,
            priority=TestCasePriority.HIGH,
            requirement_id="REQ-002",
            compliance_refs=["ISO_13485"],
            test_steps=[
                TestStep(
                    step_number=1,
                    action="Verify quality management system",
                    expected_result="Quality management system is implemented"
                )
            ],
            prerequisites=["Quality system is established"],
            expected_outcome="ISO compliance validated"
        )
        
        report = self.validator.validate_test_case(test_case, ["ISO_13485"])
        
        assert report.test_case_id == "TC-002"
        assert report.overall_compliance in [ComplianceLevel.FULLY_COMPLIANT,
                                           ComplianceLevel.PARTIALLY_COMPLIANT,
                                           ComplianceLevel.NON_COMPLIANT]
        assert 0 <= report.compliance_score <= 100
        
    def test_validate_test_case_gdpr_compliance(self):
        """Test GDPR compliance validation."""
        test_case = TestCase(
            id="TC-003",
            title="GDPR Compliance Test",
            description="Test case for GDPR data protection compliance",
            test_case_type=TestCaseType.COMPLIANCE,
            priority=TestCasePriority.HIGH,
            requirement_id="REQ-003",
            compliance_refs=["GDPR"],
            test_steps=[
                TestStep(
                    step_number=1,
                    action="Verify data protection measures",
                    expected_result="Data protection is properly implemented"
                )
            ],
            prerequisites=["Privacy settings are configured"],
            expected_outcome="GDPR compliance validated"
        )
        
        report = self.validator.validate_test_case(test_case, ["GDPR"])
        
        assert report.test_case_id == "TC-003"
        assert report.overall_compliance in [ComplianceLevel.FULLY_COMPLIANT,
                                           ComplianceLevel.PARTIALLY_COMPLIANT,
                                           ComplianceLevel.NON_COMPLIANT]
        
    def test_perform_compliance_check(self):
        """Test individual compliance check."""
        rule = {
            'check_id': 'TEST_CHECK_001',
            'check_name': 'Test Compliance Check',
            'clause': 'Test Clause',
            'pattern': r'(test|validation|compliance)',
            'required_elements': ['test_element', 'validation_element'],
            'severity': 'high'
        }
        
        test_case = TestCase(
            id="TC-004",
            title="Test Compliance Check",
            description="Test case for compliance validation testing",
            test_case_type=TestCaseType.COMPLIANCE,
            priority=TestCasePriority.MEDIUM,
            requirement_id="REQ-004",
            compliance_refs=["TEST_STANDARD"],
            test_steps=[],
            prerequisites=[],
            expected_outcome="Test compliance validated"
        )
        
        check = self.validator._perform_compliance_check(test_case, rule, "TEST_STANDARD")
        
        assert isinstance(check, ComplianceCheck)
        assert check.check_id == "TEST_CHECK_001"
        assert check.check_name == "Test Compliance Check"
        assert check.standard == "TEST_STANDARD"
        assert check.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        assert check.severity == "high"
        
    def test_extract_test_case_content(self):
        """Test test case content extraction."""
        test_case = TestCase(
            id="TC-005",
            title="Content Extraction Test",
            description="Test case for content extraction functionality",
            test_case_type=TestCaseType.POSITIVE,
            priority=TestCasePriority.MEDIUM,
            requirement_id="REQ-005",
            compliance_refs=["TEST_STANDARD"],
            test_steps=[
                TestStep(
                    step_number=1,
                    action="Extract content from test case",
                    expected_result="Content is properly extracted"
                ),
                TestStep(
                    step_number=2,
                    action="Validate extracted content",
                    expected_result="Content validation passes"
                )
            ],
            prerequisites=["Test environment is ready"],
            expected_outcome="Content extraction successful",
            pass_criteria=["Content is extracted", "Validation passes"],
            fail_criteria=["Content extraction fails", "Validation fails"]
        )
        
        content = self.validator._extract_test_case_content(test_case)
        
        assert "Content Extraction Test" in content
        assert "Test case for content extraction" in content
        assert "Extract content from test case" in content
        assert "Content is properly extracted" in content
        assert "Content is extracted" in content
        assert "Content extraction fails" in content
        
    def test_check_required_elements(self):
        """Test required elements checking."""
        content = "This is a test validation compliance check"
        required_elements = ["test", "validation", "compliance", "missing_element"]
        
        coverage = self.validator._check_required_elements(content, required_elements)
        
        # Should find 3 out of 4 elements (75% coverage)
        assert coverage == 0.75
        
    def test_get_evidence_requirements(self):
        """Test evidence requirements retrieval."""
        evidence = self.validator._get_evidence_requirements("FDA_21_CFR_820", "FDA_820_30_1")
        
        assert isinstance(evidence, list)
        assert len(evidence) > 0
        assert all(isinstance(req, str) for req in evidence)
        
    def test_identify_evidence_gaps(self):
        """Test evidence gap identification."""
        test_case = TestCase(
            id="TC-006",
            title="Evidence Gap Test",
            description="Test case for evidence gap identification",
            test_case_type=TestCaseType.COMPLIANCE,
            priority=TestCasePriority.MEDIUM,
            requirement_id="REQ-006",
            compliance_refs=["FDA_21_CFR_820"],
            test_steps=[],
            prerequisites=[],
            expected_outcome="Evidence gaps identified"
        )
        
        gaps = self.validator._identify_evidence_gaps(test_case, ["FDA_21_CFR_820"])
        
        assert isinstance(gaps, list)
        # Should identify gaps for missing evidence requirements
        
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        checks = [
            ComplianceCheck(
                check_id="CHECK_001",
                check_name="Failed Check",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.FAIL,
                message="Test check failed",
                evidence_required=["evidence1", "evidence2"],
                severity="critical"
            ),
            ComplianceCheck(
                check_id="CHECK_002",
                check_name="Warning Check",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.WARNING,
                message="Test check warning",
                evidence_required=["evidence3"],
                severity="high"
            )
        ]
        
        evidence_gaps = ["TEST_STANDARD: Missing evidence1", "TEST_STANDARD: Missing evidence2"]
        
        recommendations = self.validator._generate_recommendations(checks, evidence_gaps)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
        
        # Should contain recommendations for failed checks
        assert any("Failed Check" in rec for rec in recommendations)
        assert any("Warning Check" in rec for rec in recommendations)
        assert any("evidence gaps" in rec.lower() for rec in recommendations)
        
    def test_calculate_compliance_score(self):
        """Test compliance score calculation."""
        checks = [
            ComplianceCheck(
                check_id="CHECK_001",
                check_name="Critical Pass",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.PASS,
                message="Test check passed",
                evidence_required=[],
                severity="critical"
            ),
            ComplianceCheck(
                check_id="CHECK_002",
                check_name="High Warning",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.WARNING,
                message="Test check warning",
                evidence_required=[],
                severity="high"
            ),
            ComplianceCheck(
                check_id="CHECK_003",
                check_name="Medium Fail",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.FAIL,
                message="Test check failed",
                evidence_required=[],
                severity="medium"
            )
        ]
        
        score = self.validator._calculate_compliance_score(checks)
        
        # Score should be weighted average: (100*4 + 70*3 + 0*2) / (4+3+2) = 610/9 ≈ 67.8
        expected_score = (100 * 4 + 70 * 3 + 0 * 2) / (4 + 3 + 2)
        assert abs(score - expected_score) < 0.1
        
    def test_determine_compliance_level(self):
        """Test compliance level determination."""
        # Test with high score and no critical failures
        high_score_checks = [
            ComplianceCheck(
                check_id="CHECK_001",
                check_name="High Pass",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.PASS,
                message="Test check passed",
                evidence_required=[],
                severity="high"
            )
        ]
        
        level = self.validator._determine_compliance_level(95.0, high_score_checks)
        assert level == ComplianceLevel.FULLY_COMPLIANT
        
        # Test with medium score
        level = self.validator._determine_compliance_level(75.0, high_score_checks)
        assert level == ComplianceLevel.PARTIALLY_COMPLIANT
        
        # Test with low score
        level = self.validator._determine_compliance_level(50.0, high_score_checks)
        assert level == ComplianceLevel.NON_COMPLIANT
        
        # Test with critical failures
        critical_fail_checks = [
            ComplianceCheck(
                check_id="CHECK_001",
                check_name="Critical Fail",
                standard="TEST_STANDARD",
                clause="Test Clause",
                result=ValidationResult.FAIL,
                message="Critical check failed",
                evidence_required=[],
                severity="critical"
            )
        ]
        
        level = self.validator._determine_compliance_level(95.0, critical_fail_checks)
        assert level == ComplianceLevel.NON_COMPLIANT
        
    def test_generate_compliance_summary(self):
        """Test compliance summary generation."""
        reports = [
            ComplianceValidationReport(
                test_case_id="TC-001",
                overall_compliance=ComplianceLevel.FULLY_COMPLIANT,
                compliance_score=95.0,
                checks=[],
                recommendations=[],
                evidence_gaps=[],
                validation_timestamp="2024-01-01T00:00:00"
            ),
            ComplianceValidationReport(
                test_case_id="TC-002",
                overall_compliance=ComplianceLevel.PARTIALLY_COMPLIANT,
                compliance_score=75.0,
                checks=[],
                recommendations=[],
                evidence_gaps=[],
                validation_timestamp="2024-01-01T00:00:00"
            ),
            ComplianceValidationReport(
                test_case_id="TC-003",
                overall_compliance=ComplianceLevel.NON_COMPLIANT,
                compliance_score=45.0,
                checks=[],
                recommendations=[],
                evidence_gaps=[],
                validation_timestamp="2024-01-01T00:00:00"
            )
        ]
        
        summary = self.validator.generate_compliance_summary(reports)
        
        assert isinstance(summary, dict)
        assert 'summary' in summary
        assert summary['summary']['total_test_cases'] == 3
        assert summary['summary']['fully_compliant'] == 1
        assert summary['summary']['partially_compliant'] == 1
        assert summary['summary']['non_compliant'] == 1
        assert summary['summary']['average_compliance_score'] == 71.7  # (95+75+45)/3
        
    def test_empty_validation_reports(self):
        """Test handling of empty validation reports."""
        summary = self.validator.generate_compliance_summary([])
        
        assert 'error' in summary
        assert summary['error'] == 'No validation reports provided'
        
    def test_validation_rules_initialization(self):
        """Test validation rules initialization."""
        assert 'FDA_21_CFR_820' in self.validator.validation_rules
        assert 'ISO_13485' in self.validator.validation_rules
        assert 'IEC_62304' in self.validator.validation_rules
        assert 'GDPR' in self.validator.validation_rules
        
        # Check that each standard has validation rules
        for standard, rules in self.validator.validation_rules.items():
            assert isinstance(rules, list)
            assert len(rules) > 0
            for rule in rules:
                assert 'check_id' in rule
                assert 'check_name' in rule
                assert 'clause' in rule
                assert 'pattern' in rule
                assert 'required_elements' in rule
                assert 'severity' in rule
                
    def test_compliance_requirements_initialization(self):
        """Test compliance requirements initialization."""
        assert 'FDA_21_CFR_820' in self.validator.compliance_requirements
        assert 'ISO_13485' in self.validator.compliance_requirements
        assert 'IEC_62304' in self.validator.compliance_requirements
        assert 'GDPR' in self.validator.compliance_requirements
        
        # Check that each standard has requirements
        for standard, requirements in self.validator.compliance_requirements.items():
            assert 'name' in requirements
            assert 'description' in requirements
            assert 'required_evidence' in requirements
            assert 'critical_areas' in requirements
            assert isinstance(requirements['required_evidence'], list)
            assert isinstance(requirements['critical_areas'], list)

