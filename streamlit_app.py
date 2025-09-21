#!/usr/bin/env python3
"""
Healthcare AI Test Case Generator - Streamlit Prototype
A simple web interface showcasing the core features of the Healthcare AI Test Case Generator.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import io

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our modules
try:
    from input_parsing import parse_healthcare_document
    from test_case_generation import TestCaseGenerator, ExportManager, TraceabilityMatrixGenerator
    from config import Config
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed: pip install -r requirements.txt")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Healthcare AI Test Case Generator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare AI Test Case Generator</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Test Case Generation for Healthcare Software Compliance")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/2E86AB/FFFFFF?text=Healthcare+AI", width=200)
        st.markdown("### 🚀 Prototype Features")
        st.markdown("""
        **1. Document Parsing** 📄
        - Parse PDF, Word, XML, HTML, TXT
        - Extract requirements automatically
        
        **2. Test Case Generation** 🧪
        - AI-powered test case creation
        - Compliance-aware generation
        
        **3. Export & Traceability** 📊
        - Multiple export formats
        - Complete traceability matrix
        """)
        
        st.markdown("### 🔧 Configuration")
        api_key = st.text_input("Google AI API Key", type="password", help="Enter your Google AI API key")
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ API key required for full functionality")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📄 Document Parser", "🧪 Test Generator", "📊 Export & Traceability"])
    
    with tab1:
        st.markdown("### 📄 Document Parsing & Requirement Extraction")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Upload Healthcare Requirements Document")
            
            # File upload
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['pdf', 'docx', 'doc', 'xml', 'html', 'txt'],
                help="Upload a healthcare requirements document"
            )
            
            if uploaded_file is not None:
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                # Parse button
                if st.button("🔍 Parse Document", type="primary"):
                    with st.spinner("Parsing document and extracting requirements..."):
                        try:
                            # Parse the document
                            result = parse_healthcare_document(temp_path)
                            
                            # Store in session state
                            st.session_state.parsed_data = result
                            st.session_state.requirements = result.get('requirements', [])
                            st.session_state.compliance_mappings = result.get('compliance_mappings', [])
                            
                            st.success("✅ Document parsed successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Error parsing document: {str(e)}")
                            st.info("💡 Try with a different file or check the file format")
                        finally:
                            # Clean up temp file
                            Path(temp_path).unlink(missing_ok=True)
        
        with col2:
            st.markdown("#### 📋 Sample Document")
            st.markdown("""
            **Try with our sample:**
            - Medical Device Requirements
            - Patient Management System
            - Pharmacy Management
            """)
            
            if st.button("📥 Use Sample Document"):
                sample_path = "sample_demo_data/medical_device_requirements.txt"
                if Path(sample_path).exists():
                    with st.spinner("Loading sample document..."):
                        try:
                            result = parse_healthcare_document(sample_path)
                            st.session_state.parsed_data = result
                            st.session_state.requirements = result.get('requirements', [])
                            st.session_state.compliance_mappings = result.get('compliance_mappings', [])
                            st.success("✅ Sample document loaded!")
                        except Exception as e:
                            st.error(f"❌ Error loading sample: {str(e)}")
                else:
                    st.error("❌ Sample document not found")
        
        # Display parsed results
        if 'requirements' in st.session_state and st.session_state.requirements:
            st.markdown("### 📋 Extracted Requirements")
            
            # Summary
            summary = st.session_state.parsed_data.get('summary', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requirements", summary.get('total_requirements', 0))
            with col2:
                st.metric("Functional", summary.get('by_type', {}).get('functional', 0))
            with col3:
                st.metric("Compliance Refs", summary.get('compliance_refs', 0))
            with col4:
                st.metric("High Priority", summary.get('by_priority', {}).get('high', 0))
            
            # Requirements table
            if st.session_state.requirements:
                req_data = []
                for req in st.session_state.requirements[:10]:  # Show first 10
                    req_data.append({
                        'ID': getattr(req, 'id', 'N/A'),
                        'Description': getattr(req, 'description', 'N/A')[:100] + '...',
                        'Type': getattr(req, 'type', 'N/A'),
                        'Priority': getattr(req, 'priority', 'N/A')
                    })
                
                df = pd.DataFrame(req_data)
                st.dataframe(df, use_container_width=True)
                
                if len(st.session_state.requirements) > 10:
                    st.info(f"Showing first 10 of {len(st.session_state.requirements)} requirements")
    
    with tab2:
        st.markdown("### 🧪 AI-Powered Test Case Generation")
        
        if 'requirements' not in st.session_state or not st.session_state.requirements:
            st.warning("⚠️ Please parse a document first in the Document Parser tab")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Generate Test Cases")
                st.info(f"Ready to generate test cases for {len(st.session_state.requirements)} requirements")
                
                # Generation options
                test_types = st.multiselect(
                    "Select Test Types",
                    ['positive', 'negative', 'boundary', 'integration', 'security', 'compliance'],
                    default=['positive', 'negative', 'compliance']
                )
                
                if st.button("🚀 Generate Test Cases", type="primary"):
                    with st.spinner("Generating test cases with AI..."):
                        try:
                            # Initialize test case generator
                            generator = TestCaseGenerator()
                            
                            # Generate test cases
                            test_cases = generator.generate_test_cases(
                                st.session_state.requirements,
                                st.session_state.compliance_mappings
                            )
                            
                            # Store in session state
                            st.session_state.test_cases = test_cases
                            
                            st.success(f"✅ Generated {len(test_cases)} test cases!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating test cases: {str(e)}")
                            st.info("💡 Make sure you have configured your API key in the sidebar")
            
            with col2:
                st.markdown("#### 🎯 Generation Options")
                st.markdown("""
                **Test Types:**
                - ✅ Positive Testing
                - ❌ Negative Testing  
                - 🔄 Boundary Testing
                - 🔗 Integration Testing
                - 🔒 Security Testing
                - 📋 Compliance Testing
                """)
                
                st.markdown("**AI Features:**")
                st.markdown("""
                - 🤖 AI-powered generation
                - 📊 Compliance mapping
                - 🎯 Priority assignment
                - 📝 Step-by-step actions
                """)
        
        # Display generated test cases
        if 'test_cases' in st.session_state and st.session_state.test_cases:
            st.markdown("### 📋 Generated Test Cases")
            
            # Test cases summary
            test_cases = st.session_state.test_cases
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Test Cases", len(test_cases))
            with col2:
                positive_count = sum(1 for tc in test_cases if getattr(tc, 'test_case_type', None) == 'positive')
                st.metric("Positive Tests", positive_count)
            with col3:
                compliance_count = sum(1 for tc in test_cases if getattr(tc, 'test_case_type', None) == 'compliance')
                st.metric("Compliance Tests", compliance_count)
            with col4:
                high_priority = sum(1 for tc in test_cases if getattr(tc, 'priority', None) == 'high')
                st.metric("High Priority", high_priority)
            
            # Test cases table
            tc_data = []
            for tc in test_cases[:10]:  # Show first 10
                tc_data.append({
                    'ID': getattr(tc, 'id', 'N/A'),
                    'Title': getattr(tc, 'title', 'N/A')[:50] + '...',
                    'Type': getattr(tc, 'test_case_type', 'N/A'),
                    'Priority': getattr(tc, 'priority', 'N/A'),
                    'Steps': len(getattr(tc, 'test_steps', []))
                })
            
            df = pd.DataFrame(tc_data)
            st.dataframe(df, use_container_width=True)
            
            if len(test_cases) > 10:
                st.info(f"Showing first 10 of {len(test_cases)} test cases")
            
            # Show detailed test case
            if st.checkbox("🔍 Show Detailed Test Case"):
                selected_idx = st.selectbox("Select Test Case", range(len(test_cases)))
                if selected_idx is not None:
                    tc = test_cases[selected_idx]
                    st.markdown(f"**Test Case: {getattr(tc, 'id', 'N/A')}**")
                    st.markdown(f"**Title:** {getattr(tc, 'title', 'N/A')}")
                    st.markdown(f"**Description:** {getattr(tc, 'description', 'N/A')}")
                    st.markdown(f"**Type:** {getattr(tc, 'test_case_type', 'N/A')}")
                    st.markdown(f"**Priority:** {getattr(tc, 'priority', 'N/A')}")
                    
                    # Test steps
                    steps = getattr(tc, 'test_steps', [])
                    if steps:
                        st.markdown("**Test Steps:**")
                        for i, step in enumerate(steps[:5], 1):  # Show first 5 steps
                            st.markdown(f"{i}. {getattr(step, 'action', 'N/A')}")
                            st.markdown(f"   Expected: {getattr(step, 'expected_result', 'N/A')}")
    
    with tab3:
        st.markdown("### 📊 Export & Traceability Matrix")
        
        if 'test_cases' not in st.session_state or not st.session_state.test_cases:
            st.warning("⚠️ Please generate test cases first in the Test Generator tab")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Export Test Cases")
                
                # Export options
                export_format = st.selectbox(
                    "Select Export Format",
                    ['Excel (.xlsx)', 'JSON (.json)', 'CSV (.csv)']
                )
                
                if st.button("📤 Export Test Cases", type="primary"):
                    with st.spinner("Exporting test cases..."):
                        try:
                            # Initialize export manager
                            export_manager = ExportManager()
                            
                            # Determine file extension
                            format_map = {
                                'Excel (.xlsx)': 'excel',
                                'JSON (.json)': 'json',
                                'CSV (.csv)': 'csv'
                            }
                            
                            format_type = format_map[export_format]
                            filename = f"healthcare_test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                            
                            # Export test cases
                            success = export_manager.export_test_cases(
                                st.session_state.test_cases,
                                filename,
                                format_type
                            )
                            
                            if success:
                                st.success(f"✅ Test cases exported to {filename}")
                                
                                # Provide download link
                                with open(filename, 'rb') as f:
                                    st.download_button(
                                        label="📥 Download File",
                                        data=f.read(),
                                        file_name=filename,
                                        mime="application/octet-stream"
                                    )
                            else:
                                st.error("❌ Export failed")
                                
                        except Exception as e:
                            st.error(f"❌ Error exporting: {str(e)}")
                
                st.markdown("#### Generate Traceability Matrix")
                
                if st.button("🔗 Generate Traceability Matrix", type="secondary"):
                    with st.spinner("Generating traceability matrix..."):
                        try:
                            # Initialize traceability matrix generator
                            matrix_generator = TraceabilityMatrixGenerator()
                            
                            # Generate traceability matrix
                            matrix_data = matrix_generator.generate_traceability_matrix(
                                st.session_state.requirements,
                                st.session_state.test_cases,
                                st.session_state.compliance_mappings
                            )
                            
                            # Store in session state
                            st.session_state.matrix_data = matrix_data
                            
                            st.success("✅ Traceability matrix generated!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating traceability matrix: {str(e)}")
            
            with col2:
                st.markdown("#### 📊 Export Options")
                st.markdown("""
                **Supported Formats:**
                - 📊 Excel (.xlsx)
                - 📄 JSON (.json)
                - 📋 CSV (.csv)
                - 🔗 Jira Integration
                - ☁️ Azure DevOps
                """)
                
                st.markdown("**Traceability Features:**")
                st.markdown("""
                - 🔗 Requirement → Test Case
                - 📋 Compliance Mapping
                - 📊 Coverage Analysis
                - 📈 Audit Trail
                """)
        
        # Display traceability matrix
        if 'matrix_data' in st.session_state and st.session_state.matrix_data:
            st.markdown("### 🔗 Traceability Matrix")
            
            matrix_data = st.session_state.matrix_data
            coverage_summary = matrix_data.get('matrix_views', {}).get('coverage_summary', {})
            
            # Coverage metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requirements", coverage_summary.get('total_requirements', 0))
            with col2:
                st.metric("Total Test Cases", coverage_summary.get('total_test_cases', 0))
            with col3:
                st.metric("Covered Requirements", coverage_summary.get('covered_requirements', 0))
            with col4:
                coverage_pct = coverage_summary.get('coverage_percentage', 0)
                st.metric("Coverage %", f"{coverage_pct}%")
            
            # Export traceability matrix
            if st.button("📤 Export Traceability Matrix"):
                with st.spinner("Exporting traceability matrix..."):
                    try:
                        filename = f"traceability_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        success = matrix_generator.export_traceability_matrix(
                            matrix_data,
                            filename,
                            'excel'
                        )
                        
                        if success:
                            st.success(f"✅ Traceability matrix exported to {filename}")
                            
                            with open(filename, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Traceability Matrix",
                                    data=f.read(),
                                    file_name=filename,
                                    mime="application/octet-stream"
                                )
                        else:
                            st.error("❌ Export failed")
                            
                    except Exception as e:
                        st.error(f"❌ Error exporting: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏥 Healthcare AI Test Case Generator | Built with Streamlit | 
        <a href='https://github.com/your-username/healthcare-ai-testcase-generator' target='_blank'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
