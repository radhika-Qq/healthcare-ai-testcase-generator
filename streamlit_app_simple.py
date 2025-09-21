#!/usr/bin/env python3
"""
Healthcare AI Test Case Generator - Simplified Streamlit Prototype
A simplified version for easy deployment on Streamlit Cloud.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import io

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
</style>
""", unsafe_allow_html=True)

def create_sample_requirements():
    """Create sample requirements for demo."""
    return [
        {
            "id": "REQ-001",
            "description": "The system shall store patient demographic information including name, date of birth, and medical record number.",
            "type": "functional",
            "priority": "high",
            "compliance_refs": ["HIPAA", "FDA_21_CFR_820"]
        },
        {
            "id": "REQ-002", 
            "description": "The system shall encrypt all patient data in accordance with HIPAA requirements.",
            "type": "security",
            "priority": "critical",
            "compliance_refs": ["HIPAA", "FDA_21_CFR_11"]
        },
        {
            "id": "REQ-003",
            "description": "The system shall maintain an audit trail of all patient data access.",
            "type": "compliance",
            "priority": "high",
            "compliance_refs": ["FDA_21_CFR_820", "ISO_13485"]
        },
        {
            "id": "REQ-004",
            "description": "The system shall support electronic health record (EHR) integration per HL7 FHIR standards.",
            "type": "integration",
            "priority": "medium",
            "compliance_refs": ["HL7_FHIR", "IEC_62304"]
        },
        {
            "id": "REQ-005",
            "description": "The system shall validate clinical data entry against medical terminology standards.",
            "type": "functional",
            "priority": "high",
            "compliance_refs": ["IEC_62304", "ISO_13485"]
        }
    ]

def create_sample_test_cases():
    """Create sample test cases for demo."""
    return [
        {
            "id": "TC-001",
            "title": "Verify patient demographic data storage",
            "description": "Test that patient demographic information is correctly stored in the system",
            "type": "positive",
            "priority": "high",
            "requirement_id": "REQ-001",
            "test_steps": [
                {"step": 1, "action": "Navigate to patient registration page", "expected": "Page loads successfully"},
                {"step": 2, "action": "Enter patient name, DOB, and MRN", "expected": "Data is accepted"},
                {"step": 3, "action": "Click Save button", "expected": "Patient data is stored"},
                {"step": 4, "action": "Verify data in database", "expected": "Data matches input"}
            ]
        },
        {
            "id": "TC-002",
            "title": "Verify data encryption compliance",
            "description": "Test that patient data is encrypted according to HIPAA requirements",
            "type": "compliance",
            "priority": "critical",
            "requirement_id": "REQ-002",
            "test_steps": [
                {"step": 1, "action": "Store sensitive patient data", "expected": "Data is encrypted at rest"},
                {"step": 2, "action": "Transmit data over network", "expected": "Data is encrypted in transit"},
                {"step": 3, "action": "Verify encryption algorithms", "expected": "Uses approved encryption standards"},
                {"step": 4, "action": "Test key management", "expected": "Encryption keys are properly managed"}
            ]
        },
        {
            "id": "TC-003",
            "title": "Verify audit trail functionality",
            "description": "Test that all patient data access is properly logged",
            "type": "compliance",
            "priority": "high",
            "requirement_id": "REQ-003",
            "test_steps": [
                {"step": 1, "action": "Access patient data", "expected": "Access is logged"},
                {"step": 2, "action": "Modify patient data", "expected": "Modification is logged"},
                {"step": 3, "action": "View audit trail", "expected": "All actions are recorded"},
                {"step": 4, "action": "Verify log integrity", "expected": "Logs cannot be tampered with"}
            ]
        }
    ]

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare AI Test Case Generator</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Test Case Generation for Healthcare Software Compliance")
    
    # Sidebar
    with st.sidebar:
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
        
        st.markdown("### 🔧 Demo Mode")
        st.info("This is a demo version showcasing the core features. For full AI functionality, deploy with API keys configured.")
    
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
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                st.info("📝 In the full version, this would parse the document and extract requirements using AI.")
            
            # Demo button
            if st.button("🔍 Load Sample Requirements", type="primary"):
                st.session_state.requirements = create_sample_requirements()
                st.session_state.compliance_mappings = [
                    {"requirement_id": "REQ-001", "standard": "HIPAA", "clause": "164.312(a)(1)"},
                    {"requirement_id": "REQ-002", "standard": "FDA_21_CFR_820", "clause": "820.30(g)"},
                    {"requirement_id": "REQ-003", "standard": "ISO_13485", "clause": "4.2.4"}
                ]
                st.success("✅ Sample requirements loaded!")
        
        with col2:
            st.markdown("#### 📋 Sample Features")
            st.markdown("""
            **Try the demo:**
            - Click "Load Sample Requirements"
            - View extracted requirements
            - See compliance mappings
            """)
        
        # Display requirements
        if 'requirements' in st.session_state and st.session_state.requirements:
            st.markdown("### 📋 Extracted Requirements")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requirements", len(st.session_state.requirements))
            with col2:
                functional_count = sum(1 for req in st.session_state.requirements if req['type'] == 'functional')
                st.metric("Functional", functional_count)
            with col3:
                st.metric("Compliance Refs", len(st.session_state.compliance_mappings))
            with col4:
                high_priority = sum(1 for req in st.session_state.requirements if req['priority'] == 'high')
                st.metric("High Priority", high_priority)
            
            # Requirements table
            df = pd.DataFrame(st.session_state.requirements)
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.markdown("### 🧪 AI-Powered Test Case Generation")
        
        if 'requirements' not in st.session_state or not st.session_state.requirements:
            st.warning("⚠️ Please load sample requirements first in the Document Parser tab")
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
                
                if st.button("🚀 Generate Sample Test Cases", type="primary"):
                    st.session_state.test_cases = create_sample_test_cases()
                    st.success(f"✅ Generated {len(st.session_state.test_cases)} test cases!")
            
            with col2:
                st.markdown("#### 🎯 Generation Features")
                st.markdown("""
                **AI Capabilities:**
                - 🤖 Smart test case creation
                - 📊 Compliance mapping
                - 🎯 Priority assignment
                - 📝 Step-by-step actions
                """)
        
        # Display test cases
        if 'test_cases' in st.session_state and st.session_state.test_cases:
            st.markdown("### 📋 Generated Test Cases")
            
            # Test cases summary
            test_cases = st.session_state.test_cases
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Test Cases", len(test_cases))
            with col2:
                positive_count = sum(1 for tc in test_cases if tc['type'] == 'positive')
                st.metric("Positive Tests", positive_count)
            with col3:
                compliance_count = sum(1 for tc in test_cases if tc['type'] == 'compliance')
                st.metric("Compliance Tests", compliance_count)
            with col4:
                high_priority = sum(1 for tc in test_cases if tc['priority'] == 'high')
                st.metric("High Priority", high_priority)
            
            # Test cases table
            tc_data = []
            for tc in test_cases:
                tc_data.append({
                    'ID': tc['id'],
                    'Title': tc['title'][:50] + '...',
                    'Type': tc['type'],
                    'Priority': tc['priority'],
                    'Steps': len(tc['test_steps'])
                })
            
            df = pd.DataFrame(tc_data)
            st.dataframe(df, use_container_width=True)
            
            # Show detailed test case
            if st.checkbox("🔍 Show Detailed Test Case"):
                selected_idx = st.selectbox("Select Test Case", range(len(test_cases)))
                if selected_idx is not None:
                    tc = test_cases[selected_idx]
                    st.markdown(f"**Test Case: {tc['id']}**")
                    st.markdown(f"**Title:** {tc['title']}")
                    st.markdown(f"**Description:** {tc['description']}")
                    st.markdown(f"**Type:** {tc['type']}")
                    st.markdown(f"**Priority:** {tc['priority']}")
                    
                    # Test steps
                    st.markdown("**Test Steps:**")
                    for step in tc['test_steps']:
                        st.markdown(f"{step['step']}. {step['action']}")
                        st.markdown(f"   Expected: {step['expected']}")
    
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
                    # Create sample export data
                    export_data = {
                        "test_cases": st.session_state.test_cases,
                        "requirements": st.session_state.requirements,
                        "exported_at": datetime.now().isoformat(),
                        "total_test_cases": len(st.session_state.test_cases),
                        "total_requirements": len(st.session_state.requirements)
                    }
                    
                    if export_format == 'JSON (.json)':
                        json_str = json.dumps(export_data, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_str,
                            file_name=f"healthcare_test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    elif export_format == 'CSV (.csv)':
                        # Convert to CSV format
                        csv_data = []
                        for tc in st.session_state.test_cases:
                            csv_data.append({
                                'ID': tc['id'],
                                'Title': tc['title'],
                                'Type': tc['type'],
                                'Priority': tc['priority'],
                                'Requirement_ID': tc['requirement_id']
                            })
                        df = pd.DataFrame(csv_data)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"healthcare_test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:  # Excel
                        st.info("📊 Excel export would be available in the full version with openpyxl")
                    
                    st.success("✅ Export data prepared!")
                
                st.markdown("#### Generate Traceability Matrix")
                
                if st.button("🔗 Generate Traceability Matrix", type="secondary"):
                    # Create sample traceability data
                    traceability_data = {
                        "coverage_summary": {
                            "total_requirements": len(st.session_state.requirements),
                            "total_test_cases": len(st.session_state.test_cases),
                            "covered_requirements": len(st.session_state.requirements),
                            "coverage_percentage": 100.0
                        },
                        "traceability_items": [
                            {
                                "requirement_id": req['id'],
                                "test_case_id": tc['id'],
                                "coverage_type": "direct",
                                "compliance_standard": "FDA_21_CFR_820"
                            }
                            for req in st.session_state.requirements
                            for tc in st.session_state.test_cases
                            if req['id'] == tc['requirement_id']
                        ]
                    }
                    
                    st.session_state.traceability_data = traceability_data
                    st.success("✅ Traceability matrix generated!")
            
            with col2:
                st.markdown("#### 📊 Export Features")
                st.markdown("""
                **Supported Formats:**
                - 📊 Excel (.xlsx)
                - 📄 JSON (.json)
                - 📋 CSV (.csv)
                - 🔗 Jira Integration
                - ☁️ Azure DevOps
                """)
        
        # Display traceability matrix
        if 'traceability_data' in st.session_state and st.session_state.traceability_data:
            st.markdown("### 🔗 Traceability Matrix")
            
            traceability_data = st.session_state.traceability_data
            coverage_summary = traceability_data['coverage_summary']
            
            # Coverage metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Requirements", coverage_summary['total_requirements'])
            with col2:
                st.metric("Total Test Cases", coverage_summary['total_test_cases'])
            with col3:
                st.metric("Covered Requirements", coverage_summary['covered_requirements'])
            with col4:
                st.metric("Coverage %", f"{coverage_summary['coverage_percentage']}%")
            
            # Export traceability matrix
            if st.button("📤 Export Traceability Matrix"):
                json_str = json.dumps(traceability_data, indent=2)
                st.download_button(
                    label="📥 Download Traceability Matrix",
                    data=json_str,
                    file_name=f"traceability_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🏥 Healthcare AI Test Case Generator | Built with Streamlit | 
        <a href='https://github.com/your-username/healthcare-ai-testcase-generator' target='_blank'>GitHub</a></p>
        <p><strong>Demo Version</strong> - For full AI functionality, deploy with API keys configured</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
