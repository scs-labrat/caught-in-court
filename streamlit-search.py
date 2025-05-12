import os
import io
import base64
import PyPDF2
import streamlit as st

# Page config
st.set_page_config(
    page_title="Court List Search",
    page_icon="⚖️",
    layout="centered",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        background-color: #0c0c0c;
        color: #f5f5f5;
        font-family: 'Fira Code', monospace;
    }
    .stTextInput > div > div > input {
        background-color: #1c1c1c;
        color: #f5f5f5;
    }
    .stButton button {
        background-color: #d72638;
        color: white;
        border-radius: 8px;
    }
    .stDownloadButton button {
        background-color: #277da1;
        color: white;
        border-radius: 8px;
    }
    .reportview-container .markdown-text-container {
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("# ⚖️ Daily Court List Search")
st.markdown("#### 🔍 Enter a name to scan across downloaded court PDFs")
name = st.text_input("Name to search", placeholder="e.g. John Smith")

@st.cache_data(show_spinner=False)
def search_name(name, root='data'):
    hits = []
    for court in os.listdir(root):
        court_path = os.path.join(root, court)
        if not os.path.isdir(court_path):
            continue
        for file in os.listdir(court_path):
            if file.endswith('.pdf'):
                file_path = os.path.join(court_path, file)
                try:
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for i, page in enumerate(reader.pages):
                            text = page.extract_text() or ""
                            if name.lower() in text.lower():
                                hits.append((court, file, i + 1))
                except Exception as e:
                    st.error(f"❌ Error reading {file_path}: {e}")
    return hits

def extract_pages(pdf_path, page_numbers):
    output = PyPDF2.PdfWriter()
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in page_numbers:
            try:
                output.add_page(reader.pages[page_num - 1])
            except IndexError:
                st.warning(f"⚠️ Page {page_num} not found in {pdf_path}")
    buffer = io.BytesIO()
    output.write(buffer)
    buffer.seek(0)
    return buffer

def display_pdf_link(file_bytes, filename="preview.pdf"):
    base64_pdf = base64.b64encode(file_bytes.read()).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank">📄 Open preview in new tab</a>'
    st.markdown(href, unsafe_allow_html=True)

# -- Search logic
if name:
    with st.spinner("🕵️‍♂️ Searching... please wait."):
        results = search_name(name)

    if results:
        st.success(f"✅ Found `{name}` in {len(results)} page(s):")

        grouped = {}
        for court, file, page in results:
            key = (court, file)
            grouped.setdefault(key, []).append(page)

        for (court, file), pages in grouped.items():
            st.markdown("---")
            st.markdown(f"#### 📂 `{court}` — `{file}`")
            st.markdown(f"**🧾 Matching Pages:** `{', '.join(map(str, pages))}`")

            pdf_path = os.path.join('data', court, file)
            combined_pdf = extract_pages(pdf_path, pages)

            st.download_button(
                label="⬇️ Download matched pages",
                data=combined_pdf,
                file_name=f"{court}_{file.replace('.pdf', '')}_matches.pdf",
                mime="application/pdf"
            )

            combined_pdf.seek(0)
            display_pdf_link(combined_pdf)

    else:
        st.warning(f"🚫 No matches found for `{name}`.")
else:
    st.info("👈 Enter a name above to start searching.")
