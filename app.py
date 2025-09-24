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

def convert_file_to_text(file_content, filename):
    """
    Universal file-to-text converter using MarkItDown
    
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
    Create a download link for the converted text file
    
    Args:
        text_content (str): The converted text content
        original_filename (str): Original filename
        
    Returns:
        tuple: (download_filename, b64_content) for download
    """
    # Generate download filename
    base_name = Path(original_filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_filename = f"{base_name}_converted_{timestamp}.txt"
    
    # Prepare file content with metadata header
    file_header = f"""# Converted Text Document
# Original File: {original_filename}
# Conversion Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Converted Characters: {len(text_content):,}
# Converter: MarkItDown (Microsoft)
# 
# ===== CONVERTED CONTENT BELOW =====

"""
    
    full_content = file_header + text_content
    b64_content = base64.b64encode(full_content.encode()).decode()
    
    return download_filename, b64_content

# Streamlit App Configuration
st.set_page_config(
    page_title="Docs to TXT Converter",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# App Header
st.title("📄 Docs to TXT Converter")
st.markdown("""
**Simple. Fast. Universal.**  
Drag, drop, and download your files as clean text.
""")

# Supported formats info
with st.expander("📋 Supported File Formats"):
    st.markdown("""
    - **Documents**: PDF, DOCX, PPTX, XLSX
    - **Images**: JPG, JPEG, PNG (with OCR)
    - **Audio**: MP3
    
    **File Size Limit**: 200MB per file
    """)

st.markdown("---")

# File Upload Section
uploaded_file = st.file_uploader(
    "**Drop your file here or click to browse**",
    type=['pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'jpeg', 'png', 'mp3'],
    help="Upload PDF, Office documents, images, or MP3 files to convert to text format"
)

# File size limit (200MB)
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB in bytes

# Process uploaded file
if uploaded_file is not None:
    # Get file content and size
    file_content = uploaded_file.getvalue()
    file_size = len(file_content)
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        st.error(f"❌ **File too large!** Your file is {format_file_size(file_size)}.")
        st.error(f"📏 **Maximum allowed size**: {format_file_size(MAX_FILE_SIZE)}")
        st.markdown("**Please try:**")
        st.markdown("- Compress your file before uploading")
        st.markdown("- Use a smaller file")
        st.markdown("- Split large documents into smaller parts")
        st.stop()
    
    # Check file type (additional validation)
    allowed_extensions = ['.pdf', '.docx', '.pptx', '.xlsx', '.jpg', '.jpeg', '.png', '.mp3']
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    if file_extension not in allowed_extensions:
        st.error(f"❌ **Unsupported file type**: `{file_extension}`")
        st.error("📋 **Supported formats**: PDF, DOCX, PPTX, XLSX, JPG, JPEG, PNG, MP3")
        st.markdown("**Please try:**")
        st.markdown("- Convert your file to a supported format")
        st.markdown("- Check the file extension is correct")
        st.stop()
    
    # Display file information
    st.success(f"✅ File uploaded: **{uploaded_file.name}** ({format_file_size(file_size)})")
    
    # Show progress for larger files
    if file_size > 10 * 1024 * 1024:  # 10MB
        st.info(f"📊 **Large file detected** ({format_file_size(file_size)}). Processing may take longer...")
    
    # Convert file with improved spinner message
    with st.spinner("Converting…"):
        result = convert_file_to_text(file_content, uploaded_file.name)
    
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
        
        # Download Section
        st.subheader("💾 Download Text File")
        
        download_filename, b64_content = create_download_link(result['text'], uploaded_file.name)
        
        # Download button
        st.download_button(
            label="📥 Download TXT File",
            data=base64.b64decode(b64_content),
            file_name=download_filename,
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )
        
        st.success(f"📄 **{download_filename}** ready for download ({len(result['text']):,} characters)")
        
        st.markdown("---")
        
        # Tabbed interface for preview and file size comparison
        tab1, tab2 = st.tabs(["📖 Rendered Preview", "📊 File Size Comparison"])
        
        with tab1:
            # Preview Section
            st.text_area(
                label="Converted Text Content",
                value=result['text'],
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
            
            st.info(f"📝 **Complete content shown above** ({len(result['text']):,} characters total). Download the file to save permanently.")
        
        with tab2:
            # File Size Comparison Table
            original_size = info['size_bytes']
            converted_size = len(result['text'].encode('utf-8'))  # Size of text in bytes
            
            # Calculate percentage reduction
            if original_size > 0:
                size_reduction_percent = ((original_size - converted_size) / original_size) * 100
            else:
                size_reduction_percent = 0
            
            # Create comparison table
            st.markdown("### 📊 Size Comparison")
            
            comparison_data = {
                "File Type": ["Original File", "Converted .txt File"],
                "File Size": [info['size_readable'], format_file_size(converted_size)]
            }
            
            # Display the comparison table
            st.dataframe(
                comparison_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Show percentage comparison
            if size_reduction_percent > 0:
                st.success(f"💡 **Text version is {size_reduction_percent:.1f}% smaller than the original file.**")
            elif size_reduction_percent < 0:
                st.info(f"📊 **Text version is {abs(size_reduction_percent):.1f}% larger than the original file.**")
            else:
                st.info("📊 **Text version is the same size as the original file.**")
            
            # Additional insights
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Space Saved", f"{format_file_size(max(0, original_size - converted_size))}")
            with col2:
                if converted_size > 0:
                    compression_ratio = original_size / converted_size
                    st.metric("Compression Ratio", f"{compression_ratio:.1f}:1")
                else:
                    st.metric("Compression Ratio", "N/A")
        
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
    2. **Preview** the converted text content
    3. **Compare** original vs text file sizes
    4. **Download** the complete text file
    
    That's it! Simple and fast. ⚡
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Powered by <a href='https://github.com/microsoft/markitdown' target='_blank'>MarkItDown</a> by Microsoft
</div>
""", unsafe_allow_html=True)