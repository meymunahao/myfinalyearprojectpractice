import streamlit as st
import os
import itertools
import csv
from io import StringIO
from pymongo import MongoClient
from nltk.tokenize import sent_tokenize
from fpdf import FPDF

from ingestion import extract_any_text
from preprocessing import clean_and_preprocess
from comparison import calculate_similarity, get_matched_sentences

# The PDF Generator
def generate_turnitin_report(doc1_name, doc2_name, score, raw_text, matches):
    """Generates a PDF where plagiarized sentences are colored red."""
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Adding the Report Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Plagiarism Report: {doc1_name}", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 11)
    pdf.cell(0, 10, txt=f"Compared against: {doc2_name}", ln=True, align='C')
    
    # 2. Adding the Score (Coloring it red if it failed the 20% limit)
    pdf.set_font("Arial", 'B', 12)
    if score > 20.0:
        pdf.set_text_color(255, 0, 0) # Red ink
    else:
        pdf.set_text_color(0, 128, 0) # Green ink
    pdf.cell(0, 10, txt=f"Final Similarity Score: {score:.2f}%", ln=True, align='C')
    
    # Resetting the ink to black and adding some spacing
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(10) 
    
    # 3. Writing the actual document text with intext/inline highlighting
    pdf.set_font("Arial", size=11)
    
    # Extracting the flagged sentences from our dictionary for easy checking
    flagged_sentences = [match['doc1_sentence'] for match in matches]
    
    # Breaking the original document into sentences
    all_sentences = sent_tokenize(raw_text)
    
    for sentence in all_sentences:
        if sentence in flagged_sentences:
            pdf.set_text_color(255, 0, 0)
        else:
            pdf.set_text_color(0, 0, 0) 
            
        clean_sentence = sentence.encode('latin-1', 'ignore').decode('latin-1')
        pdf.write(8, clean_sentence + " ")
        
    return pdf.output(dest='S').encode('latin-1')

# Database Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['plagiarism_db']
results_collection = db['results']

st.set_page_config(page_title="Deep Learning Plagiarism Checker", page_icon="🕵️‍♀️", layout="wide")

# Initializing Session State Memory
if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False
    st.session_state.report_data = []
    st.session_state.ui_elements = []
    st.session_state.raw_docs = {} # Added to remember text for the PDF download!

st.title("🕵️‍♀️ Deep Learning Custom Plagiarism Checker")
st.markdown("Upload multiple student submissions to detect semantic similarity and paraphrasing.")


# Sidebar
st.sidebar.header("⚙️ Settings")
similarity_threshold = st.sidebar.slider(
    "Acceptable Plagiarism Limit (%)", 
    min_value=0, 
    max_value=100, 
    value=20, 
    step=1
)

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Score Guide")
st.sidebar.info(
    "**Understanding the Plagiarism Score:**\n\n"
    "🔴 **> 20%:** Flagged. High amount of copied or heavily paraphrased sentences.\n\n"
    "🟢 **<= 20%:** Acceptable. Falls within standard academic limits for quotes and common phrases.\n\n"
    "*(Note: Sentence-level matching requires an 80% semantic similarity to be flagged as a copy)*"
)

st.subheader("📂 Document Upload")
uploaded_files = st.file_uploader(
    "Open your assignment folder and select all files (Ctrl+A):", 
    type=['pdf', 'docx', 'txt'], 
    accept_multiple_files=True
)

if uploaded_files and not st.session_state.scan_complete:
     st.session_state.scan_complete = False

if st.button("🚀 Run Plagiarism Check"):
    if len(uploaded_files) < 2:
        st.warning("Please upload at least TWO documents to compare.")
    else:
        with st.spinner("Analyzing documents using Sentence-BERT..."):
            
            saved_paths = []
            for file in uploaded_files:
                # Make sure the 'submissions' folder exists!
                os.makedirs("submissions", exist_ok=True) 
                
                file_path = os.path.join("submissions", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                saved_paths.append(file_path)
            
            processed_docs = {}
            
            for path in saved_paths:
                raw_text = extract_any_text(path) 
                clean_text = clean_and_preprocess(raw_text)
                processed_docs[path] = clean_text 
                # Save raw text directly to session state so it survives button clicks
                st.session_state.raw_docs[path] = raw_text 
            
            report_data = []
            db_records = []
            ui_elements = [] 
            
            pairs = list(itertools.combinations(saved_paths, 2))
            
            for doc1, doc2 in pairs:
                name1 = os.path.basename(doc1)
                name2 = os.path.basename(doc2)
                
                # 1. Get the raw text to count sentences
                raw_text1 = st.session_state.raw_docs[doc1]
                raw_text2 = st.session_state.raw_docs[doc2]
                
                # 2. Find matching sentences FIRST (Keep the strict 80% threshold for the AI)
                matches = get_matched_sentences(raw_text1, raw_text2, threshold_percentage=80.0)
                
                # 3. Calculate the Turnitin-Style Score
                total_sentences = len(sent_tokenize(raw_text1))
                
                if total_sentences > 0:
                    score = (len(matches) / total_sentences) * 100
                else:
                    score = 0.0
                
                # 4. Compare the new score against the UI slider
                if score > similarity_threshold:
                    status = "FLAGGED"
                    ui_elements.append({
                        "type": "error",
                        "message": f"🚨 **{status}:** '{name1}' has a plagiarism score of **{score:.2f}%** compared to '{name2}'",
                        "matches": matches,
                        "doc1_name": name1,
                        "doc2_name": name2,
                        "score": score  # Save the exact math number for the PDF
                    })
                else:
                    status = "CLEAR"
                    ui_elements.append({
                        "type": "success",
                        "message": f"✅ **{status}:** '{name1}' is within limits at **{score:.2f}%** compared to '{name2}'"
                    })
                
                report_data.append([name1, name2, f"{score:.2f}%", status])
                db_records.append({
                    "document_1": name1,
                    "document_2": name2,
                    "similarity_score": round(score, 2),
                    "status": status,
                    "threshold_used": similarity_threshold
                })
            
            # Save the final results to session state
            st.session_state.report_data = report_data
            st.session_state.ui_elements = ui_elements
            st.session_state.scan_complete = True
            
            # Save to Database
            if db_records:
                results_collection.insert_many(db_records)

# Displaying from memory
if st.session_state.scan_complete:
    st.markdown("---")
    st.subheader("📊 Plagiarism Report")
    
    import pandas as pd
    
    # 1. Separating the results into two lists
    flagged_elements = [el for el in st.session_state.ui_elements if el["type"] == "error"]
    clear_elements = [el for el in st.session_state.ui_elements if el["type"] == "success"]
    
    # 2. Providing a quick summary at the top
    st.info(f"**Analysis Complete:** Found **{len(flagged_elements)}** flagged pairs out of {len(st.session_state.ui_elements)} total comparisons.")
    
    # 3. Create clean UI Tabs
    tab1, tab2 = st.tabs(["🚨 Flagged Matches", "✅ Clear Documents"])
    
    # Only showing those who plagiarized
    with tab1:
        if not flagged_elements:
            st.success("Great news! No plagiarism detected above the threshold.")
        else:
            for element in flagged_elements:
                st.error(element["message"])
                
                # --- NEW: Generate and display the PDF download button ---
                doc1_path = os.path.join("submissions", element['doc1_name'])
                student_raw_text = st.session_state.raw_docs[doc1_path]
                
                pdf_bytes = generate_turnitin_report(
                    doc1_name=element['doc1_name'],
                    doc2_name=element['doc2_name'],
                    score=element['score'],
                    raw_text=student_raw_text,
                    matches=element["matches"]
                )
                
                st.download_button(
                    label=f"📥 Download Turnitin-Style Report for {element['doc1_name']}",
                    data=pdf_bytes,
                    file_name=f"Report_{element['doc1_name']}.pdf",
                    mime="application/pdf",
                    key=f"dl_{element['doc1_name']}_{element['doc2_name']}"
                )
                # ---------------------------------------------------------

                if element.get("matches"):
                    with st.expander(f"🔍 View Matched Sentences between {element['doc1_name']} and {element['doc2_name']}"):
                        table_data = []
                        for match in element["matches"]:
                            table_data.append({
                                "Match %": f"{match['score']:.2f}%",
                                f"Text in {element['doc1_name']}": match['doc1_sentence'],
                                f"Text in {element['doc2_name']}": match['doc2_sentence']
                            })
                        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    # Organizing the cleared documents all to avoid screen cluttering
    with tab2:
        if clear_elements:
            with st.expander("View all cleared comparisons"):
                for element in clear_elements:
                    st.success(element["message"])
        else:
            st.info("No cleared documents.")
            
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Document 1", "Document 2", "Similarity Score", "Status"])
    csv_writer.writerows(st.session_state.report_data)

    st.markdown("---")
    st.download_button(
        label="📥 Download Plagiarism Report (CSV)",
        data=csv_buffer.getvalue(),
        file_name="plagiarism_report.csv",
        mime="text/csv"
    )
    
    if st.button("🔄 Clear Results for New Upload"):
        st.session_state.scan_complete = False
        st.session_state.report_data = []
        st.session_state.ui_elements = []
        st.session_state.raw_docs = {}
        st.rerun()