# Universal File to Markdown Converter

A simple, fast, and universal file converter that transforms any document, image, or data file into clean markdown format.

## 🚀 Features

- **Drag & Drop Interface**: Simple file upload with drag and drop
- **Universal Conversion**: Supports 10+ file formats (PDF, DOCX, PPTX, XLSX, images, etc.)
- **OCR Support**: Automatic text extraction from images
- **Instant Preview**: See first 1000 characters immediately
- **One-Click Download**: Get your markdown file instantly
- **Clean Output**: Properly formatted markdown with metadata

## 📋 Supported Formats

- **Documents**: PDF, DOCX, PPTX, XLSX, HTML, TXT, MD
- **Images**: JPG, PNG, BMP, GIF (with OCR)
- **Data**: CSV, JSON, XML
- **Archives**: ZIP (extracts and processes contents)

## 🛠️ Installation & Usage

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd universal-file-converter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. **Fork this repository**
2. **Connect to Streamlit Cloud** at [share.streamlit.io](https://share.streamlit.io)
3. **Deploy** by selecting your forked repository
4. **Done!** Your app is live

## 💻 How It Works

1. **Upload**: Drag and drop any supported file
2. **Convert**: Powered by Microsoft's MarkItDown library
3. **Preview**: See the first 1000 characters of converted text  
4. **Download**: Get the complete markdown file

## 🔧 Technical Details

- **Framework**: Streamlit for web interface
- **Converter**: Microsoft MarkItDown for universal file processing  
- **Processing**: Temporary file handling for security
- **Output**: Clean markdown with metadata headers
- **Performance**: Cached converter initialization for speed

## 📦 Dependencies

Core libraries used:
- `streamlit` - Web application framework
- `markitdown` - Microsoft's universal document converter
- `pillow` - Image processing support
- `python-magic` - File type detection

## 🌟 Why This App?

- **Simple**: Just drag, drop, and download
- **Fast**: Optimized processing with caching
- **Universal**: Handles almost any file format
- **Clean**: Produces well-formatted markdown
- **Free**: Open source and free to use
- **Reliable**: Built on Microsoft's proven MarkItDown library

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

**Built with ❤️ using Streamlit and Microsoft MarkItDown**