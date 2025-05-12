import os
import PyPDF2

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
                    print(f"Error reading {file}: {e}")
    return hits

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python search.py <name>")
    else:
        name = sys.argv[1]
        results = search_name(name)
        if results:
            print(f"Found '{name}' in the following files:")
            for court, file in results:
                print(f"{court}/{file}")
        else:
            print(f"No matches found for '{name}'.")
