"""
Explainable AI for Compliance Module

Generates human-readable explanations for test case generation and compliance mapping,
providing transparency in AI decision-making for regulatory compliance.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from enum import Enum

logger = logging.getLogger(__name__)


class ExplanationType(Enum):
    """Types of explanations that can be generated."""
    COMPLIANCE_MAPPING = "compliance_mapping"
    TEST_CASE_GENERATION = "test_case_generation"
    PRIORITY_ASSIGNMENT = "priority_assignment"
    RISK_ASSESSMENT = "risk_assessment"
    EVIDENCE_REQUIREMENT = "evidence_requirement"


@dataclass
class ComplianceExplanation:
    """Explanation for compliance mapping decision."""
    requirement_id: str
    compliance_standard: str
    mapped_clause: str
    confidence_score: float
    reasoning_steps: List[str]
    evidence_cited: List[str]
    regulatory_context: str
    human_readable_summary: str
    generated_at: str


@dataclass
class TestCaseExplanation:
    """Explanation for test case generation decision."""
    test_case_id: str
    requirement_id: str
    generation_reasoning: List[str]
    step_justification: List[Dict[str, str]]
    compliance_considerations: List[str]
    risk_factors_addressed: List[str]
    human_readable_summary: str
    generated_at: str


@dataclass
class PriorityExplanation:
    """Explanation for priority assignment decision."""
    test_case_id: str
    assigned_priority: str
    priority_score: float
    contributing_factors: List[Dict[str, Any]]
    risk_analysis: str
    business_impact: str
    human_readable_summary: str
    generated_at: str


class ExplainableAI:
    """Explainable AI system for compliance and test case generation."""
    
    def __init__(self, explanation_db_path: str = "data/explanations.json"):
        """Initialize the explainable AI system."""
        self.explanation_db_path = Path(explanation_db_path)
        self.explanation_db_path.parent.mkdir(exist_ok=True)
        self.explanations_db = self._load_explanations()
        
        # Compliance standard knowledge base
        self.compliance_knowledge = self._initialize_compliance_knowledge()
        
        # Explanation templates
        self.explanation_templates = self._initialize_templates()
    
    def _load_explanations(self) -> Dict[str, Any]:
        """Load existing explanations from database."""
        if not self.explanation_db_path.exists():
            return {'compliance': {}, 'test_cases': {}, 'priorities': {}}
        
        try:
            with open(self.explanation_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading explanations: {e}")
            return {'compliance': {}, 'test_cases': {}, 'priorities': {}}
    
    def _save_explanations(self):
        """Save explanations to database."""
        try:
            with open(self.explanation_db_path, 'w') as f:
                json.dump(self.explanations_db, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving explanations: {e}")
    
    def _initialize_compliance_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance standard knowledge base."""
        return {
            'FDA_21_CFR_820': {
                'name': 'FDA Quality System Regulation',
                'description': 'Regulation for medical device quality systems',
                'key_areas': [
                    'Design Controls',
                    'Document Controls',
                    'Corrective and Preventive Actions',
                    'Management Responsibility',
                    'Resource Management'
                ],
                'evidence_requirements': [
                    'Design control documentation',
                    'Risk management files',
                    'Verification and validation records',
                    'Quality system procedures',
                    'Management review records'
                ],
                'test_requirements': [
                    'Design verification testing',
                    'Design validation testing',
                    'Process validation',
                    'Software validation',
                    'Risk management testing'
                ]
            },
            'ISO_13485': {
                'name': 'Medical Devices Quality Management Systems',
                'description': 'International standard for medical device quality management',
                'key_areas': [
                    'Quality Management System',
                    'Management Responsibility',
                    'Resource Management',
                    'Product Realization',
                    'Measurement, Analysis and Improvement'
                ],
                'evidence_requirements': [
                    'Quality manual',
                    'Quality procedures',
                    'Management review records',
                    'Training records',
                    'Corrective action records'
                ],
                'test_requirements': [
                    'Quality system testing',
                    'Process validation',
                    'Product testing',
                    'Supplier evaluation',
                    'Customer satisfaction testing'
                ]
            },
            'IEC_62304': {
                'name': 'Medical Device Software Life Cycle Processes',
                'description': 'Standard for medical device software development',
                'key_areas': [
                    'Software Life Cycle Processes',
                    'Software Development Process',
                    'Software Risk Management',
                    'Software Configuration Management',
                    'Software Problem Resolution'
                ],
                'evidence_requirements': [
                    'Software development plan',
                    'Software requirements specification',
                    'Software design specification',
                    'Software verification and validation',
                    'Software risk management file'
                ],
                'test_requirements': [
                    'Unit testing',
                    'Integration testing',
                    'System testing',
                    'Software risk management testing',
                    'Regression testing'
                ]
            },
            'GDPR': {
                'name': 'General Data Protection Regulation',
                'description': 'EU regulation for data protection and privacy',
                'key_areas': [
                    'Data Processing Principles',
                    'Data Subject Rights',
                    'Data Protection by Design',
                    'Data Breach Notification',
                    'Privacy Impact Assessment'
                ],
                'evidence_requirements': [
                    'Data processing records',
                    'Privacy impact assessments',
                    'Data subject consent records',
                    'Data breach response procedures',
                    'Data protection policies'
                ],
                'test_requirements': [
                    'Data protection testing',
                    'Privacy control testing',
                    'Data subject rights testing',
                    'Consent management testing',
                    'Data breach response testing'
                ]
            },
            'HIPAA': {
                'name': 'Health Insurance Portability and Accountability Act',
                'description': 'US regulation for healthcare data protection',
                'key_areas': [
                    'Administrative Safeguards',
                    'Physical Safeguards',
                    'Technical Safeguards',
                    'Breach Notification',
                    'Business Associate Agreements'
                ],
                'evidence_requirements': [
                    'Security risk assessments',
                    'Policies and procedures',
                    'Training records',
                    'Access control documentation',
                    'Audit logs'
                ],
                'test_requirements': [
                    'Security control testing',
                    'Access control testing',
                    'Audit trail testing',
                    'Encryption testing',
                    'Breach response testing'
                ]
            }
        }
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize explanation templates."""
        return {
            'compliance_mapping': """
**Compliance Mapping Explanation for {requirement_id}**

**Standard**: {compliance_standard}
**Mapped Clause**: {mapped_clause}
**Confidence**: {confidence_score:.1%}

**Reasoning Process**:
{reasoning_steps}

**Evidence Cited**:
{evidence_cited}

**Regulatory Context**:
{regulatory_context}

**Summary**: {human_readable_summary}
            """,
            
            'test_case_generation': """
**Test Case Generation Explanation for {test_case_id}**

**Requirement**: {requirement_id}

**Generation Reasoning**:
{generation_reasoning}

**Step-by-Step Justification**:
{step_justification}

**Compliance Considerations**:
{compliance_considerations}

**Risk Factors Addressed**:
{risk_factors_addressed}

**Summary**: {human_readable_summary}
            """,
            
            'priority_assignment': """
**Priority Assignment Explanation for {test_case_id}**

**Assigned Priority**: {assigned_priority}
**Priority Score**: {priority_score:.1f}/100

**Contributing Factors**:
{contributing_factors}

**Risk Analysis**:
{risk_analysis}

**Business Impact**:
{business_impact}

**Summary**: {human_readable_summary}
            """
        }
    
    def explain_compliance_mapping(self, requirement: Dict[str, Any], 
                                 compliance_standard: str, 
                                 mapped_clause: str,
                                 confidence_score: float) -> ComplianceExplanation:
        """Generate explanation for compliance mapping decision."""
        try:
            # Extract requirement details
            requirement_id = requirement.get('id', 'unknown')
            requirement_text = requirement.get('description', '')
            requirement_type = requirement.get('type', 'unknown')
            
            # Generate reasoning steps
            reasoning_steps = self._generate_compliance_reasoning(
                requirement_text, compliance_standard, mapped_clause
            )
            
            # Identify evidence cited
            evidence_cited = self._identify_evidence_cited(
                requirement_text, compliance_standard
            )
            
            # Get regulatory context
            regulatory_context = self._get_regulatory_context(
                compliance_standard, mapped_clause
            )
            
            # Generate human-readable summary
            human_readable_summary = self._generate_compliance_summary(
                requirement_id, compliance_standard, mapped_clause, 
                confidence_score, reasoning_steps
            )
            
            explanation = ComplianceExplanation(
                requirement_id=requirement_id,
                compliance_standard=compliance_standard,
                mapped_clause=mapped_clause,
                confidence_score=confidence_score,
                reasoning_steps=reasoning_steps,
                evidence_cited=evidence_cited,
                regulatory_context=regulatory_context,
                human_readable_summary=human_readable_summary,
                generated_at=datetime.now().isoformat()
            )
            
            # Save explanation
            self.explanations_db['compliance'][requirement_id] = {
                'compliance_standard': compliance_standard,
                'mapped_clause': mapped_clause,
                'confidence_score': confidence_score,
                'reasoning_steps': reasoning_steps,
                'evidence_cited': evidence_cited,
                'regulatory_context': regulatory_context,
                'human_readable_summary': human_readable_summary,
                'generated_at': explanation.generated_at
            }
            self._save_explanations()
            
            logger.info(f"Compliance explanation generated for {requirement_id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating compliance explanation: {e}")
            raise
    
    def explain_test_case_generation(self, test_case: Any, 
                                   requirement: Dict[str, Any]) -> TestCaseExplanation:
        """Generate explanation for test case generation decision."""
        try:
            test_case_id = getattr(test_case, 'id', 'unknown')
            requirement_id = requirement.get('id', 'unknown')
            
            # Generate generation reasoning
            generation_reasoning = self._generate_test_case_reasoning(
                test_case, requirement
            )
            
            # Generate step-by-step justification
            step_justification = self._generate_step_justification(test_case)
            
            # Identify compliance considerations
            compliance_considerations = self._identify_compliance_considerations(
                test_case, requirement
            )
            
            # Identify risk factors addressed
            risk_factors_addressed = self._identify_risk_factors_addressed(
                test_case, requirement
            )
            
            # Generate human-readable summary
            human_readable_summary = self._generate_test_case_summary(
                test_case_id, requirement_id, generation_reasoning
            )
            
            explanation = TestCaseExplanation(
                test_case_id=test_case_id,
                requirement_id=requirement_id,
                generation_reasoning=generation_reasoning,
                step_justification=step_justification,
                compliance_considerations=compliance_considerations,
                risk_factors_addressed=risk_factors_addressed,
                human_readable_summary=human_readable_summary,
                generated_at=datetime.now().isoformat()
            )
            
            # Save explanation
            self.explanations_db['test_cases'][test_case_id] = {
                'requirement_id': requirement_id,
                'generation_reasoning': generation_reasoning,
                'step_justification': step_justification,
                'compliance_considerations': compliance_considerations,
                'risk_factors_addressed': risk_factors_addressed,
                'human_readable_summary': human_readable_summary,
                'generated_at': explanation.generated_at
            }
            self._save_explanations()
            
            logger.info(f"Test case explanation generated for {test_case_id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating test case explanation: {e}")
            raise
    
    def explain_priority_assignment(self, test_case: Any, 
                                  priority_score: float,
                                  risk_factors: List[Any]) -> PriorityExplanation:
        """Generate explanation for priority assignment decision."""
        try:
            test_case_id = getattr(test_case, 'id', 'unknown')
            
            # Determine assigned priority
            if priority_score >= 80:
                assigned_priority = 'Critical'
            elif priority_score >= 60:
                assigned_priority = 'High'
            elif priority_score >= 40:
                assigned_priority = 'Medium'
            else:
                assigned_priority = 'Low'
            
            # Generate contributing factors
            contributing_factors = self._generate_contributing_factors(
                priority_score, risk_factors
            )
            
            # Generate risk analysis
            risk_analysis = self._generate_risk_analysis(risk_factors)
            
            # Generate business impact analysis
            business_impact = self._generate_business_impact(
                priority_score, assigned_priority, risk_factors
            )
            
            # Generate human-readable summary
            human_readable_summary = self._generate_priority_summary(
                test_case_id, assigned_priority, priority_score, 
                contributing_factors, risk_analysis
            )
            
            explanation = PriorityExplanation(
                test_case_id=test_case_id,
                assigned_priority=assigned_priority,
                priority_score=priority_score,
                contributing_factors=contributing_factors,
                risk_analysis=risk_analysis,
                business_impact=business_impact,
                human_readable_summary=human_readable_summary,
                generated_at=datetime.now().isoformat()
            )
            
            # Save explanation
            self.explanations_db['priorities'][test_case_id] = {
                'assigned_priority': assigned_priority,
                'priority_score': priority_score,
                'contributing_factors': contributing_factors,
                'risk_analysis': risk_analysis,
                'business_impact': business_impact,
                'human_readable_summary': human_readable_summary,
                'generated_at': explanation.generated_at
            }
            self._save_explanations()
            
            logger.info(f"Priority explanation generated for {test_case_id}")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating priority explanation: {e}")
            raise
    
    def _generate_compliance_reasoning(self, requirement_text: str, 
                                     compliance_standard: str, 
                                     mapped_clause: str) -> List[str]:
        """Generate reasoning steps for compliance mapping."""
        reasoning = []
        
        # Analyze requirement text for compliance keywords
        compliance_keywords = self._extract_compliance_keywords(requirement_text)
        
        reasoning.append(f"1. Analyzed requirement text for compliance indicators")
        reasoning.append(f"2. Identified keywords: {', '.join(compliance_keywords)}")
        reasoning.append(f"3. Matched against {compliance_standard} requirements")
        reasoning.append(f"4. Selected clause: {mapped_clause}")
        
        # Add specific reasoning based on standard
        if compliance_standard in self.compliance_knowledge:
            standard_info = self.compliance_knowledge[compliance_standard]
            reasoning.append(f"5. Applied {standard_info['name']} guidelines")
            reasoning.append(f"6. Considered key areas: {', '.join(standard_info['key_areas'][:3])}")
        
        return reasoning
    
    def _extract_compliance_keywords(self, text: str) -> List[str]:
        """Extract compliance-related keywords from text."""
        keywords = []
        
        # Common compliance keywords
        compliance_patterns = [
            r'\b(shall|must|required|mandatory)\b',
            r'\b(compliance|regulatory|standard)\b',
            r'\b(validation|verification|testing)\b',
            r'\b(documentation|record|evidence)\b',
            r'\b(risk|safety|security)\b',
            r'\b(quality|management|process)\b'
        ]
        
        for pattern in compliance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))
    
    def _identify_evidence_cited(self, requirement_text: str, 
                               compliance_standard: str) -> List[str]:
        """Identify evidence requirements cited in the requirement."""
        evidence = []
        
        if compliance_standard in self.compliance_knowledge:
            standard_info = self.compliance_knowledge[compliance_standard]
            evidence_requirements = standard_info['evidence_requirements']
            
            # Check which evidence requirements are mentioned
            for evidence_req in evidence_requirements:
                if any(word in requirement_text.lower() for word in evidence_req.lower().split()):
                    evidence.append(evidence_req)
        
        return evidence
    
    def _get_regulatory_context(self, compliance_standard: str, 
                              mapped_clause: str) -> str:
        """Get regulatory context for the compliance standard."""
        if compliance_standard in self.compliance_knowledge:
            standard_info = self.compliance_knowledge[compliance_standard]
            return f"""
            {standard_info['name']} ({compliance_standard}) is a {standard_info['description']}.
            
            This standard covers key areas including:
            {', '.join(standard_info['key_areas'])}
            
            The mapped clause '{mapped_clause}' relates to the standard's requirements
            for ensuring compliance with regulatory expectations.
            """
        else:
            return f"Compliance standard {compliance_standard} requires adherence to {mapped_clause}."
    
    def _generate_compliance_summary(self, requirement_id: str, 
                                   compliance_standard: str, 
                                   mapped_clause: str,
                                   confidence_score: float, 
                                   reasoning_steps: List[str]) -> str:
        """Generate human-readable compliance summary."""
        return f"""
        Requirement {requirement_id} has been mapped to {compliance_standard} 
        clause '{mapped_clause}' with {confidence_score:.1%} confidence.
        
        This mapping was determined by analyzing the requirement text for compliance
        indicators and matching them against the regulatory standard's requirements.
        The AI system identified relevant keywords and applied standard-specific
        guidelines to make this determination.
        """
    
    def _generate_test_case_reasoning(self, test_case: Any, 
                                    requirement: Dict[str, Any]) -> List[str]:
        """Generate reasoning for test case generation."""
        reasoning = []
        
        test_case_type = getattr(test_case, 'test_case_type', None)
        if test_case_type:
            reasoning.append(f"1. Generated {test_case_type.value} test case based on requirement type")
        
        test_steps = getattr(test_case, 'test_steps', [])
        reasoning.append(f"2. Created {len(test_steps)} test steps to cover requirement scenarios")
        
        compliance_refs = getattr(test_case, 'compliance_refs', [])
        if compliance_refs:
            reasoning.append(f"3. Incorporated compliance references: {', '.join(compliance_refs)}")
        
        priority = getattr(test_case, 'priority', None)
        if priority:
            reasoning.append(f"4. Assigned {priority.value} priority based on requirement criticality")
        
        reasoning.append("5. Applied healthcare testing best practices")
        reasoning.append("6. Ensured test case traceability to requirement")
        
        return reasoning
    
    def _generate_step_justification(self, test_case: Any) -> List[Dict[str, str]]:
        """Generate step-by-step justification for test case."""
        justifications = []
        
        test_steps = getattr(test_case, 'test_steps', [])
        for i, step in enumerate(test_steps, 1):
            justification = {
                'step_number': i,
                'action': getattr(step, 'action', ''),
                'expected_result': getattr(step, 'expected_result', ''),
                'justification': f"Step {i} validates specific aspect of the requirement"
            }
            justifications.append(justification)
        
        return justifications
    
    def _identify_compliance_considerations(self, test_case: Any, 
                                          requirement: Dict[str, Any]) -> List[str]:
        """Identify compliance considerations in test case."""
        considerations = []
        
        compliance_refs = getattr(test_case, 'compliance_refs', [])
        for ref in compliance_refs:
            if ref in self.compliance_knowledge:
                standard_info = self.compliance_knowledge[ref]
                considerations.append(f"Test case addresses {standard_info['name']} requirements")
        
        test_case_type = getattr(test_case, 'test_case_type', None)
        if test_case_type and test_case_type.value == 'compliance':
            considerations.append("Test case specifically validates compliance requirements")
        
        return considerations
    
    def _identify_risk_factors_addressed(self, test_case: Any, 
                                       requirement: Dict[str, Any]) -> List[str]:
        """Identify risk factors addressed by test case."""
        risk_factors = []
        
        test_case_type = getattr(test_case, 'test_case_type', None)
        if test_case_type:
            if test_case_type.value in ['security', 'compliance']:
                risk_factors.append("Addresses security and compliance risks")
            elif test_case_type.value == 'performance':
                risk_factors.append("Addresses performance and scalability risks")
            elif test_case_type.value == 'boundary':
                risk_factors.append("Addresses boundary condition risks")
        
        priority = getattr(test_case, 'priority', None)
        if priority and priority.value in ['critical', 'high']:
            risk_factors.append("Addresses high-priority business risks")
        
        return risk_factors
    
    def _generate_test_case_summary(self, test_case_id: str, 
                                  requirement_id: str, 
                                  generation_reasoning: List[str]) -> str:
        """Generate human-readable test case summary."""
        return f"""
        Test case {test_case_id} was generated for requirement {requirement_id} using
        AI-powered analysis of the requirement text and compliance standards.
        
        The generation process involved analyzing the requirement for testable scenarios,
        applying healthcare testing best practices, and ensuring compliance with
        relevant regulatory standards. The test case includes comprehensive steps
        to validate the requirement's functionality and compliance aspects.
        """
    
    def _generate_contributing_factors(self, priority_score: float, 
                                     risk_factors: List[Any]) -> List[Dict[str, Any]]:
        """Generate contributing factors for priority assignment."""
        factors = []
        
        for risk_factor in risk_factors:
            if hasattr(risk_factor, 'factor_name'):
                factors.append({
                    'factor': risk_factor.factor_name,
                    'value': risk_factor.factor_value,
                    'weight': risk_factor.weight,
                    'impact': risk_factor.impact,
                    'description': risk_factor.description
                })
        
        return factors
    
    def _generate_risk_analysis(self, risk_factors: List[Any]) -> str:
        """Generate risk analysis summary."""
        if not risk_factors:
            return "No significant risk factors identified."
        
        high_risk_factors = [rf for rf in risk_factors if hasattr(rf, 'impact') and rf.impact == 'high']
        medium_risk_factors = [rf for rf in risk_factors if hasattr(rf, 'impact') and rf.impact == 'medium']
        
        analysis = f"Risk analysis identified {len(high_risk_factors)} high-risk factors"
        if medium_risk_factors:
            analysis += f" and {len(medium_risk_factors)} medium-risk factors"
        
        analysis += ". These factors contribute to the overall priority assessment."
        
        return analysis
    
    def _generate_business_impact(self, priority_score: float, 
                                assigned_priority: str, 
                                risk_factors: List[Any]) -> str:
        """Generate business impact analysis."""
        if assigned_priority == 'Critical':
            return "Critical priority indicates potential for significant business impact if not addressed immediately."
        elif assigned_priority == 'High':
            return "High priority indicates important business impact requiring prompt attention."
        elif assigned_priority == 'Medium':
            return "Medium priority indicates moderate business impact that should be addressed in regular testing cycles."
        else:
            return "Low priority indicates minimal business impact that can be addressed when resources are available."
    
    def _generate_priority_summary(self, test_case_id: str, 
                                 assigned_priority: str, 
                                 priority_score: float,
                                 contributing_factors: List[Dict[str, Any]], 
                                 risk_analysis: str) -> str:
        """Generate human-readable priority summary."""
        return f"""
        Test case {test_case_id} has been assigned {assigned_priority} priority 
        (score: {priority_score:.1f}/100) based on AI analysis of multiple factors.
        
        The priority assignment considers requirement criticality, historical defect data,
        code complexity, compliance impact, user impact, and change frequency.
        {risk_analysis}
        
        This priority level ensures appropriate testing resources are allocated
        based on the test case's business impact and risk profile.
        """
    
    def generate_explanation_report(self, explanation_type: ExplanationType, 
                                  entity_id: str) -> Optional[str]:
        """Generate formatted explanation report."""
        try:
            if explanation_type == ExplanationType.COMPLIANCE_MAPPING:
                explanation_data = self.explanations_db['compliance'].get(entity_id)
                if not explanation_data:
                    return None
                
                template = self.explanation_templates['compliance_mapping']
                return template.format(
                    requirement_id=entity_id,
                    compliance_standard=explanation_data['compliance_standard'],
                    mapped_clause=explanation_data['mapped_clause'],
                    confidence_score=explanation_data['confidence_score'],
                    reasoning_steps='\n'.join(f"- {step}" for step in explanation_data['reasoning_steps']),
                    evidence_cited='\n'.join(f"- {evidence}" for evidence in explanation_data['evidence_cited']),
                    regulatory_context=explanation_data['regulatory_context'],
                    human_readable_summary=explanation_data['human_readable_summary']
                )
            
            elif explanation_type == ExplanationType.TEST_CASE_GENERATION:
                explanation_data = self.explanations_db['test_cases'].get(entity_id)
                if not explanation_data:
                    return None
                
                template = self.explanation_templates['test_case_generation']
                return template.format(
                    test_case_id=entity_id,
                    requirement_id=explanation_data['requirement_id'],
                    generation_reasoning='\n'.join(f"- {reason}" for reason in explanation_data['generation_reasoning']),
                    step_justification='\n'.join(f"- Step {step['step_number']}: {step['justification']}" for step in explanation_data['step_justification']),
                    compliance_considerations='\n'.join(f"- {consideration}" for consideration in explanation_data['compliance_considerations']),
                    risk_factors_addressed='\n'.join(f"- {factor}" for factor in explanation_data['risk_factors_addressed']),
                    human_readable_summary=explanation_data['human_readable_summary']
                )
            
            elif explanation_type == ExplanationType.PRIORITY_ASSIGNMENT:
                explanation_data = self.explanations_db['priorities'].get(entity_id)
                if not explanation_data:
                    return None
                
                template = self.explanation_templates['priority_assignment']
                contributing_factors_text = '\n'.join(
                    f"- {factor['factor']}: {factor['value']:.2f} (weight: {factor['weight']:.2f}, impact: {factor['impact']})"
                    for factor in explanation_data['contributing_factors']
                )
                
                return template.format(
                    test_case_id=entity_id,
                    assigned_priority=explanation_data['assigned_priority'],
                    priority_score=explanation_data['priority_score'],
                    contributing_factors=contributing_factors_text,
                    risk_analysis=explanation_data['risk_analysis'],
                    business_impact=explanation_data['business_impact'],
                    human_readable_summary=explanation_data['human_readable_summary']
                )
            
        except Exception as e:
            logger.error(f"Error generating explanation report: {e}")
            return None
    
    def get_explanation_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated explanations."""
        try:
            compliance_count = len(self.explanations_db['compliance'])
            test_case_count = len(self.explanations_db['test_cases'])
            priority_count = len(self.explanations_db['priorities'])
            
            return {
                'total_explanations': compliance_count + test_case_count + priority_count,
                'compliance_explanations': compliance_count,
                'test_case_explanations': test_case_count,
                'priority_explanations': priority_count,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting explanation statistics: {e}")
            return {'error': str(e)}
