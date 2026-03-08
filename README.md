# Deep Learning Custom-Based Plagiarism Checker
An advanced plagiarism detection system powered by deep learning. This application analyzes text submissions to identify similarities and potential plagiarism within a student's submissions directory, providing results through an interactive web interface.

## 🚀 Tech Stack
* **Deep Learning Framework:** PyTorch & NLTK
* **Frontend Interface:** Streamlit
* **Database:** MongoDB
* **Language:** Python 3.11

## 📋 Features
* Deep learning text feature extraction and comparison.
* User-friendly web interface for document upload and analysis.
* Secure database storage for user sessions and historical checks.
* Real-time similarity scoring and highlighted results.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```
   git clone [https://github.com/meymunahao/myfinalyearprojectpractice.git]
   cd myfinalyearprojectpractice
2. **Set up a virtual environment (Windows):**
```
python -m venv venv
.\venv\Scripts\activate
```
3. **Install the required dependencies:**
```
pip install -r requirements.txt
```
4. **Environment Variables:**
Create a `.env` file in the root directory and add your MongoDB connection string:
```env
MONGO_URI="your_mongodb_connection_string_here" (currently incomplete)
```

## 💻 Running the Application
To launch the web interface, run the following command in your terminal:
```
streamlit run app.py
```

🧠 Model Architecture Details
1.	**Input Layer:** This deals with handling variable-length sequences with padding and truncation
2.	**Embedding Layer:** Making use of pre-trained BERT tokenizer or GloVe embeddings.
3.	**Core Layers:** Transformer encoders (BERT) or LSTM for sequence processing; addition to Siamese structure. 
4.	**Output Layer:** Compute cosine similarity and output score (binary, whether plagiarized or original) with threshold.
