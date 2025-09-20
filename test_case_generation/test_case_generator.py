"""
Test Case Generator for Healthcare Software

Generates detailed, compliant test cases from healthcare requirements using
AI and ensures traceability to regulatory standards.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import json
import re
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime

try:
    import google.generativeai as genai
    from google.cloud import aiplatform
except ImportError:
    genai = None
    aiplatform = None

logger = logging.getLogger(__name__)


class TestCaseType(Enum):
    """Types of test cases."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    COMPLIANCE = "compliance"


class TestCasePriority(Enum):
    """Test case priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestStep:
    """Individual test step."""
    step_number: int
    action: str
    expected_result: str
    data_inputs: Optional[Dict[str, Any]] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None


@dataclass
class TestCase:
    """Complete test case structure."""
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
    estimated_duration: Optional[int] = None  # in minutes
    created_date: str = ""
    last_modified: str = ""
    
    def __post_init__(self):
        if self.pass_criteria is None:
            self.pass_criteria = []
        if self.fail_criteria is None:
            self.fail_criteria = []
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.last_modified:
            self.last_modified = datetime.now().isoformat()


class TestCaseGenerator:
    """AI-powered test case generator for healthcare software."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize the test case generator.
        
        Args:
            api_key: Google AI API key
            project_id: Google Cloud project ID
        """
        self.api_key = api_key
        self.project_id = project_id
        
        if genai and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            logger.warning("Google Generative AI not available. Using rule-based generation.")
            self.model = None
            
    def generate_test_cases(self, requirements: List[Dict[str, Any]], 
                          compliance_mappings: List[Dict[str, Any]] = None) -> List[TestCase]:
        """
        Generate test cases from requirements.
        
        Args:
            requirements: List of parsed requirements
            compliance_mappings: Optional compliance mappings
            
        Returns:
            List of generated test cases
        """
        test_cases = []
        
        for req in requirements:
            if self.model:
                req_test_cases = self._generate_with_ai(req, compliance_mappings)
            else:
                req_test_cases = self._generate_with_rules(req, compliance_mappings)
                
            test_cases.extend(req_test_cases)
            
        return test_cases
        
    def _generate_with_ai(self, requirement: Dict[str, Any], 
                         compliance_mappings: List[Dict[str, Any]] = None) -> List[TestCase]:
        """Generate test cases using AI."""
        prompt = self._create_generation_prompt(requirement, compliance_mappings)
        
        try:
            response = self.model.generate_content(prompt)
            test_cases_data = json.loads(response.text)
            
            test_cases = []
            for tc_data in test_cases_data.get('test_cases', []):
                test_case = self._create_test_case_from_data(tc_data, requirement)
                test_cases.append(test_case)
                
            return test_cases
            
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            return self._generate_with_rules(requirement, compliance_mappings)
            
    def _create_generation_prompt(self, requirement: Dict[str, Any], 
                                compliance_mappings: List[Dict[str, Any]] = None) -> str:
        """Create prompt for AI-based test case generation."""
        compliance_info = ""
        if compliance_mappings:
            compliance_info = f"\\nCompliance References: {json.dumps(compliance_mappings, indent=2)}"
            
        return f"""
        Generate detailed test cases for the following healthcare software requirement.
        Ensure test cases include references to regulatory standards (FDA, ISO, IEC) for compliance.
        
        Requirement:
        - ID: {requirement.get('id', 'N/A')}
        - Description: {requirement.get('description', '')}
        - Type: {requirement.get('type', 'N/A')}
        - Priority: {requirement.get('priority', 'N/A')}
        - Compliance References: {requirement.get('compliance_refs', [])}
        {compliance_info}
        
        Generate test cases including:
        1. Case ID, title, description
        2. Step-by-step actions with expected results
        3. Priority based on requirement priority
        4. References to regulatory standards (FDA, ISO, IEC)
        5. Test data requirements
        6. Prerequisites and pass/fail criteria
        7. Estimated duration
        
        Focus on healthcare-specific testing including:
        - Patient safety validation
        - Data privacy and security testing
        - Regulatory compliance verification
        - Medical device functionality testing
        - Clinical workflow validation
        - Audit trail verification
        - Risk management validation
        
        Generate both positive and negative test scenarios.
        Include boundary value testing where applicable.
        
        Return the result as a JSON object with a 'test_cases' array.
        Each test case should have:
        - id: Unique test case ID (TC-XXX format)
        - title: Descriptive title
        - description: Detailed description
        - test_case_type: positive/negative/boundary/integration/performance/security/usability/compliance
        - priority: critical/high/medium/low
        - requirement_id: Reference to source requirement
        - compliance_refs: List of compliance references
        - test_steps: Array of test steps with step_number, action, expected_result
        - prerequisites: List of prerequisites
        - test_data: Object with test data requirements
        - expected_outcome: Overall expected outcome
        - pass_criteria: List of pass criteria
        - fail_criteria: List of fail criteria
        - estimated_duration: Duration in minutes
        """
        
    def _create_test_case_from_data(self, tc_data: Dict[str, Any], 
                                  requirement: Dict[str, Any]) -> TestCase:
        """Create TestCase object from AI-generated data."""
        # Create test steps
        test_steps = []
        for step_data in tc_data.get('test_steps', []):
            step = TestStep(
                step_number=step_data.get('step_number', 1),
                action=step_data.get('action', ''),
                expected_result=step_data.get('expected_result', ''),
                data_inputs=step_data.get('data_inputs'),
                preconditions=step_data.get('preconditions'),
                postconditions=step_data.get('postconditions')
            )
            test_steps.append(step)
            
        # Create test case
        test_case = TestCase(
            id=tc_data.get('id', f"TC-{uuid.uuid4().hex[:8].upper()}"),
            title=tc_data.get('title', ''),
            description=tc_data.get('description', ''),
            test_case_type=TestCaseType(tc_data.get('test_case_type', 'positive')),
            priority=TestCasePriority(tc_data.get('priority', 'medium')),
            requirement_id=requirement.get('id', ''),
            compliance_refs=tc_data.get('compliance_refs', []),
            test_steps=test_steps,
            prerequisites=tc_data.get('prerequisites', []),
            test_data=tc_data.get('test_data'),
            expected_outcome=tc_data.get('expected_outcome', ''),
            pass_criteria=tc_data.get('pass_criteria', []),
            fail_criteria=tc_data.get('fail_criteria', []),
            estimated_duration=tc_data.get('estimated_duration')
        )
        
        return test_case
        
    def _generate_with_rules(self, requirement: Dict[str, Any], 
                           compliance_mappings: List[Dict[str, Any]] = None) -> List[TestCase]:
        """Generate test cases using rule-based approach."""
        test_cases = []
        
        # Generate positive test case
        positive_tc = self._generate_positive_test_case(requirement, compliance_mappings)
        if positive_tc:
            test_cases.append(positive_tc)
            
        # Generate negative test case
        negative_tc = self._generate_negative_test_case(requirement, compliance_mappings)
        if negative_tc:
            test_cases.append(negative_tc)
            
        # Generate boundary test case if applicable
        boundary_tc = self._generate_boundary_test_case(requirement, compliance_mappings)
        if boundary_tc:
            test_cases.append(boundary_tc)
            
        return test_cases
        
    def _generate_positive_test_case(self, requirement: Dict[str, Any], 
                                   compliance_mappings: List[Dict[str, Any]] = None) -> TestCase:
        """Generate positive test case."""
        req_id = requirement.get('id', 'REQ-001')
        req_desc = requirement.get('description', '')
        
        # Extract key actions from requirement
        actions = self._extract_actions_from_requirement(req_desc)
        
        # Create test steps
        test_steps = []
        for i, action in enumerate(actions, 1):
            step = TestStep(
                step_number=i,
                action=action,
                expected_result=f"System {action.lower()} successfully",
                data_inputs=self._generate_test_data_for_action(action)
            )
            test_steps.append(step)
            
        # Create test case
        test_case = TestCase(
            id=f"TC-{req_id}-POS-001",
            title=f"Positive Test: {req_desc[:50]}...",
            description=f"Verify that the system correctly implements: {req_desc}",
            test_case_type=TestCaseType.POSITIVE,
            priority=self._map_requirement_priority_to_test_priority(requirement.get('priority', 'medium')),
            requirement_id=req_id,
            compliance_refs=requirement.get('compliance_refs', []),
            test_steps=test_steps,
            prerequisites=self._generate_prerequisites(requirement),
            expected_outcome="All test steps pass successfully",
            pass_criteria=["System responds as expected", "No errors or exceptions occur"],
            fail_criteria=["System fails to respond", "Errors or exceptions occur"],
            estimated_duration=self._estimate_duration(len(test_steps))
        )
        
        return test_case
        
    def _generate_negative_test_case(self, requirement: Dict[str, Any], 
                                   compliance_mappings: List[Dict[str, Any]] = None) -> TestCase:
        """Generate negative test case."""
        req_id = requirement.get('id', 'REQ-001')
        req_desc = requirement.get('description', '')
        
        # Generate negative scenarios
        negative_scenarios = self._generate_negative_scenarios(req_desc)
        
        # Create test steps
        test_steps = []
        for i, scenario in enumerate(negative_scenarios, 1):
            step = TestStep(
                step_number=i,
                action=scenario['action'],
                expected_result=scenario['expected_result'],
                data_inputs=scenario.get('data_inputs')
            )
            test_steps.append(step)
            
        # Create test case
        test_case = TestCase(
            id=f"TC-{req_id}-NEG-001",
            title=f"Negative Test: {req_desc[:50]}...",
            description=f"Verify that the system handles invalid inputs gracefully: {req_desc}",
            test_case_type=TestCaseType.NEGATIVE,
            priority=self._map_requirement_priority_to_test_priority(requirement.get('priority', 'medium')),
            requirement_id=req_id,
            compliance_refs=requirement.get('compliance_refs', []),
            test_steps=test_steps,
            prerequisites=self._generate_prerequisites(requirement),
            expected_outcome="System handles invalid inputs gracefully with appropriate error messages",
            pass_criteria=["System displays appropriate error messages", "System remains stable"],
            fail_criteria=["System crashes or behaves unexpectedly", "No error handling"],
            estimated_duration=self._estimate_duration(len(test_steps))
        )
        
        return test_case
        
    def _generate_boundary_test_case(self, requirement: Dict[str, Any], 
                                   compliance_mappings: List[Dict[str, Any]] = None) -> Optional[TestCase]:
        """Generate boundary test case if applicable."""
        req_desc = requirement.get('description', '').lower()
        
        # Check if requirement involves numeric values or limits
        if not any(word in req_desc for word in ['limit', 'maximum', 'minimum', 'range', 'threshold', 'value']):
            return None
            
        req_id = requirement.get('id', 'REQ-001')
        
        # Generate boundary test scenarios
        boundary_scenarios = self._generate_boundary_scenarios(req_desc)
        
        if not boundary_scenarios:
            return None
            
        # Create test steps
        test_steps = []
        for i, scenario in enumerate(boundary_scenarios, 1):
            step = TestStep(
                step_number=i,
                action=scenario['action'],
                expected_result=scenario['expected_result'],
                data_inputs=scenario.get('data_inputs')
            )
            test_steps.append(step)
            
        # Create test case
        test_case = TestCase(
            id=f"TC-{req_id}-BND-001",
            title=f"Boundary Test: {req_desc[:50]}...",
            description=f"Verify system behavior at boundary values: {req_desc}",
            test_case_type=TestCaseType.BOUNDARY,
            priority=self._map_requirement_priority_to_test_priority(requirement.get('priority', 'medium')),
            requirement_id=req_id,
            compliance_refs=requirement.get('compliance_refs', []),
            test_steps=test_steps,
            prerequisites=self._generate_prerequisites(requirement),
            expected_outcome="System behaves correctly at all boundary values",
            pass_criteria=["System handles boundary values correctly", "No unexpected behavior"],
            fail_criteria=["System fails at boundary values", "Unexpected behavior occurs"],
            estimated_duration=self._estimate_duration(len(test_steps))
        )
        
        return test_case
        
    def _extract_actions_from_requirement(self, requirement_text: str) -> List[str]:
        """Extract key actions from requirement text."""
        actions = []
        
        # Look for action verbs
        action_patterns = [
            r'(?:shall|must|will|should)\\s+([^\\n]+)',
            r'(?:enable|allow|provide|support|display|show|generate|create|validate|verify)\\s+([^\\n]+)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, requirement_text, re.IGNORECASE)
            actions.extend(matches)
            
        # If no specific actions found, create generic ones
        if not actions:
            actions = [
                "Access the system",
                "Perform the required operation",
                "Verify the result"
            ]
            
        return actions[:5]  # Limit to 5 actions
        
    def _generate_test_data_for_action(self, action: str) -> Dict[str, Any]:
        """Generate test data requirements for an action."""
        action_lower = action.lower()
        
        if 'login' in action_lower or 'authenticate' in action_lower:
            return {
                'username': 'test_user',
                'password': 'test_password',
                'role': 'healthcare_provider'
            }
        elif 'patient' in action_lower:
            return {
                'patient_id': 'PAT001',
                'patient_name': 'Test Patient',
                'date_of_birth': '1990-01-01'
            }
        elif 'data' in action_lower or 'record' in action_lower:
            return {
                'data_type': 'medical_record',
                'data_format': 'HL7_FHIR',
                'validation_rules': 'enabled'
            }
        else:
            return {
                'input_data': 'test_input',
                'expected_format': 'valid'
            }
            
    def _generate_prerequisites(self, requirement: Dict[str, Any]) -> List[str]:
        """Generate prerequisites for test case."""
        prerequisites = [
            "System is installed and configured",
            "Test environment is available",
            "Test data is prepared"
        ]
        
        # Add healthcare-specific prerequisites
        req_type = requirement.get('type', '').lower()
        if 'security' in req_type or 'privacy' in req_type:
            prerequisites.append("Security credentials are configured")
            prerequisites.append("Privacy settings are enabled")
            
        if 'compliance' in req_type:
            prerequisites.append("Compliance settings are configured")
            prerequisites.append("Audit logging is enabled")
            
        return prerequisites
        
    def _generate_negative_scenarios(self, requirement_text: str) -> List[Dict[str, Any]]:
        """Generate negative test scenarios."""
        scenarios = []
        
        # Common negative scenarios
        base_scenarios = [
            {
                'action': 'Enter invalid input data',
                'expected_result': 'System displays appropriate error message',
                'data_inputs': {'input_data': 'invalid_data'}
            },
            {
                'action': 'Submit empty form',
                'expected_result': 'System displays validation error',
                'data_inputs': {'input_data': ''}
            },
            {
                'action': 'Access without proper permissions',
                'expected_result': 'System denies access with appropriate message',
                'data_inputs': {'permissions': 'none'}
            }
        ]
        
        # Add healthcare-specific negative scenarios
        if 'patient' in requirement_text.lower():
            scenarios.append({
                'action': 'Enter invalid patient ID',
                'expected_result': 'System displays patient not found error',
                'data_inputs': {'patient_id': 'INVALID_ID'}
            })
            
        if 'data' in requirement_text.lower():
            scenarios.append({
                'action': 'Submit corrupted data',
                'expected_result': 'System handles data corruption gracefully',
                'data_inputs': {'data_format': 'corrupted'}
            })
            
        return base_scenarios + scenarios[:3]  # Limit to 6 total scenarios
        
    def _generate_boundary_scenarios(self, requirement_text: str) -> List[Dict[str, Any]]:
        """Generate boundary test scenarios."""
        scenarios = []
        
        # Look for numeric values in requirement
        numeric_patterns = [
            r'(\\d+)\\s*(?:seconds?|minutes?|hours?|days?)',
            r'(\\d+)\\s*(?:bytes?|kb|mb|gb)',
            r'(\\d+)\\s*(?:characters?|fields?|records?)',
        ]
        
        for pattern in numeric_patterns:
            matches = re.findall(pattern, requirement_text, re.IGNORECASE)
            for match in matches:
                value = int(match)
                scenarios.extend([
                    {
                        'action': f'Test with value {value - 1} (just below limit)',
                        'expected_result': 'System accepts the value',
                        'data_inputs': {'test_value': value - 1}
                    },
                    {
                        'action': f'Test with value {value} (at limit)',
                        'expected_result': 'System accepts the value',
                        'data_inputs': {'test_value': value}
                    },
                    {
                        'action': f'Test with value {value + 1} (just above limit)',
                        'expected_result': 'System rejects the value with appropriate error',
                        'data_inputs': {'test_value': value + 1}
                    }
                ])
                
        return scenarios[:6]  # Limit to 6 scenarios
        
    def _map_requirement_priority_to_test_priority(self, req_priority: str) -> TestCasePriority:
        """Map requirement priority to test case priority."""
        priority_mapping = {
            'critical': TestCasePriority.CRITICAL,
            'high': TestCasePriority.HIGH,
            'medium': TestCasePriority.MEDIUM,
            'low': TestCasePriority.LOW
        }
        
        return priority_mapping.get(req_priority.lower(), TestCasePriority.MEDIUM)
        
    def _estimate_duration(self, num_steps: int) -> int:
        """Estimate test case duration based on number of steps."""
        # Base duration of 5 minutes plus 2 minutes per step
        return 5 + (num_steps * 2)
        
    def refine_test_case(self, test_case: TestCase, refinement_prompt: str) -> TestCase:
        """
        Refine test case based on natural language prompt.
        
        Args:
            test_case: Test case to refine
            refinement_prompt: Natural language refinement instruction
            
        Returns:
            Refined test case
        """
        if self.model:
            return self._refine_with_ai(test_case, refinement_prompt)
        else:
            return self._refine_with_rules(test_case, refinement_prompt)
            
    def _refine_with_ai(self, test_case: TestCase, refinement_prompt: str) -> TestCase:
        """Refine test case using AI."""
        prompt = f"""
        Refine the following test case based on the refinement instruction:
        
        Original Test Case:
        {json.dumps(asdict(test_case), indent=2)}
        
        Refinement Instruction:
        {refinement_prompt}
        
        Return the refined test case as a JSON object with the same structure.
        """
        
        try:
            response = self.model.generate_content(prompt)
            refined_data = json.loads(response.text)
            
            # Update test case with refined data
            for key, value in refined_data.items():
                if hasattr(test_case, key):
                    setattr(test_case, key, value)
                    
            # Update last modified timestamp
            test_case.last_modified = datetime.now().isoformat()
            
            return test_case
            
        except Exception as e:
            logger.error(f"AI refinement failed: {str(e)}")
            return self._refine_with_rules(test_case, refinement_prompt)
            
    def _refine_with_rules(self, test_case: TestCase, refinement_prompt: str) -> TestCase:
        """Refine test case using rule-based approach."""
        prompt_lower = refinement_prompt.lower()
        
        # Update priority
        if 'high priority' in prompt_lower or 'increase priority' in prompt_lower:
            if test_case.priority == TestCasePriority.LOW:
                test_case.priority = TestCasePriority.MEDIUM
            elif test_case.priority == TestCasePriority.MEDIUM:
                test_case.priority = TestCasePriority.HIGH
                
        # Add negative test scenarios
        if 'add negative' in prompt_lower or 'negative test' in prompt_lower:
            negative_steps = self._generate_negative_scenarios(test_case.description)
            for step_data in negative_steps:
                step = TestStep(
                    step_number=len(test_case.test_steps) + 1,
                    action=step_data['action'],
                    expected_result=step_data['expected_result'],
                    data_inputs=step_data.get('data_inputs')
                )
                test_case.test_steps.append(step)
                
        # Update last modified timestamp
        test_case.last_modified = datetime.now().isoformat()
        
        return test_case

