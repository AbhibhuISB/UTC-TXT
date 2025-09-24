import streamlit as st
import tempfile
import os
from pathlib import Path
from datetime import datetime
import base64
import mimetypes

# Core conversion library
from markitdown import MarkItDown

# Initialize the MarkItDown converter
@st.cache_resource
def get_converter():
    """Initialize and cache the MarkItDown converter"""
    return MarkItDown()

def format_file_size(size_bytes):
    """
    Convert bytes to human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def convert_file_to_markdown(file_content, filename):
    """
    Universal file-to-markdown converter using MarkItDown
    
    Args:
        file_content (bytes): Raw file content as bytes
        filename (str): Original filename with extension
    
    Returns:
        dict: Conversion result containing success status, text, file info, and error message
    """
    result = {
        'success': False,
        'text': '',
        'file_info': {},
        'error': ''
    }
    
    try:
        # Get file information
        file_size = len(file_content)
        file_ext = Path(filename).suffix.lower()
        
        result['file_info'] = {
            'filename': filename,
            'size_bytes': file_size,
            'size_readable': format_file_size(file_size),
            'extension': file_ext,
            'mime_type': mimetypes.guess_type(filename)[0] or 'unknown'
        }
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Convert file using MarkItDown
            md_converter = get_converter()
            conversion_result = md_converter.convert(temp_file_path)
            
            # Extract converted text
            if hasattr(conversion_result, 'text_content'):
                result['text'] = conversion_result.text_content
            else:
                result['text'] = str(conversion_result)
            
            result['success'] = True
            
        except Exception as convert_error:
            result['error'] = f"Conversion error: {str(convert_error)}"
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        result['error'] = f"File processing error: {str(e)}"
    
    return result

def create_download_link(text_content, original_filename):
    """
    Create a download link for the converted markdown text
    
    Args:
        text_content (str): The converted text content
        original_filename (str): Original filename
        
    Returns:
        tuple: (download_filename, b64_content) for download
    """
    # Generate download filename
    base_name = Path(original_filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_filename = f"{base_name}_converted_{timestamp}.md"
    
    # Prepare file content with metadata header
    file_header = f"""# Converted Markdown Document
<!-- 
Original File: {original_filename}
Conversion Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Converted Characters: {len(text_content):,}
Converter: MarkItDown (Microsoft)
-->

"""
    
    full_content = file_header + text_content
    b64_content = base64.b64encode(full_content.encode()).decode()
    
    return download_filename, b64_content

# Streamlit App Configuration
st.set_page_config(
    page_title="Universal File to Markdown Converter",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# App Header
st.title("📄 Universal File to Markdown Converter")
st.markdown("""
**Simple. Fast. Universal.**  
Drag, drop, and download your files as clean markdown text.
""")

# Supported formats info
with st.expander("📋 Supported File Formats"):
    st.markdown("""
    - **Documents**: PDF, DOCX, PPTX, XLSX, HTML, TXT, MD
    - **Images**: JPG, PNG, BMP, GIF (with OCR)
    - **Data**: CSV, JSON, XML
    - **Archives**: ZIP (extracts and processes contents)
    """)

st.markdown("---")

# File Upload Section
uploaded_file = st.file_uploader(
    "**Drop your file here or click to browse**",
    type=['pdf', 'docx', 'pptx', 'xlsx', 'html', 'htm', 'txt', 'md', 'csv', 'json', 'xml', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'zip'],
    help="Upload any document, image, or data file to convert to markdown format"
)

# Process uploaded file
if uploaded_file is not None:
    # Display file information
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({format_file_size(len(uploaded_file.getvalue()))})")
    
    # Convert file
    with st.spinner("🔄 Converting file to markdown..."):
        file_content = uploaded_file.getvalue()
        result = convert_file_to_markdown(file_content, uploaded_file.name)
    
    if result['success']:
        # Display conversion success
        info = result['file_info']
        st.success("✅ Conversion completed successfully!")
        
        # File information in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Type", info['extension'].upper())
        with col2:
            st.metric("Original Size", info['size_readable'])
        with col3:
            st.metric("Text Length", f"{len(result['text']):,} chars")
        
        st.markdown("---")
        
        # Preview Section
        st.subheader("📖 Preview (First 1000 characters)")
        
        preview_length = 1000
        preview_text = result['text'][:preview_length]
        
        # Display preview in a code block
        st.code(preview_text, language="markdown")
        
        if len(result['text']) > preview_length:
            remaining_chars = len(result['text']) - preview_length
            st.info(f"📝 **{remaining_chars:,} more characters available in full download**")
        
        st.markdown("---")
        
        # Download Section
        st.subheader("💾 Download Full Markdown File")
        
        download_filename, b64_content = create_download_link(result['text'], uploaded_file.name)
        
        # Download button
        st.download_button(
            label="📥 Download Full Markdown File",
            data=base64.b64decode(b64_content),
            file_name=download_filename,
            mime="text/markdown",
            use_container_width=True
        )
        
        st.success(f"📄 **{download_filename}** ready for download ({len(result['text']):,} characters)")
        
    else:
        # Display error
        st.error("❌ Conversion Failed")
        st.error(f"**Error:** {result['error']}")
        
        st.markdown("**Please try:**")
        st.markdown("- Check if the file format is supported")
        st.markdown("- Ensure the file is not corrupted")
        st.markdown("- Try a different file")

else:
    # Instructions when no file is uploaded
    st.info("👆 **Upload a file above to get started**")
    st.markdown("""
    ### How it works:
    1. **Drag & Drop** or click to upload any supported file
    2. **Preview** the first 1000 characters of converted markdown
    3. **Download** the complete markdown file
    
    That's it! Simple and fast. ⚡
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Powered by <a href='https://github.com/microsoft/markitdown' target='_blank'>MarkItDown</a> by Microsoft
</div>
""", unsafe_allow_html=True)