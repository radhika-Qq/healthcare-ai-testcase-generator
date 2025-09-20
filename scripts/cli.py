#!/usr/bin/env python3
"""
Command Line Interface for Healthcare AI Test Case Generator

This script provides a command-line interface for the Healthcare AI Test Case Generator,
allowing users to parse documents, generate test cases, and export results from the command line.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from input_parsing import parse_healthcare_document
from test_case_generation import (
    TestCaseGenerator, 
    ComplianceValidator, 
    ExportManager, 
    TraceabilityMatrixGenerator
)
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthcareAICLI:
    """Command Line Interface for Healthcare AI Test Case Generator."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.config = Config()
        self.setup_directories()
        
    def setup_directories(self):
        """Set up required directories."""
        self.config.create_directories()
        
    def parse_document(self, document_path: str, output_path: Optional[str] = None) -> dict:
        """Parse a healthcare document."""
        logger.info(f"Parsing document: {document_path}")
        
        try:
            result = parse_healthcare_document(document_path, self.config.GOOGLE_AI_API_KEY)
            
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                logger.info(f"Parsed data saved to: {output_path}")
            
            logger.info(f"✅ Successfully parsed document")
            logger.info(f"   - Requirements found: {len(result['requirements'])}")
            logger.info(f"   - Compliance mappings: {len(result['compliance_mappings'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parsing document: {e}")
            raise
    
    def generate_test_cases(self, requirements: List[dict], 
                          compliance_mappings: List[dict] = None,
                          output_path: Optional[str] = None) -> List[dict]:
        """Generate test cases from requirements."""
        logger.info("Generating test cases...")
        
        try:
            generator = TestCaseGenerator(
                api_key=self.config.GOOGLE_AI_API_KEY,
                project_id=self.config.GOOGLE_CLOUD_PROJECT_ID
            )
            
            test_cases = generator.generate_test_cases(requirements, compliance_mappings)
            
            if output_path:
                # Convert test cases to serializable format
                test_cases_data = []
                for tc in test_cases:
                    tc_dict = {
                        'id': tc.id,
                        'title': tc.title,
                        'description': tc.description,
                        'test_case_type': tc.test_case_type.value,
                        'priority': tc.priority.value,
                        'requirement_id': tc.requirement_id,
                        'compliance_refs': tc.compliance_refs,
                        'test_steps': [
                            {
                                'step_number': step.step_number,
                                'action': step.action,
                                'expected_result': step.expected_result,
                                'data_inputs': step.data_inputs,
                                'preconditions': step.preconditions,
                                'postconditions': step.postconditions
                            }
                            for step in tc.test_steps
                        ],
                        'prerequisites': tc.prerequisites,
                        'expected_outcome': tc.expected_outcome,
                        'pass_criteria': tc.pass_criteria,
                        'fail_criteria': tc.fail_criteria,
                        'estimated_duration': tc.estimated_duration,
                        'created_date': tc.created_date,
                        'last_modified': tc.last_modified
                    }
                    test_cases_data.append(tc_dict)
                
                with open(output_path, 'w') as f:
                    json.dump(test_cases_data, f, indent=2, default=str)
                logger.info(f"Test cases saved to: {output_path}")
            
            logger.info(f"✅ Successfully generated {len(test_cases)} test cases")
            
            # Show summary
            test_case_types = {}
            test_case_priorities = {}
            
            for tc in test_cases:
                tc_type = tc.test_case_type.value
                tc_priority = tc.priority.value
                
                test_case_types[tc_type] = test_case_types.get(tc_type, 0) + 1
                test_case_priorities[tc_priority] = test_case_priorities.get(tc_priority, 0) + 1
            
            logger.info(f"   - By type: {test_case_types}")
            logger.info(f"   - By priority: {test_case_priorities}")
            
            return test_cases
            
        except Exception as e:
            logger.error(f"❌ Error generating test cases: {e}")
            raise
    
    def validate_compliance(self, test_cases: List[dict]) -> List[dict]:
        """Validate test cases for compliance."""
        logger.info("Validating compliance...")
        
        try:
            validator = ComplianceValidator()
            validation_reports = []
            
            for tc_data in test_cases:
                # Convert dict back to TestCase object for validation
                from test_case_generation.test_case_generator import TestCase, TestStep, TestCaseType, TestCasePriority
                
                test_steps = [
                    TestStep(
                        step_number=step['step_number'],
                        action=step['action'],
                        expected_result=step['expected_result'],
                        data_inputs=step.get('data_inputs'),
                        preconditions=step.get('preconditions'),
                        postconditions=step.get('postconditions')
                    )
                    for step in tc_data['test_steps']
                ]
                
                tc = TestCase(
                    id=tc_data['id'],
                    title=tc_data['title'],
                    description=tc_data['description'],
                    test_case_type=TestCaseType(tc_data['test_case_type']),
                    priority=TestCasePriority(tc_data['priority']),
                    requirement_id=tc_data['requirement_id'],
                    compliance_refs=tc_data['compliance_refs'],
                    test_steps=test_steps,
                    prerequisites=tc_data['prerequisites'],
                    expected_outcome=tc_data['expected_outcome'],
                    pass_criteria=tc_data['pass_criteria'],
                    fail_criteria=tc_data['fail_criteria'],
                    estimated_duration=tc_data.get('estimated_duration'),
                    created_date=tc_data.get('created_date', ''),
                    last_modified=tc_data.get('last_modified', '')
                )
                
                report = validator.validate_test_case(tc, tc.compliance_refs)
                validation_reports.append({
                    'test_case_id': report.test_case_id,
                    'overall_compliance': report.overall_compliance.value,
                    'compliance_score': report.compliance_score,
                    'checks_count': len(report.checks),
                    'recommendations_count': len(report.recommendations),
                    'evidence_gaps_count': len(report.evidence_gaps)
                })
            
            # Calculate summary statistics
            avg_score = sum(r['compliance_score'] for r in validation_reports) / len(validation_reports)
            compliance_levels = {}
            for report in validation_reports:
                level = report['overall_compliance']
                compliance_levels[level] = compliance_levels.get(level, 0) + 1
            
            logger.info(f"✅ Compliance validation completed")
            logger.info(f"   - Average compliance score: {avg_score:.1f}%")
            logger.info(f"   - Compliance levels: {compliance_levels}")
            
            return validation_reports
            
        except Exception as e:
            logger.error(f"❌ Error validating compliance: {e}")
            raise
    
    def export_results(self, test_cases: List[dict], 
                      format_type: str, 
                      output_path: str,
                      **kwargs) -> bool:
        """Export test cases to specified format."""
        logger.info(f"Exporting test cases to {format_type.upper()}...")
        
        try:
            export_manager = ExportManager()
            
            # Convert dict format back to TestCase objects
            from test_case_generation.test_case_generator import TestCase, TestStep, TestCaseType, TestCasePriority
            
            tc_objects = []
            for tc_data in test_cases:
                test_steps = [
                    TestStep(
                        step_number=step['step_number'],
                        action=step['action'],
                        expected_result=step['expected_result'],
                        data_inputs=step.get('data_inputs'),
                        preconditions=step.get('preconditions'),
                        postconditions=step.get('postconditions')
                    )
                    for step in tc_data['test_steps']
                ]
                
                tc = TestCase(
                    id=tc_data['id'],
                    title=tc_data['title'],
                    description=tc_data['description'],
                    test_case_type=TestCaseType(tc_data['test_case_type']),
                    priority=TestCasePriority(tc_data['priority']),
                    requirement_id=tc_data['requirement_id'],
                    compliance_refs=tc_data['compliance_refs'],
                    test_steps=test_steps,
                    prerequisites=tc_data['prerequisites'],
                    expected_outcome=tc_data['expected_outcome'],
                    pass_criteria=tc_data['pass_criteria'],
                    fail_criteria=tc_data['fail_criteria'],
                    estimated_duration=tc_data.get('estimated_duration'),
                    created_date=tc_data.get('created_date', ''),
                    last_modified=tc_data.get('last_modified', '')
                )
                tc_objects.append(tc)
            
            success = export_manager.export_test_cases(
                tc_objects, 
                output_path, 
                format_type, 
                **kwargs
            )
            
            if success:
                logger.info(f"✅ Successfully exported to: {output_path}")
            else:
                logger.error(f"❌ Failed to export to: {output_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error exporting results: {e}")
            raise
    
    def generate_traceability_matrix(self, requirements: List[dict], 
                                   test_cases: List[dict],
                                   compliance_mappings: List[dict] = None,
                                   output_path: Optional[str] = None) -> dict:
        """Generate traceability matrix."""
        logger.info("Generating traceability matrix...")
        
        try:
            matrix_generator = TraceabilityMatrixGenerator()
            
            matrix_data = matrix_generator.generate_traceability_matrix(
                requirements,
                test_cases,
                compliance_mappings
            )
            
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(matrix_data, f, indent=2, default=str)
                logger.info(f"Traceability matrix saved to: {output_path}")
            
            # Show summary
            coverage_summary = matrix_data['matrix_views']['coverage_summary']
            logger.info(f"✅ Traceability matrix generated")
            logger.info(f"   - Requirements: {coverage_summary['total_requirements']}")
            logger.info(f"   - Test cases: {coverage_summary['total_test_cases']}")
            logger.info(f"   - Coverage: {coverage_summary['coverage_percentage']}%")
            logger.info(f"   - Traceability items: {len(matrix_data['traceability_items'])}")
            
            return matrix_data
            
        except Exception as e:
            logger.error(f"❌ Error generating traceability matrix: {e}")
            raise
    
    def run_complete_workflow(self, document_path: str, 
                            output_dir: str = "output",
                            export_formats: List[str] = None) -> dict:
        """Run the complete workflow from document parsing to export."""
        logger.info("🚀 Starting complete workflow...")
        start_time = time.time()
        
        if export_formats is None:
            export_formats = ['json', 'excel']
        
        try:
            # Step 1: Parse document
            logger.info("Step 1: Parsing document...")
            parsed_result = self.parse_document(document_path)
            
            # Step 2: Generate test cases
            logger.info("Step 2: Generating test cases...")
            test_cases = self.generate_test_cases(
                parsed_result['requirements'],
                parsed_result['compliance_mappings']
            )
            
            # Step 3: Validate compliance
            logger.info("Step 3: Validating compliance...")
            validation_reports = self.validate_compliance(test_cases)
            
            # Step 4: Generate traceability matrix
            logger.info("Step 4: Generating traceability matrix...")
            matrix_data = self.generate_traceability_matrix(
                parsed_result['requirements'],
                test_cases,
                parsed_result['compliance_mappings']
            )
            
            # Step 5: Export results
            logger.info("Step 5: Exporting results...")
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            export_results = {}
            for format_type in export_formats:
                file_path = output_path / f"test_cases.{format_type}"
                success = self.export_results(test_cases, format_type, str(file_path))
                export_results[format_type] = success
            
            # Export traceability matrix
            matrix_path = output_path / "traceability_matrix.xlsx"
            matrix_generator = TraceabilityMatrixGenerator()
            matrix_success = matrix_generator.export_traceability_matrix(
                matrix_data, str(matrix_path), 'excel'
            )
            export_results['traceability_matrix'] = matrix_success
            
            # Generate summary report
            end_time = time.time()
            duration = end_time - start_time
            
            summary = {
                'workflow_completed': True,
                'duration_seconds': duration,
                'document_parsed': True,
                'requirements_found': len(parsed_result['requirements']),
                'test_cases_generated': len(test_cases),
                'compliance_validated': len(validation_reports),
                'export_results': export_results,
                'output_directory': str(output_path.absolute()),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save summary report
            summary_path = output_path / "workflow_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"🎉 Complete workflow finished successfully!")
            logger.info(f"   - Duration: {duration:.2f} seconds")
            logger.info(f"   - Output directory: {output_path.absolute()}")
            logger.info(f"   - Files generated: {len([r for r in export_results.values() if r])}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            raise


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Healthcare AI Test Case Generator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a document
  python cli.py parse requirements.pdf --output parsed_data.json
  
  # Generate test cases
  python cli.py generate requirements.json --output test_cases.json
  
  # Run complete workflow
  python cli.py workflow requirements.pdf --output-dir results --formats json excel
  
  # Export test cases
  python cli.py export test_cases.json --format excel --output test_cases.xlsx
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse healthcare document')
    parse_parser.add_argument('document', help='Path to healthcare document')
    parse_parser.add_argument('--output', '-o', help='Output file path')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate test cases')
    generate_parser.add_argument('requirements', help='Path to requirements JSON file')
    generate_parser.add_argument('--output', '-o', help='Output file path')
    generate_parser.add_argument('--compliance', help='Path to compliance mappings JSON file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate compliance')
    validate_parser.add_argument('test_cases', help='Path to test cases JSON file')
    validate_parser.add_argument('--output', '-o', help='Output file path')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export test cases')
    export_parser.add_argument('test_cases', help='Path to test cases JSON file')
    export_parser.add_argument('--format', '-f', choices=['json', 'excel', 'csv', 'jira', 'azure_devops'],
                              default='excel', help='Export format')
    export_parser.add_argument('--output', '-o', required=True, help='Output file path')
    export_parser.add_argument('--project-key', help='Jira project key')
    export_parser.add_argument('--issue-type', help='Jira issue type')
    
    # Traceability command
    trace_parser = subparsers.add_parser('traceability', help='Generate traceability matrix')
    trace_parser.add_argument('requirements', help='Path to requirements JSON file')
    trace_parser.add_argument('test_cases', help='Path to test cases JSON file')
    trace_parser.add_argument('--output', '-o', help='Output file path')
    trace_parser.add_argument('--compliance', help='Path to compliance mappings JSON file')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('document', help='Path to healthcare document')
    workflow_parser.add_argument('--output-dir', '-d', default='output', help='Output directory')
    workflow_parser.add_argument('--formats', nargs='+', choices=['json', 'excel', 'csv', 'jira', 'azure_devops'],
                                default=['json', 'excel'], help='Export formats')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = HealthcareAICLI()
    
    try:
        if args.command == 'parse':
            cli.parse_document(args.document, args.output)
            
        elif args.command == 'generate':
            with open(args.requirements, 'r') as f:
                requirements = json.load(f)
            
            compliance_mappings = None
            if args.compliance:
                with open(args.compliance, 'r') as f:
                    compliance_mappings = json.load(f)
            
            cli.generate_test_cases(requirements, compliance_mappings, args.output)
            
        elif args.command == 'validate':
            with open(args.test_cases, 'r') as f:
                test_cases = json.load(f)
            
            validation_reports = cli.validate_compliance(test_cases)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(validation_reports, f, indent=2, default=str)
                logger.info(f"Validation reports saved to: {args.output}")
            
        elif args.command == 'export':
            with open(args.test_cases, 'r') as f:
                test_cases = json.load(f)
            
            export_kwargs = {}
            if args.project_key:
                export_kwargs['project_key'] = args.project_key
            if args.issue_type:
                export_kwargs['issue_type'] = args.issue_type
            
            cli.export_results(test_cases, args.format, args.output, **export_kwargs)
            
        elif args.command == 'traceability':
            with open(args.requirements, 'r') as f:
                requirements = json.load(f)
            with open(args.test_cases, 'r') as f:
                test_cases = json.load(f)
            
            compliance_mappings = None
            if args.compliance:
                with open(args.compliance, 'r') as f:
                    compliance_mappings = json.load(f)
            
            cli.generate_traceability_matrix(requirements, test_cases, compliance_mappings, args.output)
            
        elif args.command == 'workflow':
            cli.run_complete_workflow(args.document, args.output_dir, args.formats)
            
        elif args.command == 'config':
            if args.validate:
                issues = cli.config.validate_config()
                if issues:
                    logger.error("Configuration issues found:")
                    for issue in issues:
                        logger.error(f"  - {issue}")
                else:
                    logger.info("✅ Configuration is valid")
                    
            if args.show:
                logger.info("Current configuration:")
                logger.info(f"  - Environment: {cli.config.ENVIRONMENT}")
                logger.info(f"  - Log Level: {cli.config.LOG_LEVEL}")
                logger.info(f"  - Default Export Format: {cli.config.DEFAULT_EXPORT_FORMAT}")
                logger.info(f"  - Google AI API Key: {'Set' if cli.config.GOOGLE_AI_API_KEY else 'Not set'}")
                logger.info(f"  - Google Cloud Project: {'Set' if cli.config.GOOGLE_CLOUD_PROJECT_ID else 'Not set'}")
                
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

