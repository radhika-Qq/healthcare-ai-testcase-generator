"""
Requirement Extractor for Healthcare Software

Uses AI to extract functional and non-functional requirements from
parsed healthcare documents with context and priority identification.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from dataclasses import dataclass
from enum import Enum

try:
    import google.generativeai as genai
    from google.cloud import aiplatform
except ImportError:
    genai = None
    aiplatform = None

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    """Types of requirements."""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    USABILITY = "usability"
    RELIABILITY = "reliability"


class Priority(Enum):
    """Requirement priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Requirement:
    """Structured requirement data."""
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


class RequirementExtractor:
    """AI-powered requirement extractor for healthcare software."""
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize the requirement extractor.
        
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
            logger.warning("Google Generative AI not available. Using rule-based extraction.")
            self.model = None
            
    def extract_requirements(self, parsed_doc: Dict[str, Any]) -> List[Requirement]:
        """
        Extract requirements from parsed document.
        
        Args:
            parsed_doc: Parsed document dictionary
            
        Returns:
            List of extracted requirements
        """
        clean_text = self._extract_clean_text(parsed_doc)
        
        if self.model:
            return self._extract_with_ai(clean_text, parsed_doc)
        else:
            return self._extract_with_rules(clean_text, parsed_doc)
            
    def _extract_clean_text(self, parsed_doc: Dict[str, Any]) -> str:
        """Extract clean text from parsed document."""
        text_parts = []
        
        for item in parsed_doc['content']:
            if item['type'] in ['text', 'paragraph', 'html_element', 'text_line']:
                text_parts.append(item['text'])
            elif item['type'] == 'table':
                for row in item['data']:
                    text_parts.append(' | '.join(str(cell) for cell in row))
                    
        return '\n'.join(text_parts)
        
    def _extract_with_ai(self, text: str, parsed_doc: Dict[str, Any]) -> List[Requirement]:
        """Extract requirements using AI."""
        prompt = self._create_extraction_prompt(text)
        
        try:
            response = self.model.generate_content(prompt)
            requirements_data = json.loads(response.text)
            
            requirements = []
            for i, req_data in enumerate(requirements_data.get('requirements', [])):
                requirement = Requirement(
                    id=req_data.get('id', f"REQ-{i+1:03d}"),
                    description=req_data.get('description', ''),
                    type=RequirementType(req_data.get('type', 'functional')),
                    priority=Priority(req_data.get('priority', 'medium')),
                    source_section=req_data.get('source_section', ''),
                    compliance_refs=req_data.get('compliance_refs', []),
                    context=req_data.get('context', ''),
                    acceptance_criteria=req_data.get('acceptance_criteria', []),
                    dependencies=req_data.get('dependencies', []),
                    raw_text=req_data.get('raw_text', '')
                )
                requirements.append(requirement)
                
            return requirements
            
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return self._extract_with_rules(text, parsed_doc)
            
    def _create_extraction_prompt(self, text: str) -> str:
        """Create prompt for AI-based requirement extraction."""
        return f"""
        Extract all functional and non-functional requirements from the following healthcare software specification document.
        Identify key entities, conditions, and expected behaviors with context.
        
        For each requirement, provide:
        - A unique ID (REQ-XXX format)
        - Clear description
        - Type (functional, non_functional, performance, security, compliance, usability, reliability)
        - Priority (critical, high, medium, low)
        - Source section or location
        - Compliance references (FDA, ISO 13485, IEC 62304, GDPR, etc.)
        - Context and background
        - Acceptance criteria
        - Dependencies on other requirements
        - Raw text from document
        
        Focus on healthcare-specific requirements including:
        - Patient safety requirements
        - Data privacy and security
        - Regulatory compliance
        - Medical device functionality
        - Clinical workflow integration
        - Audit trail requirements
        - Risk management
        
        Document text:
        {text[:8000]}  # Limit text length for API
        
        Return the result as a JSON object with a 'requirements' array.
        """
        
    def _extract_with_rules(self, text: str, parsed_doc: Dict[str, Any]) -> List[Requirement]:
        """Extract requirements using rule-based approach."""
        requirements = []
        
        # Split text into sections
        sections = self._split_into_sections(text)
        
        req_counter = 1
        for section_title, section_text in sections:
            section_requirements = self._extract_from_section(
                section_text, section_title, req_counter
            )
            requirements.extend(section_requirements)
            req_counter += len(section_requirements)
            
        return requirements
        
    def _split_into_sections(self, text: str) -> List[Tuple[str, str]]:
        """Split text into logical sections."""
        sections = []
        
        # Look for section headers (numbered or titled)
        section_patterns = [
            r'^\d+\.?\s+([A-Z][^\n]*?)(?=\n|$)',  # "1. Section Title" or "1 Section Title"
            r'^([A-Z][A-Z\s]+)(?=\n|$)',          # "SECTION TITLE"
        ]
        
        lines = text.split('\n')
        current_section = "General"
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if current_text:
                        sections.append((current_section, '\n'.join(current_text)))
                    current_section = line
                    current_text = []
                    is_header = True
                    break
                    
            if not is_header:
                current_text.append(line)
                
        if current_text:
            sections.append((current_section, '\n'.join(current_text)))
            
        return sections
        
    def _extract_from_section(self, text: str, section_title: str, start_id: int) -> List[Requirement]:
        """Extract requirements from a specific section."""
        requirements = []
        
        # Look for requirement patterns
        req_patterns = [
            r'(?:The system shall|The software shall|The application shall|Shall|Must|Should)\s+([^\n]+)',
            r'(?:REQ|Requirement)\s*[\d\.]+\s*:?\s*([^\n]+)',
            r'\d+\.\d+\s+([^\n]+)',
        ]
        
        sentences = re.split(r'[.!?]+', text)
        req_counter = start_id
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            for pattern in req_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    req_text = match.group(1) if match.groups() else sentence
                    
                    # Determine requirement type
                    req_type = self._classify_requirement_type(req_text)
                    
                    # Determine priority
                    priority = self._determine_priority(req_text, section_title)
                    
                    # Extract compliance references
                    compliance_refs = self._extract_compliance_refs(req_text)
                    
                    requirement = Requirement(
                        id=f"REQ-{req_counter:03d}",
                        description=req_text,
                        type=req_type,
                        priority=priority,
                        source_section=section_title,
                        compliance_refs=compliance_refs,
                        context=section_title,
                        acceptance_criteria=self._extract_acceptance_criteria(req_text),
                        dependencies=[],
                        raw_text=sentence
                    )
                    
                    requirements.append(requirement)
                    req_counter += 1
                    break
                    
        return requirements
        
    def _classify_requirement_type(self, text: str) -> RequirementType:
        """Classify requirement type based on content."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['performance', 'speed', 'response time', 'throughput']):
            return RequirementType.PERFORMANCE
        elif any(word in text_lower for word in ['security', 'encrypt', 'authenticate', 'authorize']):
            return RequirementType.SECURITY
        elif any(word in text_lower for word in ['compliance', 'fda', 'iso', 'iec', 'gdpr']):
            return RequirementType.COMPLIANCE
        elif any(word in text_lower for word in ['usability', 'user interface', 'user experience', 'ui']):
            return RequirementType.USABILITY
        elif any(word in text_lower for word in ['reliability', 'availability', 'uptime', 'fault']):
            return RequirementType.RELIABILITY
        elif any(word in text_lower for word in ['shall', 'must', 'should', 'will']):
            return RequirementType.FUNCTIONAL
        else:
            return RequirementType.NON_FUNCTIONAL
            
    def _determine_priority(self, text: str, section_title: str) -> Priority:
        """Determine requirement priority."""
        text_lower = text.lower()
        section_lower = section_title.lower()
        
        if any(word in text_lower for word in ['critical', 'essential', 'mandatory', 'required']):
            return Priority.CRITICAL
        elif any(word in text_lower for word in ['important', 'high priority', 'urgent']):
            return Priority.HIGH
        elif any(word in section_lower for word in ['safety', 'security', 'compliance']):
            return Priority.HIGH
        elif any(word in text_lower for word in ['optional', 'nice to have', 'low priority']):
            return Priority.LOW
        else:
            return Priority.MEDIUM
            
    def _extract_compliance_refs(self, text: str) -> List[str]:
        """Extract compliance references from text."""
        compliance_patterns = [
            r'FDA\\s*[\\d\\.\\-]*',
            r'ISO\\s*[\\d\\.\\-]*',
            r'IEC\\s*[\\d\\.\\-]*',
            r'GDPR',
            r'HIPAA',
            r'21\\s*CFR\\s*[\\d\\.\\-]*',
        ]
        
        refs = []
        for pattern in compliance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            refs.extend(matches)
            
        return list(set(refs))  # Remove duplicates
        
    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """Extract acceptance criteria from requirement text."""
        criteria = []
        
        # Look for criteria patterns
        criteria_patterns = [
            r'when\s+([^\n]+)',
            r'if\s+([^\n]+)',
            r'within\s+([^\n]+)',
            r'less than\s+([^\n]+)',
            r'greater than\s+([^\n]+)',
        ]
        
        for pattern in criteria_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            criteria.extend(matches)
            
        return criteria
        
    def summarize_requirements(self, requirements: List[Requirement]) -> Dict[str, Any]:
        """
        Summarize extracted requirements into standardized format.
        
        Args:
            requirements: List of extracted requirements
            
        Returns:
            Summary dictionary
        """
        summary = {
            'total_requirements': len(requirements),
            'by_type': {},
            'by_priority': {},
            'compliance_refs': set(),
            'requirements': []
        }
        
        for req in requirements:
            # Count by type
            req_type = req.type.value
            summary['by_type'][req_type] = summary['by_type'].get(req_type, 0) + 1
            
            # Count by priority
            priority = req.priority.value
            summary['by_priority'][priority] = summary['by_priority'].get(priority, 0) + 1
            
            # Collect compliance references
            summary['compliance_refs'].update(req.compliance_refs)
            
            # Add requirement summary
            summary['requirements'].append({
                'id': req.id,
                'description': req.description,
                'type': req_type,
                'priority': priority,
                'compliance_refs': req.compliance_refs
            })
            
        # Convert set to list for JSON serialization
        summary['compliance_refs'] = list(summary['compliance_refs'])
        
        return summary
