#!/usr/bin/env python3
"""
Cloud Deployment Script for Healthcare AI Test Case Generator

This script automates the deployment of the Healthcare AI Test Case Generator
to various cloud platforms including Google Cloud Platform and AWS.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CloudDeployer:
    """Handles cloud deployment for the Healthcare AI Test Case Generator."""
    
    def __init__(self, config_path: str = "deployment_config.yaml"):
        """Initialize the cloud deployer with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.project_root = Path(__file__).parent.parent
        
    def _load_config(self) -> Dict[str, Any]:
        """Load deployment configuration."""
        if not self.config_path.exists():
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return self._get_default_config()
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default deployment configuration."""
        return {
            'project_name': 'healthcare-ai-testcase-generator',
            'version': '1.0.0',
            'cloud_provider': 'gcp',
            'gcp': {
                'project_id': os.getenv('GOOGLE_CLOUD_PROJECT_ID', ''),
                'region': 'us-central1',
                'service_name': 'healthcare-ai-generator',
                'min_instances': 1,
                'max_instances': 10,
                'cpu': '1',
                'memory': '2Gi'
            },
            'aws': {
                'region': 'us-east-1',
                'cluster_name': 'healthcare-ai-cluster',
                'service_name': 'healthcare-ai-generator',
                'task_cpu': '1024',
                'task_memory': '2048'
            },
            'environment': {
                'GOOGLE_AI_API_KEY': os.getenv('GOOGLE_AI_API_KEY', ''),
                'GOOGLE_CLOUD_PROJECT_ID': os.getenv('GOOGLE_CLOUD_PROJECT_ID', ''),
                'LOG_LEVEL': 'INFO'
            }
        }
    
    def deploy_gcp(self) -> bool:
        """Deploy to Google Cloud Platform."""
        logger.info("🚀 Deploying to Google Cloud Platform...")
        
        try:
            # Check if gcloud is installed
            self._check_gcloud_installed()
            
            # Set project
            project_id = self.config['gcp']['project_id']
            if not project_id:
                logger.error("Google Cloud Project ID not configured")
                return False
                
            subprocess.run(['gcloud', 'config', 'set', 'project', project_id], check=True)
            
            # Enable required APIs
            self._enable_gcp_apis()
            
            # Build and push Docker image
            self._build_and_push_docker_image()
            
            # Deploy to Cloud Run
            self._deploy_to_cloud_run()
            
            logger.info("✅ Successfully deployed to Google Cloud Platform")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ GCP deployment failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during GCP deployment: {e}")
            return False
    
    def deploy_aws(self) -> bool:
        """Deploy to AWS."""
        logger.info("🚀 Deploying to AWS...")
        
        try:
            # Check if AWS CLI is installed
            self._check_aws_cli_installed()
            
            # Create ECR repository
            self._create_ecr_repository()
            
            # Build and push Docker image
            self._build_and_push_docker_image_aws()
            
            # Deploy to ECS
            self._deploy_to_ecs()
            
            logger.info("✅ Successfully deployed to AWS")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ AWS deployment failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during AWS deployment: {e}")
            return False
    
    def _check_gcloud_installed(self):
        """Check if gcloud CLI is installed."""
        try:
            subprocess.run(['gcloud', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("gcloud CLI not found. Please install Google Cloud SDK.")
    
    def _check_aws_cli_installed(self):
        """Check if AWS CLI is installed."""
        try:
            subprocess.run(['aws', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("AWS CLI not found. Please install AWS CLI.")
    
    def _enable_gcp_apis(self):
        """Enable required GCP APIs."""
        apis = [
            'run.googleapis.com',
            'cloudbuild.googleapis.com',
            'containerregistry.googleapis.com',
            'aiplatform.googleapis.com'
        ]
        
        for api in apis:
            logger.info(f"Enabling API: {api}")
            subprocess.run(['gcloud', 'services', 'enable', api], check=True)
    
    def _build_and_push_docker_image(self):
        """Build and push Docker image to GCP."""
        project_id = self.config['gcp']['project_id']
        service_name = self.config['gcp']['service_name']
        version = self.config['version']
        
        image_name = f"gcr.io/{project_id}/{service_name}:{version}"
        
        # Build Docker image
        logger.info(f"Building Docker image: {image_name}")
        subprocess.run([
            'docker', 'build', '-t', image_name, '.'
        ], cwd=self.project_root, check=True)
        
        # Push to GCR
        logger.info(f"Pushing image to GCR: {image_name}")
        subprocess.run(['docker', 'push', image_name], check=True)
    
    def _deploy_to_cloud_run(self):
        """Deploy to Google Cloud Run."""
        project_id = self.config['gcp']['project_id']
        service_name = self.config['gcp']['service_name']
        version = self.config['version']
        region = self.config['gcp']['region']
        
        image_name = f"gcr.io/{project_id}/{service_name}:{version}"
        
        # Prepare environment variables
        env_vars = []
        for key, value in self.config['environment'].items():
            if value:
                env_vars.append(f"{key}={value}")
        
        # Deploy to Cloud Run
        cmd = [
            'gcloud', 'run', 'deploy', service_name,
            '--image', image_name,
            '--platform', 'managed',
            '--region', region,
            '--allow-unauthenticated',
            '--min-instances', str(self.config['gcp']['min_instances']),
            '--max-instances', str(self.config['gcp']['max_instances']),
            '--cpu', self.config['gcp']['cpu'],
            '--memory', self.config['gcp']['memory']
        ]
        
        if env_vars:
            cmd.extend(['--set-env-vars', ','.join(env_vars)])
        
        logger.info(f"Deploying to Cloud Run: {service_name}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Extract service URL
        for line in result.stdout.split('\n'):
            if 'Service URL:' in line:
                service_url = line.split('Service URL:')[1].strip()
                logger.info(f"Service deployed at: {service_url}")
                break
    
    def _create_ecr_repository(self):
        """Create ECR repository if it doesn't exist."""
        region = self.config['aws']['region']
        project_name = self.config['project_name']
        
        try:
            subprocess.run([
                'aws', 'ecr', 'create-repository',
                '--repository-name', project_name,
                '--region', region
            ], check=True, capture_output=True)
            logger.info(f"Created ECR repository: {project_name}")
        except subprocess.CalledProcessError as e:
            if "RepositoryAlreadyExistsException" in str(e.stderr):
                logger.info(f"ECR repository {project_name} already exists")
            else:
                raise
    
    def _build_and_push_docker_image_aws(self):
        """Build and push Docker image to AWS ECR."""
        region = self.config['aws']['region']
        project_name = self.config['project_name']
        version = self.config['version']
        
        # Get ECR login token
        login_cmd = subprocess.run([
            'aws', 'ecr', 'get-login-password', '--region', region
        ], check=True, capture_output=True, text=True)
        
        # Login to ECR
        subprocess.run([
            'docker', 'login', '--username', 'AWS', '--password-stdin',
            f"{self._get_ecr_registry(region)}"
        ], input=login_cmd.stdout, text=True, check=True)
        
        # Build and tag image
        image_name = f"{self._get_ecr_registry(region)}/{project_name}:{version}"
        
        logger.info(f"Building Docker image: {image_name}")
        subprocess.run([
            'docker', 'build', '-t', image_name, '.'
        ], cwd=self.project_root, check=True)
        
        # Push to ECR
        logger.info(f"Pushing image to ECR: {image_name}")
        subprocess.run(['docker', 'push', image_name], check=True)
    
    def _get_ecr_registry(self, region: str) -> str:
        """Get ECR registry URL for region."""
        account_id = subprocess.run([
            'aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'
        ], check=True, capture_output=True, text=True).stdout.strip()
        
        return f"{account_id}.dkr.ecr.{region}.amazonaws.com"
    
    def _deploy_to_ecs(self):
        """Deploy to AWS ECS."""
        region = self.config['aws']['region']
        cluster_name = self.config['aws']['cluster_name']
        service_name = self.config['aws']['service_name']
        project_name = self.config['project_name']
        version = self.config['version']
        
        # Create task definition
        task_def = self._create_ecs_task_definition()
        
        # Register task definition
        task_def_file = self.project_root / "task-definition.json"
        with open(task_def_file, 'w') as f:
            json.dump(task_def, f, indent=2)
        
        subprocess.run([
            'aws', 'ecs', 'register-task-definition',
            '--cli-input-json', f"file://{task_def_file}",
            '--region', region
        ], check=True)
        
        # Create or update service
        try:
            subprocess.run([
                'aws', 'ecs', 'create-service',
                '--cluster', cluster_name,
                '--service-name', service_name,
                '--task-definition', f"{project_name}:{version}",
                '--desired-count', '1',
                '--region', region
            ], check=True)
            logger.info(f"Created ECS service: {service_name}")
        except subprocess.CalledProcessError as e:
            if "ServiceAlreadyExists" in str(e.stderr):
                # Update existing service
                subprocess.run([
                    'aws', 'ecs', 'update-service',
                    '--cluster', cluster_name,
                    '--service', service_name,
                    '--task-definition', f"{project_name}:{version}",
                    '--region', region
                ], check=True)
                logger.info(f"Updated ECS service: {service_name}")
            else:
                raise
    
    def _create_ecs_task_definition(self) -> Dict[str, Any]:
        """Create ECS task definition."""
        region = self.config['aws']['region']
        project_name = self.config['project_name']
        version = self.config['version']
        
        return {
            "family": project_name,
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": self.config['aws']['task_cpu'],
            "memory": self.config['aws']['task_memory'],
            "executionRoleArn": f"arn:aws:iam::{self._get_account_id()}:role/ecsTaskExecutionRole",
            "containerDefinitions": [
                {
                    "name": project_name,
                    "image": f"{self._get_ecr_registry(region)}/{project_name}:{version}",
                    "portMappings": [
                        {
                            "containerPort": 8080,
                            "protocol": "tcp"
                        }
                    ],
                    "environment": [
                        {"name": key, "value": value}
                        for key, value in self.config['environment'].items()
                        if value
                    ],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/{project_name}",
                            "awslogs-region": region,
                            "awslogs-stream-prefix": "ecs"
                        }
                    }
                }
            ]
        }
    
    def _get_account_id(self) -> str:
        """Get AWS account ID."""
        return subprocess.run([
            'aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'
        ], check=True, capture_output=True, text=True).stdout.strip()
    
    def create_dockerfile(self):
        """Create Dockerfile for deployment."""
        dockerfile_content = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
"""
        
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        logger.info(f"Created Dockerfile: {dockerfile_path}")
    
    def create_deployment_config(self):
        """Create deployment configuration file."""
        config = self._get_default_config()
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created deployment config: {self.config_path}")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy Healthcare AI Test Case Generator to cloud')
    parser.add_argument('--provider', choices=['gcp', 'aws'], required=True,
                       help='Cloud provider to deploy to')
    parser.add_argument('--config', default='deployment_config.yaml',
                       help='Deployment configuration file')
    parser.add_argument('--create-config', action='store_true',
                       help='Create default configuration file')
    parser.add_argument('--create-dockerfile', action='store_true',
                       help='Create Dockerfile for deployment')
    
    args = parser.parse_args()
    
    deployer = CloudDeployer(args.config)
    
    if args.create_config:
        deployer.create_deployment_config()
        return
    
    if args.create_dockerfile:
        deployer.create_dockerfile()
        return
    
    # Deploy to selected provider
    if args.provider == 'gcp':
        success = deployer.deploy_gcp()
    elif args.provider == 'aws':
        success = deployer.deploy_aws()
    else:
        logger.error(f"Unsupported cloud provider: {args.provider}")
        return
    
    if success:
        logger.info("🎉 Deployment completed successfully!")
    else:
        logger.error("❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

