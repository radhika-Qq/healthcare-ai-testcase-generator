#!/usr/bin/env python3
"""
Deployment script for Healthcare AI Test Case Generator Prototype
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages for Streamlit app."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def run_streamlit():
    """Run the Streamlit app locally."""
    print("🚀 Starting Streamlit app...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped.")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def main():
    """Main deployment function."""
    print("🏥 Healthcare AI Test Case Generator - Prototype Deployment")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found. Please run from the project root directory.")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    print("\n🎯 Prototype Features:")
    print("1. 📄 Document Parsing - Upload and parse healthcare requirements")
    print("2. 🧪 Test Generation - AI-powered test case generation")
    print("3. 📊 Export & Traceability - Export results and generate traceability matrix")
    
    print("\n🌐 Access your prototype at: http://localhost:8501")
    print("📝 Note: Configure your API key in the sidebar for full functionality")
    
    # Run Streamlit
    run_streamlit()

if __name__ == "__main__":
    main()
