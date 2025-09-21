# 🚀 Healthcare AI Test Case Generator - Prototype Deployment Guide

## Overview

This guide will help you deploy and share your Healthcare AI Test Case Generator prototype. The prototype showcases 3 core features in a user-friendly web interface.

## 🎯 Prototype Features

### 1. 📄 Document Parsing
- Upload healthcare requirements documents (PDF, Word, XML, HTML, TXT)
- AI-powered requirement extraction
- Compliance mapping to regulatory standards
- Real-time parsing results

### 2. 🧪 Test Case Generation
- AI-powered test case creation
- Multiple test types (positive, negative, compliance, security)
- Step-by-step test case details
- Priority assignment

### 3. 📊 Export & Traceability
- Multiple export formats (Excel, JSON, CSV)
- Complete traceability matrix generation
- Coverage analysis
- Download functionality

## 🚀 Quick Start (Local Deployment)

### Option 1: Automated Setup
```bash
# Run the deployment script
python deploy_prototype.py
```

### Option 2: Manual Setup
```bash
# 1. Install requirements
pip install -r requirements_streamlit.txt

# 2. Run Streamlit app
streamlit run streamlit_app.py
```

### 3. Access the App
- Open your browser to: `http://localhost:8501`
- The app will be running locally on your machine

## ☁️ Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Prepare your repository:**
   ```bash
   # Ensure your code is on GitHub
   git add .
   git commit -m "Add Streamlit prototype"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Configure environment variables:**
   - In Streamlit Cloud dashboard
   - Go to Settings → Secrets
   - Add your API keys:
   ```toml
   [secrets]
   GOOGLE_AI_API_KEY = "your-api-key-here"
   OPENAI_API_KEY = "your-openai-key-here"
   ```

### Option 2: Heroku

1. **Create Heroku app:**
   ```bash
   # Install Heroku CLI
   # Create Procfile
   echo "web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   
   # Deploy
   heroku create your-app-name
   git push heroku main
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set GOOGLE_AI_API_KEY=your-api-key
   heroku config:set OPENAI_API_KEY=your-openai-key
   ```

### Option 3: Railway

1. **Connect GitHub repository:**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the repository

2. **Configure deployment:**
   - Set start command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - Add environment variables in Railway dashboard

### Option 4: Render

1. **Create Web Service:**
   - Go to [render.com](https://render.com)
   - Connect GitHub repository
   - Choose "Web Service"

2. **Configure:**
   - Build Command: `pip install -r requirements_streamlit.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

## 📱 Demo Video Alternative

If you prefer not to deploy, create a demo video:

### Tools for Recording:
- **Loom** (Recommended): [loom.com](https://loom.com)
- **OBS Studio**: Free screen recording
- **QuickTime** (Mac): Built-in screen recording
- **Windows Game Bar** (Windows): Built-in screen recording

### Demo Script:
1. **Introduction** (30 seconds)
   - "This is the Healthcare AI Test Case Generator prototype"
   - "It helps healthcare software teams generate compliant test cases"

2. **Feature 1 - Document Parsing** (1 minute)
   - Upload a sample document
   - Show requirement extraction
   - Highlight compliance mapping

3. **Feature 2 - Test Generation** (1 minute)
   - Generate test cases
   - Show different test types
   - Display detailed test steps

4. **Feature 3 - Export & Traceability** (1 minute)
   - Export to Excel
   - Generate traceability matrix
   - Show coverage analysis

5. **Conclusion** (30 seconds)
   - "This prototype demonstrates the core value proposition"
   - "Ready for production deployment and scaling"

## 🔧 Configuration

### API Keys Setup
The app supports multiple AI providers:

```python
# In the Streamlit sidebar, enter:
GOOGLE_AI_API_KEY = "your-gemini-api-key"
OPENAI_API_KEY = "your-openai-api-key"
ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

### Environment Variables (for cloud deployment)
```bash
GOOGLE_AI_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## 📊 Performance Optimization

### For Local Development:
- Use sample documents for faster testing
- Limit test case generation to 10-20 cases
- Enable caching for repeated operations

### For Production:
- Implement proper error handling
- Add loading states and progress bars
- Optimize for mobile devices
- Add user authentication

## 🎨 Customization

### Branding:
- Update the logo in the sidebar
- Modify colors in the CSS section
- Add your company branding

### Features:
- Add more export formats
- Implement user authentication
- Add data persistence
- Include more AI providers

## 📈 Analytics & Monitoring

### Add Analytics:
```python
# Add to streamlit_app.py
import streamlit_analytics

# Track page views and interactions
streamlit_analytics.start_tracking()
```

### Monitor Usage:
- Track document uploads
- Monitor test case generation
- Analyze export patterns

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors:**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **API Key Issues:**
   - Check API key format
   - Verify API key permissions
   - Test with sample data first

3. **File Upload Issues:**
   - Check file format support
   - Verify file size limits
   - Test with sample documents

4. **Deployment Issues:**
   - Check port configuration
   - Verify environment variables
   - Review deployment logs

## 📞 Support

### Getting Help:
- Check the GitHub issues
- Review the documentation
- Contact the development team

### Contributing:
- Fork the repository
- Create a feature branch
- Submit a pull request

## 🎯 Next Steps

### Immediate Actions:
1. Deploy to Streamlit Cloud (easiest)
2. Create a demo video (backup option)
3. Share the prototype link

### Future Enhancements:
1. Add user authentication
2. Implement data persistence
3. Add more AI providers
4. Create mobile app version

---

**Ready to deploy? Choose your preferred method and get your prototype live! 🚀**
