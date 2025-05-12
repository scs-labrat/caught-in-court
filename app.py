import streamlit as st
import os
import PyPDF2

st.set_page_config(page_title="Court Appearance Search", layout="wide")

st.title("🔍 QLD Court Attendance Search")
st.markdown("Enter a name to search across all daily law list PDFs.")

query = st.text_input("Search for a name", placeholder="e.g. John Smith")

def search_name(name, root='data'):
    hits = []
    for court in os.listdir(root):
        court_path = os.path.join(root, court)
        if not os.path.isdir(court_path):
            continue
        for file in os.listdir(court_path):
            if file.endswith('.pdf'):
                try:
                    with open(os.path.join(court_path, file), 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = " ".join(page.extract_text() or "" for page in reader.pages)
                        if name.lower() in text.lower():
                            hits.append((court, file))
                except Exception as e:
                    st.error(f"Error reading {file}: {e}")
    return hits

if query:
    with st.spinner("Searching..."):
        results = search_name(query)
    if results:
        st.success(f"Found {len(results)} result(s) for **{query}**:")
        for court, file in sorted(results):
            st.markdown(f"- **{court}**: `{file}`")
    else:
        st.warning(f"No results found for **{query}**.")
