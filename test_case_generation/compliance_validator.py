"""
Compliance Validator for Healthcare Test Cases

Validates that generated test cases meet regulatory compliance requirements
for FDA, ISO 13485, IEC 62304, and GDPR standards.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance validation levels."""
    FULLY_COMPLIANT = "fully_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


class ValidationResult(Enum):
    """Validation result types."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ComplianceCheck:
    """Individual compliance check result."""
    check_id: str
    check_name: str
    standard: str
    clause: str
    result: ValidationResult
    message: str
    evidence_required: List[str]
    severity: str  # critical, high, medium, low


@dataclass
class ComplianceValidationReport:
    """Complete compliance validation report."""
    test_case_id: str
    overall_compliance: ComplianceLevel
    compliance_score: float  # 0-100
    checks: List[ComplianceCheck]
    recommendations: List[str]
    evidence_gaps: List[str]
    validation_timestamp: str


class ComplianceValidator:
    """Validates test cases against healthcare compliance standards."""
    
    def __init__(self):
        """Initialize compliance validator with validation rules."""
        self.validation_rules = self._initialize_validation_rules()
        self.compliance_requirements = self._initialize_compliance_requirements()
        
    def _initialize_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize validation rules for different compliance standards."""
        return {
            'FDA_21_CFR_820': [
                {
                    'check_id': 'FDA_820_30_1',
                    'check_name': 'Design Controls Documentation',
                    'clause': '820.30(a)',
                    'pattern': r'(design|development|verification|validation)',
                    'required_elements': ['design_input', 'design_output', 'verification', 'validation'],
                    'severity': 'critical'
                },
                {
                    'check_id': 'FDA_820_30_2',
                    'check_name': 'Risk Management',
                    'clause': '820.30(g)',
                    'pattern': r'(risk|hazard|safety)',
                    'required_elements': ['risk_assessment', 'hazard_analysis', 'safety_validation'],
                    'severity': 'critical'
                },
                {
                    'check_id': 'FDA_820_30_3',
                    'check_name': 'Design Review',
                    'clause': '820.30(e)',
                    'pattern': r'(review|approval|signature)',
                    'required_elements': ['design_review', 'approval_process', 'signature_verification'],
                    'severity': 'high'
                }
            ],
            'FDA_21_CFR_11': [
                {
                    'check_id': 'FDA_11_10_1',
                    'check_name': 'Electronic Records Validation',
                    'clause': '11.10(a)',
                    'pattern': r'(electronic|record|validation)',
                    'required_elements': ['electronic_validation', 'record_integrity', 'audit_trail'],
                    'severity': 'critical'
                },
                {
                    'check_id': 'FDA_11_10_2',
                    'check_name': 'Electronic Signatures',
                    'clause': '11.10(b)',
                    'pattern': r'(signature|authentication|authorization)',
                    'required_elements': ['signature_validation', 'authentication', 'authorization'],
                    'severity': 'critical'
                }
            ],
            'ISO_13485': [
                {
                    'check_id': 'ISO_13485_7_3_1',
                    'check_name': 'Design and Development Planning',
                    'clause': '7.3.1',
                    'pattern': r'(design|development|planning)',
                    'required_elements': ['design_plan', 'development_process', 'quality_planning'],
                    'severity': 'high'
                },
                {
                    'check_id': 'ISO_13485_7_3_2',
                    'check_name': 'Design Inputs',
                    'clause': '7.3.2',
                    'pattern': r'(input|requirement|specification)',
                    'required_elements': ['input_requirements', 'specifications', 'validation_criteria'],
                    'severity': 'high'
                },
                {
                    'check_id': 'ISO_13485_7_3_3',
                    'check_name': 'Design Outputs',
                    'clause': '7.3.3',
                    'pattern': r'(output|result|deliverable)',
                    'required_elements': ['output_specifications', 'deliverables', 'acceptance_criteria'],
                    'severity': 'high'
                }
            ],
            'IEC_62304': [
                {
                    'check_id': 'IEC_62304_5_1_1',
                    'check_name': 'Software Life Cycle Processes',
                    'clause': '5.1.1',
                    'pattern': r'(software|lifecycle|process)',
                    'required_elements': ['software_process', 'lifecycle_management', 'process_validation'],
                    'severity': 'critical'
                },
                {
                    'check_id': 'IEC_62304_5_1_2',
                    'check_name': 'Software Safety Classification',
                    'clause': '5.1.2',
                    'pattern': r'(safety|classification|risk)',
                    'required_elements': ['safety_classification', 'risk_analysis', 'safety_validation'],
                    'severity': 'critical'
                }
            ],
            'GDPR': [
                {
                    'check_id': 'GDPR_25_1',
                    'check_name': 'Data Protection by Design',
                    'clause': 'Article 25',
                    'pattern': r'(privacy|data protection|personal data)',
                    'required_elements': ['privacy_by_design', 'data_protection', 'consent_management'],
                    'severity': 'high'
                },
                {
                    'check_id': 'GDPR_32_1',
                    'check_name': 'Security of Processing',
                    'clause': 'Article 32',
                    'pattern': r'(security|encryption|access control)',
                    'required_elements': ['data_security', 'encryption', 'access_control'],
                    'severity': 'high'
                }
            ]
        }
        
    def _initialize_compliance_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance requirements for different standards."""
        return {
            'FDA_21_CFR_820': {
                'name': 'FDA Quality System Regulation',
                'description': 'Medical device quality management requirements',
                'required_evidence': [
                    'Design and development documentation',
                    'Risk management file',
                    'Verification and validation records',
                    'Design review records',
                    'Corrective and preventive action records'
                ],
                'critical_areas': ['design_controls', 'risk_management', 'quality_system']
            },
            'FDA_21_CFR_11': {
                'name': 'FDA Electronic Records and Electronic Signatures',
                'description': 'Electronic records and signatures validation',
                'required_evidence': [
                    'System validation documentation',
                    'Electronic signature procedures',
                    'Audit trail records',
                    'Access control documentation'
                ],
                'critical_areas': ['electronic_validation', 'signature_verification', 'audit_trail']
            },
            'ISO_13485': {
                'name': 'ISO 13485 Medical Devices Quality Management',
                'description': 'Medical device quality management system requirements',
                'required_evidence': [
                    'Quality management system documentation',
                    'Risk management documentation',
                    'Design and development records',
                    'Management review records'
                ],
                'critical_areas': ['quality_management', 'risk_management', 'design_development']
            },
            'IEC_62304': {
                'name': 'IEC 62304 Medical Device Software',
                'description': 'Medical device software life cycle processes',
                'required_evidence': [
                    'Software development plan',
                    'Software requirements specification',
                    'Software architecture documentation',
                    'Software verification and validation records'
                ],
                'critical_areas': ['software_lifecycle', 'safety_classification', 'risk_management']
            },
            'GDPR': {
                'name': 'General Data Protection Regulation',
                'description': 'Data protection and privacy requirements',
                'required_evidence': [
                    'Data protection impact assessment',
                    'Privacy by design documentation',
                    'Data processing agreements',
                    'Consent management records'
                ],
                'critical_areas': ['data_protection', 'privacy_by_design', 'consent_management']
            }
        }
        
    def validate_test_case(self, test_case: Any, compliance_refs: List[str]) -> ComplianceValidationReport:
        """
        Validate a test case against compliance standards.
        
        Args:
            test_case: Test case to validate
            compliance_refs: List of compliance references
            
        Returns:
            Compliance validation report
        """
        checks = []
        evidence_gaps = []
        recommendations = []
        
        # Validate against each compliance reference
        for compliance_ref in compliance_refs:
            standard_checks = self._validate_against_standard(test_case, compliance_ref)
            checks.extend(standard_checks)
            
        # Identify evidence gaps
        evidence_gaps = self._identify_evidence_gaps(test_case, compliance_refs)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(checks, evidence_gaps)
        
        # Calculate overall compliance score
        compliance_score = self._calculate_compliance_score(checks)
        
        # Determine overall compliance level
        overall_compliance = self._determine_compliance_level(compliance_score, checks)
        
        return ComplianceValidationReport(
            test_case_id=getattr(test_case, 'id', 'unknown'),
            overall_compliance=overall_compliance,
            compliance_score=compliance_score,
            checks=checks,
            recommendations=recommendations,
            evidence_gaps=evidence_gaps,
            validation_timestamp=self._get_current_timestamp()
        )
        
    def _validate_against_standard(self, test_case: Any, compliance_ref: str) -> List[ComplianceCheck]:
        """Validate test case against a specific compliance standard."""
        checks = []
        
        # Get validation rules for the standard
        standard_rules = self.validation_rules.get(compliance_ref, [])
        
        for rule in standard_rules:
            check = self._perform_compliance_check(test_case, rule, compliance_ref)
            checks.append(check)
            
        return checks
        
    def _perform_compliance_check(self, test_case: Any, rule: Dict[str, Any], 
                                standard: str) -> ComplianceCheck:
        """Perform individual compliance check."""
        # Extract test case content for analysis
        test_content = self._extract_test_case_content(test_case)
        
        # Check if pattern matches
        pattern_matches = bool(re.search(rule['pattern'], test_content, re.IGNORECASE))
        
        # Check for required elements
        element_coverage = self._check_required_elements(test_content, rule['required_elements'])
        
        # Determine result
        if pattern_matches and element_coverage >= 0.8:  # 80% element coverage
            result = ValidationResult.PASS
            message = f"Test case meets {rule['check_name']} requirements"
        elif pattern_matches and element_coverage >= 0.5:  # 50% element coverage
            result = ValidationResult.WARNING
            message = f"Test case partially meets {rule['check_name']} requirements"
        else:
            result = ValidationResult.FAIL
            message = f"Test case does not meet {rule['check_name']} requirements"
            
        # Get evidence requirements
        evidence_required = self._get_evidence_requirements(standard, rule['check_id'])
        
        return ComplianceCheck(
            check_id=rule['check_id'],
            check_name=rule['check_name'],
            standard=standard,
            clause=rule['clause'],
            result=result,
            message=message,
            evidence_required=evidence_required,
            severity=rule['severity']
        )
        
    def _extract_test_case_content(self, test_case: Any) -> str:
        """Extract all text content from test case for analysis."""
        content_parts = []
        
        # Add basic test case information
        if hasattr(test_case, 'title'):
            content_parts.append(test_case.title)
        if hasattr(test_case, 'description'):
            content_parts.append(test_case.description)
        if hasattr(test_case, 'expected_outcome'):
            content_parts.append(test_case.expected_outcome)
            
        # Add test steps
        if hasattr(test_case, 'test_steps'):
            for step in test_case.test_steps:
                if hasattr(step, 'action'):
                    content_parts.append(step.action)
                if hasattr(step, 'expected_result'):
                    content_parts.append(step.expected_result)
                    
        # Add pass/fail criteria
        if hasattr(test_case, 'pass_criteria'):
            content_parts.extend(test_case.pass_criteria)
        if hasattr(test_case, 'fail_criteria'):
            content_parts.extend(test_case.fail_criteria)
            
        return ' '.join(content_parts)
        
    def _check_required_elements(self, content: str, required_elements: List[str]) -> float:
        """Check coverage of required elements in content."""
        if not required_elements:
            return 1.0
            
        found_elements = 0
        for element in required_elements:
            if re.search(element.replace('_', '\\s+'), content, re.IGNORECASE):
                found_elements += 1
                
        return found_elements / len(required_elements)
        
    def _get_evidence_requirements(self, standard: str, check_id: str) -> List[str]:
        """Get evidence requirements for a specific check."""
        standard_requirements = self.compliance_requirements.get(standard, {})
        return standard_requirements.get('required_evidence', [])
        
    def _identify_evidence_gaps(self, test_case: Any, compliance_refs: List[str]) -> List[str]:
        """Identify missing evidence for compliance validation."""
        gaps = []
        
        for compliance_ref in compliance_refs:
            standard_requirements = self.compliance_requirements.get(compliance_ref, {})
            required_evidence = standard_requirements.get('required_evidence', [])
            
            test_content = self._extract_test_case_content(test_case)
            
            for evidence in required_evidence:
                if not re.search(evidence.replace(' ', '\\s+'), test_content, re.IGNORECASE):
                    gaps.append(f"{compliance_ref}: {evidence}")
                    
        return gaps
        
    def _generate_recommendations(self, checks: List[ComplianceCheck], 
                                evidence_gaps: List[str]) -> List[str]:
        """Generate recommendations for improving compliance."""
        recommendations = []
        
        # Recommendations based on failed checks
        failed_checks = [check for check in checks if check.result == ValidationResult.FAIL]
        for check in failed_checks:
            recommendations.append(
                f"Improve {check.check_name}: {check.message}. "
                f"Required evidence: {', '.join(check.evidence_required)}"
            )
            
        # Recommendations based on warnings
        warning_checks = [check for check in checks if check.result == ValidationResult.WARNING]
        for check in warning_checks:
            recommendations.append(
                f"Enhance {check.check_name}: {check.message}. "
                f"Consider adding: {', '.join(check.evidence_required)}"
            )
            
        # Recommendations based on evidence gaps
        if evidence_gaps:
            recommendations.append(
                f"Address evidence gaps: {len(evidence_gaps)} missing evidence items identified. "
                f"Consider adding test steps to validate: {', '.join(evidence_gaps[:3])}"
            )
            
        return recommendations
        
    def _calculate_compliance_score(self, checks: List[ComplianceCheck]) -> float:
        """Calculate overall compliance score (0-100)."""
        if not checks:
            return 0.0
            
        total_weight = 0
        weighted_score = 0
        
        for check in checks:
            # Weight based on severity
            weight = {
                'critical': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }.get(check.severity, 1)
            
            # Score based on result
            score = {
                ValidationResult.PASS: 100,
                ValidationResult.WARNING: 70,
                ValidationResult.FAIL: 0,
                ValidationResult.INFO: 50
            }.get(check.result, 0)
            
            total_weight += weight
            weighted_score += score * weight
            
        return weighted_score / total_weight if total_weight > 0 else 0.0
        
    def _determine_compliance_level(self, score: float, checks: List[ComplianceCheck]) -> ComplianceLevel:
        """Determine overall compliance level based on score and checks."""
        if not checks:
            return ComplianceLevel.NOT_APPLICABLE
            
        # Check for critical failures
        critical_failures = [
            check for check in checks 
            if check.result == ValidationResult.FAIL and check.severity == 'critical'
        ]
        
        if critical_failures:
            return ComplianceLevel.NON_COMPLIANT
        elif score >= 90:
            return ComplianceLevel.FULLY_COMPLIANT
        elif score >= 70:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return ComplianceLevel.NON_COMPLIANT
            
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for validation report."""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def generate_compliance_summary(self, validation_reports: List[ComplianceValidationReport]) -> Dict[str, Any]:
        """
        Generate summary of compliance validation across multiple test cases.
        
        Args:
            validation_reports: List of validation reports
            
        Returns:
            Compliance summary dictionary
        """
        if not validation_reports:
            return {'error': 'No validation reports provided'}
            
        # Calculate overall statistics
        total_test_cases = len(validation_reports)
        fully_compliant = len([r for r in validation_reports if r.overall_compliance == ComplianceLevel.FULLY_COMPLIANT])
        partially_compliant = len([r for r in validation_reports if r.overall_compliance == ComplianceLevel.PARTIALLY_COMPLIANT])
        non_compliant = len([r for r in validation_reports if r.overall_compliance == ComplianceLevel.NON_COMPLIANT])
        
        # Calculate average compliance score
        avg_score = sum(r.compliance_score for r in validation_reports) / total_test_cases
        
        # Identify common issues
        all_checks = []
        for report in validation_reports:
            all_checks.extend(report.checks)
            
        failed_checks = [check for check in all_checks if check.result == ValidationResult.FAIL]
        warning_checks = [check for check in all_checks if check.result == ValidationResult.WARNING]
        
        # Group issues by standard
        issues_by_standard = {}
        for check in failed_checks + warning_checks:
            if check.standard not in issues_by_standard:
                issues_by_standard[check.standard] = []
            issues_by_standard[check.standard].append(check)
            
        return {
            'summary': {
                'total_test_cases': total_test_cases,
                'fully_compliant': fully_compliant,
                'partially_compliant': partially_compliant,
                'non_compliant': non_compliant,
                'average_compliance_score': round(avg_score, 2),
                'compliance_rate': round((fully_compliant / total_test_cases) * 100, 2)
            },
            'issues_by_standard': {
                standard: {
                    'total_issues': len(issues),
                    'critical_issues': len([c for c in issues if c.severity == 'critical']),
                    'high_issues': len([c for c in issues if c.severity == 'high']),
                    'issues': [{'check_name': c.check_name, 'message': c.message} for c in issues]
                }
                for standard, issues in issues_by_standard.items()
            },
            'recommendations': self._generate_overall_recommendations(validation_reports)
        }
        
    def _generate_overall_recommendations(self, validation_reports: List[ComplianceValidationReport]) -> List[str]:
        """Generate overall recommendations based on validation reports."""
        recommendations = []
        
        # Collect all recommendations
        all_recommendations = []
        for report in validation_reports:
            all_recommendations.extend(report.recommendations)
            
        # Count recommendation frequency
        rec_count = {}
        for rec in all_recommendations:
            rec_count[rec] = rec_count.get(rec, 0) + 1
            
        # Sort by frequency and return top recommendations
        sorted_recs = sorted(rec_count.items(), key=lambda x: x[1], reverse=True)
        
        for rec, count in sorted_recs[:10]:  # Top 10 recommendations
            recommendations.append(f"{rec} (applies to {count} test cases)")
            
        return recommendations
