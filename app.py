import streamlit as st
import os
import itertools
import csv
from io import StringIO
from pymongo import MongoClient

# --- IMPORTING YOUR CUSTOM BACKEND MODULES ---
from ingestion import extract_text_from_pdf
from preprocessing import clean_and_preprocess
from comparison import calculate_similarity, get_matched_sentences

# --- DATABASE CONNECTION ---
client = MongoClient('mongodb://localhost:27017/')
db = client['plagiarism_db']
results_collection = db['results']

st.set_page_config(page_title="Deep Learning Plagiarism Checker", page_icon="🕵️‍♀️", layout="wide")

# --- INITIALIZE SESSION STATE MEMORY ---
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

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Score Guide")
st.sidebar.info(
    "**Understanding Semantic Similarity:**\n\n"
    "🔴 **100%:** Literal, exact copy-and-paste.\n\n"
    "🟠 **80% - 99%:** Heavy paraphrasing or synonym substitution. Core meaning is identical.\n\n"
    "🟡 **50% - 79%:** Common domain terminology or general topic overlap. Usually independent work.\n\n"
    "🟢 **< 50%:** Completely original phrasing and structure."
)

st.subheader("📂 Document Upload")
uploaded_files = st.file_uploader("Open your assignment folder and select all PDFs (Ctrl+A):", type=['pdf'], accept_multiple_files=True)

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
            raw_docs = {} # NEW: We need to keep the raw text with punctuation for sentence splitting!
            
            for path in saved_paths:
                raw_text = extract_text_from_pdf(path)
                clean_text = clean_and_preprocess(raw_text)
                processed_docs[path] = clean_text 
                raw_docs[path] = raw_text # Store the raw version too
            
            report_data = []
            db_records = []
            ui_elements = [] 
            
            pairs = list(itertools.combinations(saved_paths, 2))
            
            for doc1, doc2 in pairs:
                text1 = processed_docs[doc1]
                text2 = processed_docs[doc2]
                score = calculate_similarity(text1, text2)
                
                name1 = os.path.basename(doc1)
                name2 = os.path.basename(doc2)
                
                if score >= similarity_threshold:
                    status = "FLAGGED"
                    # NEW: Run the sentence-by-sentence matrix!
                    matches = get_matched_sentences(raw_docs[doc1], raw_docs[doc2], similarity_threshold)
                    
                    ui_elements.append({
                        "type": "error",
                        "message": f"🚨 **{status}:** '{name1}' and '{name2}' have a similarity of **{score:.2f}%**",
                        "matches": matches,
                        "doc1_name": name1,
                        "doc2_name": name2
                    })
                else:
                    status = "CLEAR"
                    ui_elements.append({
                        "type": "success",
                        "message": f"✅ **{status}:** '{name1}' and '{name2}' have a similarity of **{score:.2f}%**"
                    })
                
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
            
            st.session_state.report_data = report_data
            st.session_state.ui_elements = ui_elements
            st.session_state.scan_complete = True 

# --- DISPLAY FROM MEMORY ---
if st.session_state.scan_complete:
    st.markdown("---")
    st.subheader("📊 Plagiarism Report")
    
    import pandas as pd
    
    # 1. Separate the results into two lists
    flagged_elements = [el for el in st.session_state.ui_elements if el["type"] == "error"]
    clear_elements = [el for el in st.session_state.ui_elements if el["type"] == "success"]
    
    # 2. Provide a quick summary at the top
    st.info(f"**Analysis Complete:** Found **{len(flagged_elements)}** flagged pairs out of {len(st.session_state.ui_elements)} total comparisons.")
    
    # 3. Create clean UI Tabs
    tab1, tab2 = st.tabs(["🚨 Flagged Matches", "✅ Clear Documents"])
    
    # --- TAB 1: Only show the cheaters ---
    with tab1:
        if not flagged_elements:
            st.success("Great news! No plagiarism detected above the threshold.")
        else:
            for element in flagged_elements:
                st.error(element["message"])
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

    # --- TAB 2: Hide the green banners in an expander so they don't clutter the screen ---
    with tab2:
        if clear_elements:
            with st.expander("View all cleared comparisons"):
                for element in clear_elements:
                    st.success(element["message"])
        else:
            st.info("No cleared documents.")
            
    # The download and clear buttons stay outside the tabs so they are always accessible
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
        st.rerun()