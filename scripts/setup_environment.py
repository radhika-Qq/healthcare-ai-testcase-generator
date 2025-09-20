"""
Environment Setup Script for Healthcare AI Test Case Generator

This script helps set up the development environment and install dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def main():
    """Main setup function."""
    print("Healthcare AI Test Case Generator - Environment Setup")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create necessary directories
    create_directories()
    
    # Set up environment variables
    setup_environment_variables()
    
    print("\n" + "=" * 60)
    print("✓ Environment setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Set up Google Cloud credentials (optional for AI features)")
    print("3. Run the basic usage example:")
    print("   python examples/basic_usage.py")


def check_python_version():
    """Check if Python version is compatible."""
    print("\n1. Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")


def create_virtual_environment():
    """Create virtual environment."""
    print("\n2. Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return
        
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create virtual environment: {e}")
        sys.exit(1)


def install_dependencies():
    """Install Python dependencies."""
    print("\n3. Installing dependencies...")
    
    # Determine pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        print("✓ Upgraded pip")
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✓ Installed all dependencies")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print("  You may need to install dependencies manually:")
        print(f"  {pip_cmd} install -r requirements.txt")
        sys.exit(1)


def create_directories():
    """Create necessary directories."""
    print("\n4. Creating directories...")
    
    directories = [
        "examples/output",
        "temp",
        "logs",
        "docs/examples",
        "tests/unit",
        "tests/integration"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def setup_environment_variables():
    """Set up environment variables."""
    print("\n5. Setting up environment variables...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file already exists")
        return
        
    env_content = """# Healthcare AI Test Case Generator Environment Variables

# Google Cloud Configuration (optional for AI features)
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Google AI API Key (alternative to service account)
GOOGLE_AI_API_KEY=your-api-key

# Export Configuration
DEFAULT_EXPORT_FORMAT=excel
DEFAULT_OUTPUT_DIR=output

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/healthcare_ai_generator.log

# Test Configuration
TEST_DATA_DIR=test_data
TEST_OUTPUT_DIR=test_output
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
        
    print("✓ Created .env file with default configuration")
    print("  Edit .env file to configure your specific settings")


if __name__ == "__main__":
    main()

