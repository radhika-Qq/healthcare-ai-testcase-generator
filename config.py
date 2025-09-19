"""
Configuration settings for Healthcare AI Test Case Generator
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration class for the Healthcare AI Test Case Generator."""
    
    # Project settings
    PROJECT_NAME = "Healthcare AI Test Case Generator"
    VERSION = "1.0.0"
    
    # Environment detection
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # API Configuration
    GOOGLE_AI_API_KEY: Optional[str] = os.getenv('GOOGLE_AI_API_KEY')
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Alternative AI providers
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    
    # Export Configuration
    DEFAULT_EXPORT_FORMAT = os.getenv('DEFAULT_EXPORT_FORMAT', 'excel')
    DEFAULT_OUTPUT_DIR = Path(os.getenv('DEFAULT_OUTPUT_DIR', 'output'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = Path(os.getenv('LOG_FILE', 'logs/healthcare_ai_generator.log'))
    
    # Test Configuration
    TEST_DATA_DIR = Path(os.getenv('TEST_DATA_DIR', 'test_data'))
    TEST_OUTPUT_DIR = Path(os.getenv('TEST_OUTPUT_DIR', 'test_output'))
    
    # Document Processing Configuration
    MAX_DOCUMENT_SIZE = int(os.getenv('MAX_DOCUMENT_SIZE', '50'))  # MB
    SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.docx', '.doc', '.xml', '.html', '.txt']
    
    # AI Configuration
    AI_MODEL_NAME = os.getenv('AI_MODEL_NAME', 'gemini-pro')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '8000'))
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    # Compliance Configuration
    SUPPORTED_COMPLIANCE_STANDARDS = [
        'FDA_21_CFR_820',
        'FDA_21_CFR_11',
        'ISO_13485',
        'IEC_62304',
        'GDPR',
        'HIPAA',
        'IEC_60601',
        'IEC_62366'
    ]
    
    # Test Case Configuration
    DEFAULT_TEST_CASE_TYPES = [
        'positive',
        'negative',
        'boundary',
        'integration',
        'performance',
        'security',
        'usability',
        'compliance'
    ]
    
    DEFAULT_PRIORITIES = [
        'critical',
        'high',
        'medium',
        'low'
    ]
    
    # Export Format Configuration
    JIRA_CONFIG = {
        'default_project_key': os.getenv('JIRA_PROJECT_KEY', 'TEST'),
        'default_issue_type': os.getenv('JIRA_ISSUE_TYPE', 'Test'),
        'api_url': os.getenv('JIRA_API_URL', ''),
        'username': os.getenv('JIRA_USERNAME', ''),
        'api_token': os.getenv('JIRA_API_TOKEN', '')
    }
    
    AZURE_DEVOPS_CONFIG = {
        'organization': os.getenv('AZURE_DEVOPS_ORG', ''),
        'project': os.getenv('AZURE_DEVOPS_PROJECT', ''),
        'personal_access_token': os.getenv('AZURE_DEVOPS_PAT', '')
    }
    
    # File Paths
    BASE_DIR = Path(__file__).parent
    INPUT_PARSING_DIR = BASE_DIR / 'input_parsing'
    TEST_CASE_GENERATION_DIR = BASE_DIR / 'test_case_generation'
    DOCS_DIR = BASE_DIR / 'docs'
    EXAMPLES_DIR = BASE_DIR / 'examples'
    SCRIPTS_DIR = BASE_DIR / 'scripts'
    TESTS_DIR = BASE_DIR / 'tests'
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist."""
        directories = [
            cls.DEFAULT_OUTPUT_DIR,
            cls.LOG_FILE.parent,
            cls.TEST_DATA_DIR,
            cls.TEST_OUTPUT_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return any issues."""
        issues = []
        
        # Check if required directories exist
        if not cls.INPUT_PARSING_DIR.exists():
            issues.append(f"Input parsing directory not found: {cls.INPUT_PARSING_DIR}")
        
        if not cls.TEST_CASE_GENERATION_DIR.exists():
            issues.append(f"Test case generation directory not found: {cls.TEST_CASE_GENERATION_DIR}")
        
        # Check API configuration
        has_google_ai = cls.GOOGLE_AI_API_KEY or cls.GOOGLE_APPLICATION_CREDENTIALS
        has_openai = cls.OPENAI_API_KEY
        has_anthropic = cls.ANTHROPIC_API_KEY
        
        if not any([has_google_ai, has_openai, has_anthropic]):
            issues.append("No AI API key or credentials configured (Google AI, OpenAI, or Anthropic)")
        
        # Check export configuration
        if cls.DEFAULT_EXPORT_FORMAT not in ['json', 'excel', 'csv', 'jira', 'azure_devops']:
            issues.append(f"Invalid default export format: {cls.DEFAULT_EXPORT_FORMAT}")
        
        # Check environment-specific settings
        if cls.ENVIRONMENT == 'production':
            if not has_google_ai:
                issues.append("Production environment requires Google AI configuration")
            if cls.LOG_LEVEL == 'DEBUG':
                issues.append("Production environment should not use DEBUG log level")
        
        return issues
    
    @classmethod
    def get_ai_config(cls) -> dict:
        """Get AI configuration dictionary."""
        return {
            'model_name': cls.AI_MODEL_NAME,
            'max_tokens': cls.AI_MAX_TOKENS,
            'temperature': cls.AI_TEMPERATURE,
            'google_ai_api_key': cls.GOOGLE_AI_API_KEY,
            'google_cloud_project_id': cls.GOOGLE_CLOUD_PROJECT_ID,
            'google_application_credentials': cls.GOOGLE_APPLICATION_CREDENTIALS,
            'openai_api_key': cls.OPENAI_API_KEY,
            'anthropic_api_key': cls.ANTHROPIC_API_KEY,
            'environment': cls.ENVIRONMENT
        }
    
    @classmethod
    def get_environment_config(cls) -> dict:
        """Get environment-specific configuration."""
        base_config = {
            'environment': cls.ENVIRONMENT,
            'log_level': cls.LOG_LEVEL,
            'debug_mode': cls.ENVIRONMENT == 'development'
        }
        
        if cls.ENVIRONMENT == 'development':
            base_config.update({
                'enable_debug_logging': True,
                'enable_hot_reload': True,
                'enable_profiling': True
            })
        elif cls.ENVIRONMENT == 'testing':
            base_config.update({
                'enable_debug_logging': True,
                'use_mock_apis': True,
                'disable_external_calls': True
            })
        elif cls.ENVIRONMENT == 'production':
            base_config.update({
                'enable_debug_logging': False,
                'enable_hot_reload': False,
                'enable_profiling': False,
                'require_https': True
            })
        
        return base_config
    
    @classmethod
    def get_export_config(cls, format_type: str) -> dict:
        """Get export configuration for specific format."""
        if format_type == 'jira':
            return cls.JIRA_CONFIG
        elif format_type == 'azure_devops':
            return cls.AZURE_DEVOPS_CONFIG
        else:
            return {
                'format': format_type,
                'output_dir': cls.DEFAULT_OUTPUT_DIR
            }
