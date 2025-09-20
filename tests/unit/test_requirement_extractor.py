"""
Unit tests for Requirement Extractor module
"""

import pytest
from input_parsing.requirement_extractor import RequirementExtractor, Requirement, RequirementType, Priority


class TestRequirementExtractor:
    """Test cases for RequirementExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = RequirementExtractor()
        
    def test_extractor_initialization(self):
        """Test extractor initialization."""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'model')
        
    def test_extract_clean_text(self):
        """Test clean text extraction from parsed document."""
        parsed_doc = {
            'content': [
                {'type': 'text', 'text': 'Requirement 1: The system shall store patient data.'},
                {'type': 'paragraph', 'text': 'Requirement 2: The system shall be secure.'},
                {'type': 'html_element', 'text': 'Requirement 3: The system shall be fast.'}
            ]
        }
        
        clean_text = self.extractor._extract_clean_text(parsed_doc)
        
        assert 'Requirement 1' in clean_text
        assert 'Requirement 2' in clean_text
        assert 'Requirement 3' in clean_text
        
    def test_split_into_sections(self):
        """Test text splitting into sections."""
        text = """
        1. Patient Data Management
        The system shall store patient data securely.
        
        2. Security Requirements
        The system shall implement encryption.
        
        3. Performance Requirements
        The system shall respond within 2 seconds.
        """
        
        sections = self.extractor._split_into_sections(text)
        
        assert len(sections) >= 3
        assert any('Patient Data Management' in section[0] for section in sections)
        assert any('Security Requirements' in section[0] for section in sections)
        assert any('Performance Requirements' in section[0] for section in sections)
        
    def test_classify_requirement_type(self):
        """Test requirement type classification."""
        # Test performance requirement
        perf_req = "The system shall respond within 2 seconds"
        assert self.extractor._classify_requirement_type(perf_req) == RequirementType.PERFORMANCE
        
        # Test security requirement
        sec_req = "The system shall encrypt all data"
        assert self.extractor._classify_requirement_type(sec_req) == RequirementType.SECURITY
        
        # Test compliance requirement
        comp_req = "The system shall comply with FDA regulations"
        assert self.extractor._classify_requirement_type(comp_req) == RequirementType.COMPLIANCE
        
        # Test functional requirement
        func_req = "The system shall store patient data"
        assert self.extractor._classify_requirement_type(func_req) == RequirementType.FUNCTIONAL
        
    def test_determine_priority(self):
        """Test priority determination."""
        # Test critical priority
        critical_req = "The system shall be critical for patient safety"
        critical_section = "Safety Requirements"
        assert self.extractor._determine_priority(critical_req, critical_section) == Priority.HIGH
        
        # Test high priority
        high_req = "The system shall be important for security"
        assert self.extractor._determine_priority(high_req, "General") == Priority.HIGH
        
        # Test low priority
        low_req = "The system shall be optional for users"
        assert self.extractor._determine_priority(low_req, "General") == Priority.LOW
        
        # Test medium priority (default)
        medium_req = "The system shall store data"
        assert self.extractor._determine_priority(medium_req, "General") == Priority.MEDIUM
        
    def test_extract_compliance_refs(self):
        """Test compliance reference extraction."""
        text = "The system shall comply with FDA 21 CFR 820 and ISO 13485 standards"
        
        refs = self.extractor._extract_compliance_refs(text)
        
        assert 'FDA 21 CFR 820' in refs
        assert 'ISO 13485' in refs
        
    def test_extract_acceptance_criteria(self):
        """Test acceptance criteria extraction."""
        text = "The system shall respond when user clicks submit and within 2 seconds"
        
        criteria = self.extractor._extract_acceptance_criteria(text)
        
        assert len(criteria) > 0
        assert any('when' in criterion.lower() for criterion in criteria)
        
    def test_generate_negative_scenarios(self):
        """Test negative scenario generation."""
        requirement_text = "The system shall store patient data securely"
        
        scenarios = self.extractor._generate_negative_scenarios(requirement_text)
        
        assert len(scenarios) > 0
        assert all('action' in scenario for scenario in scenarios)
        assert all('expected_result' in scenario for scenario in scenarios)
        
    def test_generate_boundary_scenarios(self):
        """Test boundary scenario generation."""
        requirement_text = "The system shall handle up to 1000 concurrent users"
        
        scenarios = self.extractor._generate_boundary_scenarios(requirement_text)
        
        assert len(scenarios) > 0
        assert all('action' in scenario for scenario in scenarios)
        assert all('expected_result' in scenario for scenario in scenarios)
        
    def test_summarize_requirements(self):
        """Test requirement summarization."""
        requirements = [
            Requirement(
                id="REQ-001",
                description="Store patient data",
                type=RequirementType.FUNCTIONAL,
                priority=Priority.HIGH,
                source_section="Data Management",
                compliance_refs=["HIPAA"],
                context="Patient data storage",
                acceptance_criteria=["Data is stored securely"],
                dependencies=[],
                raw_text="The system shall store patient data"
            ),
            Requirement(
                id="REQ-002",
                description="Encrypt data",
                type=RequirementType.SECURITY,
                priority=Priority.CRITICAL,
                source_section="Security",
                compliance_refs=["HIPAA", "GDPR"],
                context="Data protection",
                acceptance_criteria=["Data is encrypted"],
                dependencies=["REQ-001"],
                raw_text="The system shall encrypt all data"
            )
        ]
        
        summary = self.extractor.summarize_requirements(requirements)
        
        assert summary['total_requirements'] == 2
        assert summary['by_type']['functional'] == 1
        assert summary['by_type']['security'] == 1
        assert summary['by_priority']['high'] == 1
        assert summary['by_priority']['critical'] == 1
        assert 'HIPAA' in summary['compliance_refs']
        assert 'GDPR' in summary['compliance_refs']

