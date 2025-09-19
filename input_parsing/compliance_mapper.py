"""
Compliance Mapper for Healthcare Software

Maps healthcare requirements to regulatory standards including FDA, ISO 13485,
IEC 62304, and GDPR for traceability and compliance validation.
"""

import logging
from typing import Dict, List, Optional, Set, Any
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceStandard(Enum):
    """Supported compliance standards."""
    FDA_21_CFR_820 = "FDA_21_CFR_820"
    FDA_21_CFR_11 = "FDA_21_CFR_11"
    ISO_13485 = "ISO_13485"
    IEC_62304 = "IEC_62304"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    IEC_60601 = "IEC_60601"
    IEC_62366 = "IEC_62366"


@dataclass
class ComplianceMapping:
    """Mapping between requirement and compliance standard."""
    requirement_id: str
    standard: ComplianceStandard
    clause: str
    description: str
    traceability_level: str  # direct, indirect, related
    evidence_required: List[str]


class ComplianceMapper:
    """Maps healthcare requirements to regulatory compliance standards."""
    
    def __init__(self):
        """Initialize compliance mapper with standard patterns."""
        self.compliance_patterns = self._initialize_compliance_patterns()
        self.standard_descriptions = self._initialize_standard_descriptions()
        
    def _initialize_compliance_patterns(self) -> Dict[ComplianceStandard, List[str]]:
        """Initialize regex patterns for compliance standard detection."""
        return {
            ComplianceStandard.FDA_21_CFR_820: [
                r'21\\s*CFR\\s*820',
                r'FDA\\s*820',
                r'Quality\\s*System\\s*Regulation',
                r'QSR',
                r'Design\\s*Controls',
                r'Corrective\\s*and\\s*Preventive\\s*Action',
                r'CAPA'
            ],
            ComplianceStandard.FDA_21_CFR_11: [
                r'21\\s*CFR\\s*11',
                r'FDA\\s*11',
                r'Electronic\\s*Records',
                r'Electronic\\s*Signatures',
                r'ERES',
                r'Digital\\s*Signature'
            ],
            ComplianceStandard.ISO_13485: [
                r'ISO\\s*13485',
                r'Medical\\s*Devices',
                r'Quality\\s*Management',
                r'Risk\\s*Management',
                r'Design\\s*and\\s*Development',
                r'Production\\s*and\\s*Service\\s*Provision'
            ],
            ComplianceStandard.IEC_62304: [
                r'IEC\\s*62304',
                r'Medical\\s*Device\\s*Software',
                r'Software\\s*Life\\s*Cycle',
                r'Software\\s*Safety\\s*Classification',
                r'Software\\s*Risk\\s*Management'
            ],
            ComplianceStandard.GDPR: [
                r'GDPR',
                r'General\\s*Data\\s*Protection\\s*Regulation',
                r'Data\\s*Protection',
                r'Personal\\s*Data',
                r'Privacy\\s*by\\s*Design',
                r'Data\\s*Subject\\s*Rights'
            ],
            ComplianceStandard.HIPAA: [
                r'HIPAA',
                r'Health\\s*Insurance\\s*Portability',
                r'Protected\\s*Health\\s*Information',
                r'PHI',
                r'Privacy\\s*Rule',
                r'Security\\s*Rule'
            ],
            ComplianceStandard.IEC_60601: [
                r'IEC\\s*60601',
                r'Medical\\s*Electrical\\s*Equipment',
                r'Basic\\s*Safety',
                r'Essential\\s*Performance',
                r'Risk\\s*Management'
            ],
            ComplianceStandard.IEC_62366: [
                r'IEC\\s*62366',
                r'Usability\\s*Engineering',
                r'Human\\s*Factors',
                r'User\\s*Interface',
                r'Usability\\s*Testing'
            ]
        }
        
    def _initialize_standard_descriptions(self) -> Dict[ComplianceStandard, str]:
        """Initialize descriptions for compliance standards."""
        return {
            ComplianceStandard.FDA_21_CFR_820: "FDA Quality System Regulation for medical devices",
            ComplianceStandard.FDA_21_CFR_11: "FDA Electronic Records and Electronic Signatures regulation",
            ComplianceStandard.ISO_13485: "ISO 13485 Medical devices - Quality management systems",
            ComplianceStandard.IEC_62304: "IEC 62304 Medical device software - Software life cycle processes",
            ComplianceStandard.GDPR: "General Data Protection Regulation for data privacy",
            ComplianceStandard.HIPAA: "Health Insurance Portability and Accountability Act",
            ComplianceStandard.IEC_60601: "IEC 60601 Medical electrical equipment safety standards",
            ComplianceStandard.IEC_62366: "IEC 62366 Medical devices - Usability engineering"
        }
        
    def map_requirement_to_compliance(self, requirement_text: str, 
                                    requirement_id: str) -> List[ComplianceMapping]:
        """
        Map a requirement to applicable compliance standards.
        
        Args:
            requirement_text: The requirement text to analyze
            requirement_id: Unique identifier for the requirement
            
        Returns:
            List of compliance mappings
        """
        mappings = []
        text_lower = requirement_text.lower()
        
        for standard, patterns in self.compliance_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    mapping = self._create_compliance_mapping(
                        requirement_id, standard, requirement_text
                    )
                    mappings.append(mapping)
                    break  # Found a match for this standard
                    
        # If no direct matches, check for indirect compliance needs
        if not mappings:
            indirect_mappings = self._check_indirect_compliance(requirement_text, requirement_id)
            mappings.extend(indirect_mappings)
            
        return mappings
        
    def _create_compliance_mapping(self, requirement_id: str, 
                                 standard: ComplianceStandard, 
                                 requirement_text: str) -> ComplianceMapping:
        """Create a compliance mapping for a requirement."""
        clause = self._extract_clause_reference(requirement_text, standard)
        description = self.standard_descriptions[standard]
        traceability_level = self._determine_traceability_level(requirement_text, standard)
        evidence_required = self._determine_evidence_requirements(standard)
        
        return ComplianceMapping(
            requirement_id=requirement_id,
            standard=standard,
            clause=clause,
            description=description,
            traceability_level=traceability_level,
            evidence_required=evidence_required
        )
        
    def _extract_clause_reference(self, text: str, standard: ComplianceStandard) -> str:
        """Extract specific clause reference from text."""
        # Look for specific clause numbers
        clause_patterns = [
            r'clause\\s*(\\d+(?:\\.\\d+)*)',
            r'section\\s*(\\d+(?:\\.\\d+)*)',
            r'part\\s*(\\d+(?:\\.\\d+)*)',
            r'\\d+\\.\\d+(?:\\.\\d+)*'
        ]
        
        for pattern in clause_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # Return general reference based on standard
        general_refs = {
            ComplianceStandard.FDA_21_CFR_820: "820.30 (Design Controls)",
            ComplianceStandard.FDA_21_CFR_11: "11.10 (Controls for closed systems)",
            ComplianceStandard.ISO_13485: "7.3 (Design and Development)",
            ComplianceStandard.IEC_62304: "5.1 (Software Life Cycle Processes)",
            ComplianceStandard.GDPR: "Article 25 (Data protection by design)",
            ComplianceStandard.HIPAA: "164.312 (Technical safeguards)",
            ComplianceStandard.IEC_60601: "4.1 (General requirements)",
            ComplianceStandard.IEC_62366: "5.1 (Usability engineering process)"
        }
        
        return general_refs.get(standard, "General requirements")
        
    def _determine_traceability_level(self, text: str, standard: ComplianceStandard) -> str:
        """Determine the traceability level for the mapping."""
        text_lower = text.lower()
        
        # Direct traceability indicators
        direct_indicators = [
            'shall comply with', 'must meet', 'required by', 'mandated by',
            'in accordance with', 'per', 'as specified in'
        ]
        
        if any(indicator in text_lower for indicator in direct_indicators):
            return "direct"
            
        # Indirect traceability indicators
        indirect_indicators = [
            'should consider', 'recommended', 'best practice', 'guidance',
            'may require', 'could impact'
        ]
        
        if any(indicator in text_lower for indicator in indirect_indicators):
            return "indirect"
            
        return "related"
        
    def _determine_evidence_requirements(self, standard: ComplianceStandard) -> List[str]:
        """Determine evidence requirements for compliance validation."""
        evidence_map = {
            ComplianceStandard.FDA_21_CFR_820: [
                "Design and development plan",
                "Design input/output documentation",
                "Design verification and validation records",
                "Risk management file",
                "Design review records"
            ],
            ComplianceStandard.FDA_21_CFR_11: [
                "System validation documentation",
                "Electronic signature procedures",
                "Audit trail records",
                "Access control documentation",
                "System security measures"
            ],
            ComplianceStandard.ISO_13485: [
                "Quality management system documentation",
                "Risk management documentation",
                "Design and development records",
                "Management review records",
                "Corrective and preventive action records"
            ],
            ComplianceStandard.IEC_62304: [
                "Software development plan",
                "Software requirements specification",
                "Software architecture documentation",
                "Software verification and validation records",
                "Software risk management file"
            ],
            ComplianceStandard.GDPR: [
                "Data protection impact assessment",
                "Privacy by design documentation",
                "Data processing agreements",
                "Consent management records",
                "Data breach response procedures"
            ],
            ComplianceStandard.HIPAA: [
                "Risk assessment documentation",
                "Security policies and procedures",
                "Access control documentation",
                "Audit logs and monitoring records",
                "Incident response procedures"
            ],
            ComplianceStandard.IEC_60601: [
                "Risk management file",
                "Essential performance documentation",
                "Safety testing records",
                "Usability engineering file",
                "Clinical evaluation report"
            ],
            ComplianceStandard.IEC_62366: [
                "Usability engineering plan",
                "User interface specification",
                "Usability testing records",
                "Use error analysis",
                "Usability validation report"
            ]
        }
        
        return evidence_map.get(standard, ["General compliance documentation"])
        
    def _check_indirect_compliance(self, text: str, requirement_id: str) -> List[ComplianceMapping]:
        """Check for indirect compliance requirements based on content analysis."""
        mappings = []
        text_lower = text.lower()
        
        # Healthcare-specific compliance triggers
        healthcare_triggers = {
            ComplianceStandard.FDA_21_CFR_820: [
                'medical device', 'patient safety', 'quality system', 'design control',
                'risk management', 'corrective action', 'preventive action'
            ],
            ComplianceStandard.FDA_21_CFR_11: [
                'electronic record', 'electronic signature', 'digital signature',
                'audit trail', 'electronic submission'
            ],
            ComplianceStandard.ISO_13485: [
                'quality management', 'medical device', 'risk management',
                'design and development', 'production control'
            ],
            ComplianceStandard.IEC_62304: [
                'software', 'medical device software', 'software life cycle',
                'software safety', 'software risk'
            ],
            ComplianceStandard.GDPR: [
                'personal data', 'patient data', 'privacy', 'data protection',
                'consent', 'data subject', 'personal information'
            ],
            ComplianceStandard.HIPAA: [
                'protected health information', 'phi', 'health information',
                'patient information', 'medical record', 'healthcare data'
            ],
            ComplianceStandard.IEC_60601: [
                'medical electrical', 'safety', 'essential performance',
                'basic safety', 'medical equipment'
            ],
            ComplianceStandard.IEC_62366: [
                'usability', 'user interface', 'human factors', 'user experience',
                'user interaction', 'interface design'
            ]
        }
        
        for standard, triggers in healthcare_triggers.items():
            if any(trigger in text_lower for trigger in triggers):
                mapping = ComplianceMapping(
                    requirement_id=requirement_id,
                    standard=standard,
                    clause="General requirements",
                    description=self.standard_descriptions[standard],
                    traceability_level="indirect",
                    evidence_required=self._determine_evidence_requirements(standard)
                )
                mappings.append(mapping)
                
        return mappings
        
    def generate_traceability_matrix(self, requirements: List[Any], 
                                  mappings: List[ComplianceMapping]) -> Dict[str, Any]:
        """
        Generate a traceability matrix linking requirements to compliance standards.
        
        Args:
            requirements: List of requirements
            mappings: List of compliance mappings
            
        Returns:
            Traceability matrix dictionary
        """
        matrix = {
            'requirements': {},
            'standards': {},
            'traceability_summary': {}
        }
        
        # Group mappings by requirement
        req_mappings = {}
        for mapping in mappings:
            if mapping.requirement_id not in req_mappings:
                req_mappings[mapping.requirement_id] = []
            req_mappings[mapping.requirement_id].append(mapping)
            
        # Build requirement-to-standard mapping
        for req in requirements:
            req_id = getattr(req, 'id', str(req))
            matrix['requirements'][req_id] = {
                'description': getattr(req, 'description', ''),
                'compliance_standards': []
            }
            
            if req_id in req_mappings:
                for mapping in req_mappings[req_id]:
                    matrix['requirements'][req_id]['compliance_standards'].append({
                        'standard': mapping.standard.value,
                        'clause': mapping.clause,
                        'traceability_level': mapping.traceability_level,
                        'evidence_required': mapping.evidence_required
                    })
                    
        # Build standard-to-requirement mapping
        for mapping in mappings:
            standard = mapping.standard.value
            if standard not in matrix['standards']:
                matrix['standards'][standard] = {
                    'description': mapping.description,
                    'requirements': []
                }
                
            matrix['standards'][standard]['requirements'].append({
                'requirement_id': mapping.requirement_id,
                'clause': mapping.clause,
                'traceability_level': mapping.traceability_level
            })
            
        # Generate summary statistics
        matrix['traceability_summary'] = {
            'total_requirements': len(requirements),
            'total_standards': len(matrix['standards']),
            'mapped_requirements': len(req_mappings),
            'coverage_percentage': (len(req_mappings) / len(requirements) * 100) if requirements else 0
        }
        
        return matrix
