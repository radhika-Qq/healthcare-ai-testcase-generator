"""
Utility functions for Input & Parsing Module

Helper functions for document processing, text cleaning, and data validation.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json

logger = logging.getLogger(__name__)


def parse_healthcare_document(file_path: Union[str, Path], 
                            api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to parse a healthcare document and extract requirements.
    
    Args:
        file_path: Path to the healthcare document
        api_key: Optional API key for AI services
        
    Returns:
        Dictionary containing parsed document and extracted requirements
    """
    from .document_parser import DocumentParser
    from .requirement_extractor import RequirementExtractor
    from .compliance_mapper import ComplianceMapper
    
    # Initialize components
    doc_parser = DocumentParser()
    req_extractor = RequirementExtractor(api_key=api_key)
    compliance_mapper = ComplianceMapper()
    
    try:
        # Parse document
        logger.info(f"Parsing document: {file_path}")
        parsed_doc = doc_parser.parse_document(file_path)
        
        # Extract requirements
        logger.info("Extracting requirements...")
        requirements = req_extractor.extract_requirements(parsed_doc)
        
        # Map compliance standards
        logger.info("Mapping compliance standards...")
        compliance_mappings = []
        for req in requirements:
            mappings = compliance_mapper.map_requirement_to_compliance(
                req.description, req.id
            )
            compliance_mappings.extend(mappings)
            
        # Generate traceability matrix
        traceability_matrix = compliance_mapper.generate_traceability_matrix(
            requirements, compliance_mappings
        )
        
        # Summarize requirements
        req_summary = req_extractor.summarize_requirements(requirements)
        
        return {
            'document_info': {
                'file_path': str(file_path),
                'file_type': parsed_doc.get('file_type', 'unknown'),
                'total_pages': parsed_doc.get('total_pages', 0),
                'parsing_timestamp': parsed_doc.get('parsing_timestamp', ''),
            },
            'requirements': [_convert_requirement_to_dict(req) for req in requirements],
            'compliance_mappings': [mapping.__dict__ for mapping in compliance_mappings],
            'traceability_matrix': traceability_matrix,
            'summary': req_summary
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error parsing healthcare document: {error_msg}")
        
        # Provide more specific error messages
        if "not a valid word document" in error_msg.lower():
            raise ValueError("The uploaded file is not a valid Word document. Please ensure it's a proper .docx file and not corrupted.")
        elif "word document appears to be corrupted" in error_msg.lower():
            raise ValueError("The Word document appears to be corrupted. Please try re-saving the file or use a different document.")
        elif "zip file" in error_msg.lower():
            raise ValueError("Document parsing failed: The file appears to be corrupted or in an unsupported format. Please try with a different file or ensure the file is not corrupted.")
        elif "not a zip file" in error_msg.lower():
            raise ValueError("Document parsing failed: The file format is not supported. Please ensure you're uploading a valid PDF, Word document, or text file.")
        elif "file not found" in error_msg.lower():
            raise FileNotFoundError(f"Document not found: {file_path}")
        elif "unsupported file format" in error_msg.lower():
            raise ValueError(f"Unsupported file format. Please use one of: {', '.join(['.pdf', '.docx', '.doc', '.xml', '.html', '.txt'])}")
        else:
            raise ValueError(f"Document parsing failed: {error_msg}. Please try with a different file or check the file format.")


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Remove extra whitespace
    text = re.sub(r'\\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\\w\\s\\.,;:!?\\-()\\[\\]{}]', '', text)
    
    # Normalize line breaks
    text = re.sub(r'\\n+', '\\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Extract logical sections from text based on headers and structure.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of sections with metadata
    """
    sections = []
    lines = text.split('\\n')
    current_section = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a header
        if is_section_header(line):
            # Save previous section
            if current_section:
                sections.append(current_section)
                
            # Start new section
            current_section = {
                'title': line,
                'level': get_header_level(line),
                'content': [],
                'start_line': i
            }
        else:
            # Add content to current section
            if current_section:
                current_section['content'].append(line)
            else:
                # Create default section for content without header
                current_section = {
                    'title': 'Introduction',
                    'level': 1,
                    'content': [line],
                    'start_line': i
                }
                
    # Add final section
    if current_section:
        sections.append(current_section)
        
    return sections


def is_section_header(line: str) -> bool:
    """Check if a line is a section header."""
    # Common header patterns
    header_patterns = [
        r'^\\d+\\.?\\s+[A-Z]',  # Numbered sections
        r'^[A-Z][A-Z\\s]+$',     # All caps headers
        r'^[A-Z][a-z].*:$',      # Title case with colon
        r'^\\d+\\.\\d+',         # Decimal numbered sections
    ]
    
    return any(re.match(pattern, line) for pattern in header_patterns)


def get_header_level(line: str) -> int:
    """Determine the hierarchy level of a header."""
    # Count leading numbers or dots
    match = re.match(r'^(\\d+)(?:\\.|\\s)', line)
    if match:
        return len(match.group(1))
        
    # Check for all caps (usually level 1)
    if line.isupper() and len(line) > 3:
        return 1
        
    # Check for title case with colon (usually level 2)
    if ':' in line and line[0].isupper():
        return 2
        
    return 1


def validate_requirement(requirement: Dict[str, Any]) -> List[str]:
    """
    Validate a requirement object for completeness and correctness.
    
    Args:
        requirement: Requirement dictionary to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    required_fields = ['id', 'description', 'type', 'priority']
    for field in required_fields:
        if field not in requirement or not requirement[field]:
            errors.append(f"Missing required field: {field}")
            
    # Validate ID format
    if 'id' in requirement:
        if not re.match(r'^[A-Z]+-\\d+$', requirement['id']):
            errors.append("Invalid requirement ID format. Expected format: REQ-001")
            
    # Validate type
    valid_types = ['functional', 'non_functional', 'performance', 'security', 
                   'compliance', 'usability', 'reliability']
    if 'type' in requirement and requirement['type'] not in valid_types:
        errors.append(f"Invalid requirement type. Must be one of: {valid_types}")
        
    # Validate priority
    valid_priorities = ['critical', 'high', 'medium', 'low']
    if 'priority' in requirement and requirement['priority'] not in valid_priorities:
        errors.append(f"Invalid priority. Must be one of: {valid_priorities}")
        
    # Validate description length
    if 'description' in requirement:
        desc = requirement['description']
        if len(desc) < 10:
            errors.append("Requirement description too short (minimum 10 characters)")
        elif len(desc) > 1000:
            errors.append("Requirement description too long (maximum 1000 characters)")
            
    return errors


def export_to_json(data: Dict[str, Any], output_path: Union[str, Path]) -> None:
    """
    Export data to JSON file.
    
    Args:
        data: Data to export
        output_path: Path for output file
    """
    output_path = Path(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Data exported to: {output_path}")


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load data from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded data dictionary
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'
        
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
        
    return filename


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text for tagging and categorization.
    
    Args:
        text: Text to analyze
        min_length: Minimum keyword length
        
    Returns:
        List of unique keywords
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\\b\\w+\\b', text.lower())
    
    # Filter by length and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'shall'
    }
    
    keywords = [
        word for word in words 
        if len(word) >= min_length and word not in stop_words
    ]
    
    # Return unique keywords
    return list(set(keywords))


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings using simple word overlap.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
        
    # Extract words from both texts
    words1 = set(re.findall(r'\\b\\w+\\b', text1.lower()))
    words2 = set(re.findall(r'\\b\\w+\\b', text2.lower()))
    
    if not words1 and not words2:
        return 1.0
        
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def _convert_requirement_to_dict(req) -> Dict[str, Any]:
    """Convert Requirement object to dictionary with string values for enums."""
    return {
        'id': req.id,
        'description': req.description,
        'type': req.type.value if hasattr(req.type, 'value') else str(req.type),
        'priority': req.priority.value if hasattr(req.priority, 'value') else str(req.priority),
        'source_section': req.source_section,
        'compliance_refs': req.compliance_refs,
        'context': req.context,
        'acceptance_criteria': req.acceptance_criteria,
        'dependencies': req.dependencies,
        'raw_text': req.raw_text
    }
