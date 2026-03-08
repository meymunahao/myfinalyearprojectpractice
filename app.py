import streamlit as st
import os
import itertools
import csv
from io import StringIO
from pymongo import MongoClient

from ingestion import extract_text_from_pdf
from preprocessing import clean_and_preprocess
from comparison import calculate_similarity

# --- DATABASE CONNECTION ---
client = MongoClient('mongodb://localhost:27017/')
db = client['plagiarism_db']
results_collection = db['results']

st.set_page_config(page_title="Deep Learning Plagiarism Checker", page_icon="🕵️‍♀️", layout="wide")

# --- INITIALIZE SESSION STATE MEMORY ---
# This checks if we've already run a scan. If not, it sets up empty memory slots.
if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False
    st.session_state.report_data = []
    st.session_state.ui_elements = []

st.title("🕵️‍♀️ Deep Learning Custom Plagiarism Checker")
st.markdown("Upload multiple student submissions to detect semantic similarity and paraphrasing.")

st.sidebar.header("⚙️ Settings")
similarity_threshold = st.sidebar.slider(
    "Plagiarism Threshold (%)", 
    min_value=50, 
    max_value=100, 
    value=80, 
    step=1
)

st.subheader("📂 Document Upload")
# Tweaked the wording here to guide the user on how to upload the "folder" contents
uploaded_files = st.file_uploader("Open your assignment folder and select all PDFs (Ctrl+A):", type=['pdf'], accept_multiple_files=True)

# If the user uploads new files, we want to clear the old memory
if uploaded_files and not st.session_state.scan_complete:
     st.session_state.scan_complete = False

if st.button("🚀 Run Plagiarism Check"):
    if len(uploaded_files) < 2:
        st.warning("Please upload at least TWO documents to compare.")
    else:
        with st.spinner("Analyzing documents using Sentence-BERT..."):
            
            saved_paths = []
            for file in uploaded_files:
                file_path = os.path.join("submissions", file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                saved_paths.append(file_path)
            
            processed_docs = {}
            for path in saved_paths:
                raw_text = extract_text_from_pdf(path)
                clean_text = clean_and_preprocess(raw_text)
                processed_docs[path] = clean_text 
            
            report_data = []
            db_records = []
            ui_elements = [] # We will save the UI text strings here to display later
            
            pairs = list(itertools.combinations(saved_paths, 2))
            
            for doc1, doc2 in pairs:
                text1 = processed_docs[doc1]
                text2 = processed_docs[doc2]
                score = calculate_similarity(text1, text2)
                
                name1 = os.path.basename(doc1)
                name2 = os.path.basename(doc2)
                
                if score >= similarity_threshold:
                    status = "FLAGGED"
                    ui_elements.append(("error", f"🚨 **{status}:** '{name1}' and '{name2}' have a similarity of **{score:.2f}%**"))
                else:
                    status = "CLEAR"
                    ui_elements.append(("success", f"✅ **{status}:** '{name1}' and '{name2}' have a similarity of **{score:.2f}%**"))
                
                report_data.append([name1, name2, f"{score:.2f}%", status])
                db_records.append({
                    "document_1": name1,
                    "document_2": name2,
                    "similarity_score": round(score, 2),
                    "status": status,
                    "threshold_used": similarity_threshold
                })
            
            if db_records:
                results_collection.insert_many(db_records)
                st.sidebar.success("💾 Results permanently saved to MongoDB!")
            
            # --- SAVE EVERYTHING TO MEMORY ---
            st.session_state.report_data = report_data
            st.session_state.ui_elements = ui_elements
            st.session_state.scan_complete = True # Flag that memory is full and ready to display

# --- DISPLAY FROM MEMORY ---
# Because this is outside the button, it will stay on screen even after a rerun!
if st.session_state.scan_complete:
    st.markdown("---")
    st.subheader("📊 Plagiarism Report")
    
    # Print out all the alerts we saved
    for alert_type, message in st.session_state.ui_elements:
        if alert_type == "error":
            st.error(message)
        else:
            st.success(message)
            
    # Generate CSV from memory
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
    
    # Add a button to clear the screen
    if st.button("🔄 Clear Results for New Upload"):
        st.session_state.scan_complete = False
        st.session_state.report_data = []
        st.session_state.ui_elements = []
        st.rerun() # Forces the app to refresh immediately