# Deployment Guide

This guide provides instructions for deploying the Healthcare AI Test Case Generator in various environments.

## Prerequisites

### System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB disk space
- Internet connection for AI API access

### Dependencies

- Google Cloud Platform account (for Vertex AI)
- Google AI API key (alternative to GCP)
- Required Python packages (see requirements.txt)

## Installation Methods

### 1. Local Development Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/healthcare-ai-testcase-generator.git
cd healthcare-ai-testcase-generator
```

#### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Step 5: Run Setup Script
```bash
python scripts/setup_environment.py
```

### 2. Docker Deployment

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "examples/basic_usage.py"]
```

#### Step 2: Build Docker Image
```bash
docker build -t healthcare-ai-testcase-generator .
```

#### Step 3: Run Container
```bash
docker run -e GOOGLE_AI_API_KEY=your-api-key healthcare-ai-testcase-generator
```

### 3. Cloud Deployment

#### Google Cloud Platform

##### Step 1: Set Up GCP Project
```bash
gcloud projects create your-project-id
gcloud config set project your-project-id
```

##### Step 2: Enable APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com
```

##### Step 3: Create Service Account
```bash
gcloud iam service-accounts create healthcare-ai-sa
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:healthcare-ai-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

##### Step 4: Deploy to Cloud Run
```bash
gcloud run deploy healthcare-ai-testcase-generator \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

#### AWS Deployment

##### Step 1: Create ECS Task Definition
```json
{
  "family": "healthcare-ai-testcase-generator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "healthcare-ai-testcase-generator",
      "image": "your-account.dkr.ecr.region.amazonaws.com/healthcare-ai-testcase-generator",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GOOGLE_AI_API_KEY",
          "value": "your-api-key"
        }
      ]
    }
  ]
}
```

##### Step 2: Deploy to ECS
```bash
aws ecs create-cluster --cluster-name healthcare-ai-cluster
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster healthcare-ai-cluster --service-name healthcare-ai-service --task-definition healthcare-ai-testcase-generator
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_AI_API_KEY` | Google AI API key | Yes* | - |
| `GOOGLE_CLOUD_PROJECT_ID` | GCP project ID | Yes* | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | Yes* | - |
| `DEFAULT_EXPORT_FORMAT` | Default export format | No | excel |
| `LOG_LEVEL` | Logging level | No | INFO |
| `MAX_DOCUMENT_SIZE` | Max document size (MB) | No | 50 |

*At least one of the Google AI configuration options is required.

### Configuration File

Create a `config.py` file or use environment variables:

```python
import os

# Google AI Configuration
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')

# Export Configuration
DEFAULT_EXPORT_FORMAT = 'excel'
DEFAULT_OUTPUT_DIR = 'output'

# Logging Configuration
LOG_LEVEL = 'INFO'
```

## Security Considerations

### API Key Management

1. **Never commit API keys to version control**
2. **Use environment variables or secure key management**
3. **Rotate keys regularly**
4. **Use least privilege access**

### Data Protection

1. **Process documents locally when possible**
2. **Encrypt sensitive data in transit and at rest**
3. **Implement proper access controls**
4. **Maintain audit logs**

### Compliance

1. **Ensure HIPAA compliance for healthcare data**
2. **Implement GDPR compliance for EU data**
3. **Follow FDA guidelines for medical device software**
4. **Maintain audit trails**

## Monitoring and Logging

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/healthcare_ai_generator.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

Create a health check endpoint:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })
```

### Metrics Collection

```python
import time
from functools import wraps

def track_metrics(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Log metrics
        logger.info(f"Function {func.__name__} took {duration:.2f} seconds")
        return result
    return wrapper
```

## Troubleshooting

### Common Issues

#### 1. API Key Issues
```
Error: Google AI API key not found
Solution: Set GOOGLE_AI_API_KEY environment variable
```

#### 2. Import Errors
```
Error: No module named 'google.generativeai'
Solution: Install requirements: pip install -r requirements.txt
```

#### 3. Document Parsing Errors
```
Error: Unsupported file format
Solution: Ensure document is in supported format (PDF, DOCX, XML, HTML)
```

#### 4. Memory Issues
```
Error: Out of memory
Solution: Increase container memory or process smaller documents
```

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. **Use smaller document chunks for large files**
2. **Implement caching for repeated operations**
3. **Use batch processing for multiple documents**
4. **Optimize AI model parameters**

## Scaling

### Horizontal Scaling

1. **Use load balancers for multiple instances**
2. **Implement stateless design**
3. **Use message queues for async processing**
4. **Implement auto-scaling policies**

### Vertical Scaling

1. **Increase memory for large documents**
2. **Use faster CPUs for AI processing**
3. **Implement GPU acceleration for AI models**
4. **Optimize database performance**

## Backup and Recovery

### Data Backup

1. **Backup configuration files**
2. **Backup generated test cases**
3. **Backup traceability matrices**
4. **Implement automated backups**

### Disaster Recovery

1. **Create disaster recovery plan**
2. **Test recovery procedures**
3. **Maintain backup documentation**
4. **Implement monitoring and alerting**

## Maintenance

### Regular Tasks

1. **Update dependencies monthly**
2. **Review and rotate API keys**
3. **Monitor system performance**
4. **Update documentation**

### Version Updates

1. **Test updates in staging environment**
2. **Create rollback procedures**
3. **Update configuration as needed**
4. **Communicate changes to users**

This deployment guide provides comprehensive instructions for deploying the Healthcare AI Test Case Generator in various environments while maintaining security, compliance, and performance standards.
