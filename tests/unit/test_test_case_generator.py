"""
Unit tests for Test Case Generator module
"""

import pytest
from test_case_generation.test_case_generator import TestCaseGenerator, TestCase, TestStep, TestCaseType, TestCasePriority


class TestTestCaseGenerator:
    """Test cases for TestCaseGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TestCaseGenerator()
        
    def test_generator_initialization(self):
        """Test generator initialization."""
        assert self.generator is not None
        assert hasattr(self.generator, 'model')
        
    def test_extract_actions_from_requirement(self):
        """Test action extraction from requirement text."""
        requirement_text = "The system shall store patient data and validate input"
        
        actions = self.generator._extract_actions_from_requirement(requirement_text)
        
        assert len(actions) > 0
        assert any('store' in action.lower() for action in actions)
        assert any('validate' in action.lower() for action in actions)
        
    def test_generate_test_data_for_action(self):
        """Test test data generation for actions."""
        # Test login action
        login_data = self.generator._generate_test_data_for_action("Login to the system")
        assert 'username' in login_data
        assert 'password' in login_data
        
        # Test patient action
        patient_data = self.generator._generate_test_data_for_action("Access patient data")
        assert 'patient_id' in patient_data
        assert 'patient_name' in patient_data
        
        # Test generic action
        generic_data = self.generator._generate_test_data_for_action("Process data")
        assert 'input_data' in generic_data
        
    def test_generate_prerequisites(self):
        """Test prerequisite generation."""
        requirement = {
            'type': 'security',
            'description': 'Secure data access'
        }
        
        prerequisites = self.generator._generate_prerequisites(requirement)
        
        assert len(prerequisites) >= 3
        assert any('System is installed' in prereq for prereq in prerequisites)
        assert any('Security credentials' in prereq for prereq in prerequisites)
        
    def test_generate_negative_scenarios(self):
        """Test negative scenario generation."""
        requirement_text = "The system shall store patient data securely"
        
        scenarios = self.generator._generate_negative_scenarios(requirement_text)
        
        assert len(scenarios) > 0
        assert all('action' in scenario for scenario in scenarios)
        assert all('expected_result' in scenario for scenario in scenarios)
        assert all('data_inputs' in scenario for scenario in scenarios)
        
    def test_generate_boundary_scenarios(self):
        """Test boundary scenario generation."""
        requirement_text = "The system shall handle up to 1000 concurrent users"
        
        scenarios = self.generator._generate_boundary_scenarios(requirement_text)
        
        assert len(scenarios) > 0
        assert all('action' in scenario for scenario in scenarios)
        assert all('expected_result' in scenario for scenario in scenarios)
        assert all('data_inputs' in scenario for scenario in scenarios)
        
    def test_map_requirement_priority_to_test_priority(self):
        """Test priority mapping from requirement to test case."""
        assert self.generator._map_requirement_priority_to_test_priority('critical') == TestCasePriority.CRITICAL
        assert self.generator._map_requirement_priority_to_test_priority('high') == TestCasePriority.HIGH
        assert self.generator._map_requirement_priority_to_test_priority('medium') == TestCasePriority.MEDIUM
        assert self.generator._map_requirement_priority_to_test_priority('low') == TestCasePriority.LOW
        assert self.generator._map_requirement_priority_to_test_priority('unknown') == TestCasePriority.MEDIUM
        
    def test_estimate_duration(self):
        """Test duration estimation."""
        assert self.generator._estimate_duration(1) == 7  # 5 + 1*2
        assert self.generator._estimate_duration(5) == 15  # 5 + 5*2
        assert self.generator._estimate_duration(10) == 25  # 5 + 10*2
        
    def test_generate_positive_test_case(self):
        """Test positive test case generation."""
        requirement = {
            'id': 'REQ-001',
            'description': 'The system shall store patient data securely',
            'priority': 'high',
            'compliance_refs': ['HIPAA']
        }
        
        test_case = self.generator._generate_positive_test_case(requirement)
        
        assert test_case is not None
        assert test_case.id.startswith('TC-REQ-001-POS')
        assert test_case.test_case_type == TestCaseType.POSITIVE
        assert test_case.priority == TestCasePriority.HIGH
        assert test_case.requirement_id == 'REQ-001'
        assert len(test_case.test_steps) > 0
        assert test_case.expected_outcome != ""
        
    def test_generate_negative_test_case(self):
        """Test negative test case generation."""
        requirement = {
            'id': 'REQ-002',
            'description': 'The system shall validate user input',
            'priority': 'medium',
            'compliance_refs': ['FDA']
        }
        
        test_case = self.generator._generate_negative_test_case(requirement)
        
        assert test_case is not None
        assert test_case.id.startswith('TC-REQ-002-NEG')
        assert test_case.test_case_type == TestCaseType.NEGATIVE
        assert test_case.priority == TestCasePriority.MEDIUM
        assert test_case.requirement_id == 'REQ-002'
        assert len(test_case.test_steps) > 0
        assert 'invalid' in test_case.expected_outcome.lower()
        
    def test_generate_boundary_test_case(self):
        """Test boundary test case generation."""
        requirement = {
            'id': 'REQ-003',
            'description': 'The system shall handle up to 1000 users',
            'priority': 'high',
            'compliance_refs': ['ISO']
        }
        
        test_case = self.generator._generate_boundary_test_case(requirement)
        
        if test_case:  # May be None if no numeric values found
            assert test_case.id.startswith('TC-REQ-003-BND')
            assert test_case.test_case_type == TestCaseType.BOUNDARY
            assert test_case.priority == TestCasePriority.HIGH
            assert test_case.requirement_id == 'REQ-003'
            assert len(test_case.test_steps) > 0
            
    def test_generate_test_cases_with_rules(self):
        """Test test case generation using rule-based approach."""
        requirements = [
            {
                'id': 'REQ-001',
                'description': 'The system shall store patient data',
                'type': 'functional',
                'priority': 'high',
                'compliance_refs': ['HIPAA']
            }
        ]
        
        test_cases = self.generator._generate_with_rules(requirements[0])
        
        assert len(test_cases) >= 2  # At least positive and negative
        assert any(tc.test_case_type == TestCaseType.POSITIVE for tc in test_cases)
        assert any(tc.test_case_type == TestCaseType.NEGATIVE for tc in test_cases)
        
    def test_refine_test_case_with_rules(self):
        """Test test case refinement using rule-based approach."""
        test_case = TestCase(
            id="TC-001",
            title="Test Case",
            description="Test description",
            test_case_type=TestCaseType.POSITIVE,
            priority=TestCasePriority.MEDIUM,
            requirement_id="REQ-001",
            compliance_refs=[],
            test_steps=[],
            prerequisites=[],
            expected_outcome="Test outcome"
        )
        
        refinement_prompt = "Increase priority to high"
        
        refined_tc = self.generator._refine_with_rules(test_case, refinement_prompt)
        
        assert refined_tc.priority == TestCasePriority.HIGH
        assert refined_tc.last_modified != test_case.last_modified
        
    def test_create_test_case_from_data(self):
        """Test test case creation from AI-generated data."""
        tc_data = {
            'id': 'TC-001',
            'title': 'Test Case Title',
            'description': 'Test case description',
            'test_case_type': 'positive',
            'priority': 'high',
            'requirement_id': 'REQ-001',
            'compliance_refs': ['HIPAA'],
            'test_steps': [
                {
                    'step_number': 1,
                    'action': 'Login to system',
                    'expected_result': 'User is logged in',
                    'data_inputs': {'username': 'test_user'}
                }
            ],
            'prerequisites': ['System is available'],
            'test_data': {'input': 'test_data'},
            'expected_outcome': 'Test passes',
            'pass_criteria': ['All steps pass'],
            'fail_criteria': ['Any step fails'],
            'estimated_duration': 10
        }
        
        requirement = {'id': 'REQ-001'}
        
        test_case = self.generator._create_test_case_from_data(tc_data, requirement)
        
        assert test_case.id == 'TC-001'
        assert test_case.title == 'Test Case Title'
        assert test_case.test_case_type == TestCaseType.POSITIVE
        assert test_case.priority == TestCasePriority.HIGH
        assert len(test_case.test_steps) == 1
        assert test_case.test_steps[0].step_number == 1
        assert test_case.test_steps[0].action == 'Login to system'
