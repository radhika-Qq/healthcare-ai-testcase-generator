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

# Disable Streamlit's automatic rerun and polling
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_option('deprecation.showfileUploaderEncoding', False)

# Custom CSS and JavaScript
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
    .processing-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
    }
</style>

<script>
// Prevent multiple button clicks
let isProcessing = false;

function preventMultipleClicks() {
    if (isProcessing) {
        return false;
    }
    isProcessing = true;
    
    // Re-enable after 5 seconds as fallback
    setTimeout(() => {
        isProcessing = false;
    }, 5000);
    
    return true;
}

// Add click prevention to all buttons
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!preventMultipleClicks()) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    });
});

// Monitor for status calls and block them
let statusCallCount = 0;
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    if (typeof url === 'string' && url.includes('status')) {
        statusCallCount++;
        if (statusCallCount > 1) {
            console.log('Blocked duplicate status call:', url);
            return Promise.resolve(new Response('{"status": "blocked"}', {status: 200}));
        }
    }
    return originalFetch.apply(this, args);
};

// Reset status call count every 10 seconds
setInterval(() => {
    statusCallCount = 0;
}, 10000);
</script>
""", unsafe_allow_html=True)

def get_enum_value(obj):
    """Helper function to get string value from enum objects."""
    if obj is None:
        return ''
    if hasattr(obj, 'value'):
        return obj.value
    return str(obj)

def is_request_in_progress(request_type: str) -> bool:
    """Check if a specific type of request is already in progress."""
    return st.session_state.get(f'{request_type}_in_progress', False)

def set_request_status(request_type: str, in_progress: bool):
    """Set the status of a specific request type."""
    st.session_state[f'{request_type}_in_progress'] = in_progress

def get_request_id(request_type: str, *args) -> str:
    """Generate a unique request ID based on request type and arguments."""
    import hashlib
    content = f"{request_type}_{'_'.join(str(arg) for arg in args)}"
    return hashlib.md5(content.encode()).hexdigest()[:8]

def is_duplicate_request(request_type: str, request_id: str) -> bool:
    """Check if this is a duplicate request."""
    last_request = st.session_state.get(f'last_{request_type}_request', '')
    return last_request == request_id

def is_any_request_in_progress() -> bool:
    """Check if any request is currently in progress."""
    request_types = ['parse_document', 'sample_document', 'generate_test_cases', 'export_data']
    return any(st.session_state.get(f'{req_type}_in_progress', False) for req_type in request_types)

def block_all_requests():
    """Block all requests when any request is in progress."""
    return is_any_request_in_progress()

def increment_request_counter():
    """Increment the global request counter."""
    if 'request_counter' not in st.session_state:
        st.session_state.request_counter = 0
    st.session_state.request_counter += 1

def reset_request_locks():
    """Reset all request locks (for debugging)."""
    request_types = ['parse_document', 'sample_document', 'generate_test_cases', 'export_data']
    for req_type in request_types:
        st.session_state[f'{req_type}_in_progress'] = False

def main():
    # Initialize request counter
    if 'request_counter' not in st.session_state:
        st.session_state.request_counter = 0
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare AI Test Case Generator</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Test Case Generation for Healthcare Software Compliance")
    
    # Global status indicator
    if is_any_request_in_progress():
        st.warning("🔄 **Operation in progress...** Please wait for the current operation to complete before starting a new one.")
        st.markdown("---")
    
    # Request counter and debug panel
    if st.session_state.request_counter > 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📊 Total API requests made this session: {st.session_state.request_counter}")
        with col2:
            if st.button("🔄 Reset Locks", help="Reset all request locks (for debugging)"):
                reset_request_locks()
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏥 Healthcare AI")
        st.markdown("---")
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
        with st.form("api_key_form"):
            api_key = st.text_input("Google AI API Key", type="password", help="Enter your Google AI API key")
            submitted = st.form_submit_button("Save API Key")
        
        if submitted and api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key configured")
        elif submitted and not api_key:
            st.warning("⚠️ Please enter an API key")
        elif 'api_key' in st.session_state and st.session_state.api_key:
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
                if st.button("🔍 Parse Document", type="primary", key="parse_uploaded", disabled=block_all_requests()):
                    # Generate unique request ID
                    request_id = get_request_id("parse_document", uploaded_file.name, uploaded_file.size)
                    
                    # Check for duplicate requests
                    if is_duplicate_request("parse_document", request_id):
                        st.warning("⚠️ This document is already being processed. Please wait...")
                    elif is_any_request_in_progress():
                        st.warning("⚠️ Another operation is in progress. Please wait...")
                    else:
                        # Set request status and ID
                        set_request_status("parse_document", True)
                        st.session_state['last_parse_document_request'] = request_id
                        
                        with st.spinner("Parsing document and extracting requirements..."):
                            try:
                                # Increment request counter
                                increment_request_counter()
                                
                                # Parse the document
                                result = parse_healthcare_document(temp_path, st.session_state.get('api_key'))
                                
                                # Store in session state
                                st.session_state.parsed_data = result
                                st.session_state.requirements = result.get('requirements', [])
                                st.session_state.compliance_mappings = result.get('compliance_mappings', [])
                                
                                st.success("✅ Document parsed successfully!")
                                
                            except Exception as e:
                                error_msg = str(e)
                                st.error(f"❌ Error parsing document: {error_msg}")
                                
                                # Provide specific guidance based on error type
                                if "zip file" in error_msg.lower() or "not a zip file" in error_msg.lower():
                                    st.info("💡 This error usually occurs when the file is corrupted or in an unsupported format. Please try:")
                                    st.markdown("""
                                    - **Re-save the document** in a supported format (PDF, Word, or text)
                                    - **Check if the file is corrupted** by opening it in its native application
                                    - **Try a different file** to test if the issue persists
                                    - **Use the sample documents** provided in the right panel
                                    """)
                                elif "unsupported file format" in error_msg.lower():
                                    st.info("💡 Please use one of these supported formats: PDF, DOCX, DOC, XML, HTML, or TXT")
                                else:
                                    st.info("💡 Try with a different file or check the file format")
                            finally:
                                # Clean up temp file and reset status
                                Path(temp_path).unlink(missing_ok=True)
                                set_request_status("parse_document", False)
        
        with col2:
            st.markdown("#### 📋 Sample Document")
            st.markdown("""
            **Try with our sample:**
            - Medical Device Requirements
            - Patient Management System
            - Pharmacy Management
            """)
            
            if st.button("📥 Use Sample Document", key="use_sample", disabled=block_all_requests()):
                # Generate unique request ID for sample document
                request_id = get_request_id("sample_document", "medical_device_requirements.txt")
                
                # Check for duplicate requests
                if is_duplicate_request("sample_document", request_id):
                    st.warning("⚠️ Sample document is already being processed. Please wait...")
                elif is_any_request_in_progress():
                    st.warning("⚠️ Another operation is in progress. Please wait...")
                else:
                    # Set request status and ID
                    set_request_status("sample_document", True)
                    st.session_state['last_sample_document_request'] = request_id
                    
                    sample_path = "sample_demo_data/medical_device_requirements.txt"
                    if Path(sample_path).exists():
                        with st.spinner("Loading sample document..."):
                            try:
                                # Increment request counter
                                increment_request_counter()
                                
                                result = parse_healthcare_document(sample_path, st.session_state.get('api_key'))
                                st.session_state.parsed_data = result
                                st.session_state.requirements = result.get('requirements', [])
                                st.session_state.compliance_mappings = result.get('compliance_mappings', [])
                                st.success("✅ Sample document loaded!")
                            except Exception as e:
                                error_msg = str(e)
                                st.error(f"❌ Error loading sample: {error_msg}")
                                
                                if "zip file" in error_msg.lower() or "not a zip file" in error_msg.lower():
                                    st.info("💡 Sample document appears to be corrupted. Please try uploading your own document or contact support.")
                                else:
                                    st.info("💡 There was an issue loading the sample document. Please try uploading your own document.")
                            finally:
                                set_request_status("sample_document", False)
                    else:
                        st.error("❌ Sample document not found")
                        set_request_status("sample_document", False)
        
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
                compliance_refs = summary.get('compliance_refs', [])
                compliance_count = len(compliance_refs) if isinstance(compliance_refs, list) else 0
                st.metric("Compliance Refs", compliance_count)
            with col4:
                st.metric("High Priority", summary.get('by_priority', {}).get('high', 0))
            
            # Requirements table with pagination
            if st.session_state.requirements:
                # Pagination controls
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    items_per_page = st.selectbox(
                        "Items per page",
                        [10, 25, 50, 100, "All"],
                        index=0,
                        key="req_items_per_page"
                    )
                    if items_per_page == "All":
                        items_per_page = total_requirements
                
                with col2:
                    total_requirements = len(st.session_state.requirements)
                    total_pages = (total_requirements + items_per_page - 1) // items_per_page
                    
                    if 'req_current_page' not in st.session_state:
                        st.session_state.req_current_page = 1
                    
                    if total_pages > 1:
                        current_page = st.selectbox(
                            f"Page (1-{total_pages})",
                            range(1, total_pages + 1),
                            index=st.session_state.req_current_page - 1,
                            key="req_page_selector"
                        )
                        st.session_state.req_current_page = current_page
                    else:
                        st.session_state.req_current_page = 1
                
                with col3:
                    # Remove refresh button to prevent multiple API calls
                    st.markdown("**Page Controls**")
                    st.markdown("Use page selector to navigate")
                
                # Calculate pagination
                start_idx = (st.session_state.req_current_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, total_requirements)
                
                # Prepare data for current page
                req_data = []
                for req in st.session_state.requirements[start_idx:end_idx]:
                    # Handle both dictionary and object formats
                    if isinstance(req, dict):
                        req_data.append({
                            'ID': req.get('id', 'N/A'),
                            'Description': req.get('description', 'N/A')[:100] + '...',
                            'Type': req.get('type', 'N/A'),
                            'Priority': req.get('priority', 'N/A')
                        })
                    else:
                        req_data.append({
                            'ID': getattr(req, 'id', 'N/A'),
                            'Description': getattr(req, 'description', 'N/A')[:100] + '...',
                            'Type': getattr(req, 'type', 'N/A'),
                            'Priority': getattr(req, 'priority', 'N/A')
                        })
                
                df = pd.DataFrame(req_data)
                st.dataframe(df, use_container_width=True)
                
                # Pagination info
                if total_pages > 1:
                    st.info(f"Showing {start_idx + 1}-{end_idx} of {total_requirements} requirements (Page {st.session_state.req_current_page} of {total_pages})")
                else:
                    st.info(f"Showing all {total_requirements} requirements")
    
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
                
                if st.button("🚀 Generate Test Cases", type="primary", disabled=block_all_requests()):
                    # Generate unique request ID for test case generation
                    req_count = len(st.session_state.requirements) if st.session_state.requirements else 0
                    request_id = get_request_id("generate_test_cases", req_count, str(test_types))
                    
                    # Check for duplicate requests
                    if is_duplicate_request("generate_test_cases", request_id):
                        st.warning("⚠️ Test cases are already being generated for these requirements. Please wait...")
                    elif is_any_request_in_progress():
                        st.warning("⚠️ Another operation is in progress. Please wait...")
                    else:
                        # Set request status and ID
                        set_request_status("generate_test_cases", True)
                        st.session_state['last_generate_test_cases_request'] = request_id
                        
                        with st.spinner("Generating test cases with AI..."):
                            try:
                                # Increment request counter
                                increment_request_counter()
                                
                                # Initialize test case generator
                                generator = TestCaseGenerator(api_key=st.session_state.get('api_key'))
                                
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
                            finally:
                                set_request_status("generate_test_cases", False)
            
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
                positive_count = sum(1 for tc in test_cases if get_enum_value(getattr(tc, 'test_case_type', None)) == 'positive')
                st.metric("Positive Tests", positive_count)
            with col3:
                compliance_count = sum(1 for tc in test_cases if get_enum_value(getattr(tc, 'test_case_type', None)) == 'compliance')
                st.metric("Compliance Tests", compliance_count)
            with col4:
                high_priority = sum(1 for tc in test_cases if get_enum_value(getattr(tc, 'priority', None)) == 'high')
                st.metric("High Priority", high_priority)
            
            # Filtering options
            st.markdown("#### 🔍 Filter Test Cases")
            col1, col2, col3 = st.columns(3)
            
            # Clear filters button
            if st.button("🗑️ Clear All Filters"):
                # Clear session state
                if 'filter_type' in st.session_state:
                    del st.session_state['filter_type']
                if 'filter_priority' in st.session_state:
                    del st.session_state['filter_priority']
                if 'search_text' in st.session_state:
                    del st.session_state['search_text']
                st.rerun()
            
            with col1:
                filter_type = st.multiselect(
                    "Filter by Type",
                    ['positive', 'negative', 'boundary', 'integration', 'security', 'compliance'],
                    default=st.session_state.get('filter_type', [])
                )
            
            with col2:
                filter_priority = st.multiselect(
                    "Filter by Priority",
                    ['high', 'medium', 'low'],
                    default=st.session_state.get('filter_priority', [])
                )
            
            with col3:
                search_text = st.text_input("Search in Title/Description", 
                                          value=st.session_state.get('search_text', ''),
                                          placeholder="Enter search term...")
            
            # Store current filter values in session state
            st.session_state['filter_type'] = filter_type
            st.session_state['filter_priority'] = filter_priority
            st.session_state['search_text'] = search_text
            
            # Reset pagination if filters changed
            if (st.session_state.get('prev_filter_type', []) != filter_type or 
                st.session_state.get('prev_filter_priority', []) != filter_priority or 
                st.session_state.get('prev_search_text', '') != search_text):
                st.session_state.tc_current_page = 1
                st.session_state['prev_filter_type'] = filter_type
                st.session_state['prev_filter_priority'] = filter_priority
                st.session_state['prev_search_text'] = search_text
            
            # Apply filters
            filtered_test_cases = test_cases.copy()
            
            if filter_type:
                filtered_test_cases = [tc for tc in filtered_test_cases 
                                     if get_enum_value(getattr(tc, 'test_case_type', None)).lower() in filter_type]
            
            if filter_priority:
                filtered_test_cases = [tc for tc in filtered_test_cases 
                                     if get_enum_value(getattr(tc, 'priority', None)).lower() in filter_priority]
            
            if search_text:
                filtered_test_cases = [tc for tc in filtered_test_cases 
                                     if search_text.lower() in getattr(tc, 'title', '').lower() or 
                                        search_text.lower() in getattr(tc, 'description', '').lower()]
            
            # Test cases table with pagination
            if filtered_test_cases:
                # Pagination controls
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    tc_items_per_page = st.selectbox(
                        "Items per page",
                        [10, 25, 50, 100, "All"],
                        index=0,
                        key="tc_items_per_page"
                    )
                    if tc_items_per_page == "All":
                        tc_items_per_page = total_test_cases
                
                with col2:
                    total_test_cases = len(filtered_test_cases)
                    total_tc_pages = (total_test_cases + tc_items_per_page - 1) // tc_items_per_page
                    
                    if 'tc_current_page' not in st.session_state:
                        st.session_state.tc_current_page = 1
                    
                    if total_tc_pages > 1:
                        current_tc_page = st.selectbox(
                            f"Page (1-{total_tc_pages})",
                            range(1, total_tc_pages + 1),
                            index=st.session_state.tc_current_page - 1,
                            key="tc_page_selector"
                        )
                        st.session_state.tc_current_page = current_tc_page
                    else:
                        st.session_state.tc_current_page = 1
                
                with col3:
                    if st.button("🔄 Refresh", key="refresh_tc"):
                        st.session_state.tc_current_page = 1
                        st.rerun()
                
                # Calculate pagination
                start_tc_idx = (st.session_state.tc_current_page - 1) * tc_items_per_page
                end_tc_idx = min(start_tc_idx + tc_items_per_page, total_test_cases)
                
                # Prepare data for current page
                tc_data = []
                for tc in filtered_test_cases[start_tc_idx:end_tc_idx]:
                    tc_data.append({
                        'ID': getattr(tc, 'id', 'N/A'),
                        'Title': getattr(tc, 'title', 'N/A')[:50] + '...',
                        'Type': get_enum_value(getattr(tc, 'test_case_type', None)),
                        'Priority': get_enum_value(getattr(tc, 'priority', None)),
                        'Steps': len(getattr(tc, 'test_steps', []))
                    })
                
                df = pd.DataFrame(tc_data)
                st.dataframe(df, use_container_width=True)
                
                # Pagination info
                if len(filtered_test_cases) != len(test_cases):
                    if total_tc_pages > 1:
                        st.info(f"Showing {start_tc_idx + 1}-{end_tc_idx} of {total_test_cases} filtered test cases (from {len(test_cases)} total) - Page {st.session_state.tc_current_page} of {total_tc_pages}")
                    else:
                        st.info(f"Showing all {total_test_cases} filtered test cases (from {len(test_cases)} total)")
                elif total_tc_pages > 1:
                    st.info(f"Showing {start_tc_idx + 1}-{end_tc_idx} of {total_test_cases} test cases - Page {st.session_state.tc_current_page} of {total_tc_pages}")
                else:
                    st.info(f"Showing all {total_test_cases} test cases")
            else:
                st.warning("No test cases match the current filters")
            
            # Show detailed test case
            if st.checkbox("🔍 Show Detailed Test Case"):
                if filtered_test_cases:
                    # Create options for selectbox with test case info
                    options = [f"{getattr(tc, 'id', 'N/A')} - {getattr(tc, 'title', 'N/A')[:30]}..." 
                              for tc in filtered_test_cases]
                    selected_idx = st.selectbox("Select Test Case", range(len(filtered_test_cases)), 
                                              format_func=lambda x: options[x])
                    if selected_idx is not None:
                        tc = filtered_test_cases[selected_idx]
                else:
                    st.warning("No test cases match the current filters")
                    tc = None
                
                if tc is not None:
                    st.markdown(f"**Test Case: {getattr(tc, 'id', 'N/A')}**")
                    st.markdown(f"**Title:** {getattr(tc, 'title', 'N/A')}")
                    st.markdown(f"**Description:** {getattr(tc, 'description', 'N/A')}")
                    st.markdown(f"**Type:** {get_enum_value(getattr(tc, 'test_case_type', None))}")
                    st.markdown(f"**Priority:** {get_enum_value(getattr(tc, 'priority', None))}")
                    
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
                
                if st.button("📤 Export Test Cases", type="primary", disabled=block_all_requests()):
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
            if st.button("📤 Export Traceability Matrix", disabled=block_all_requests()):
                with st.spinner("Exporting traceability matrix..."):
                    try:
                        # Initialize traceability matrix generator
                        matrix_generator = TraceabilityMatrixGenerator()
                        
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
        <a href='https://github.com/radhika-Qq/healthcare-ai-testcase-generator' target='_blank'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
