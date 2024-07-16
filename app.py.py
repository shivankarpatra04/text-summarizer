import streamlit as st
from pdfminer.high_level import extract_text
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from collections import Counter
import io

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def extract_text_from_pdf(pdf_file):
    # Extract text using pdfminer
    text = extract_text(pdf_file)
    
    # Join characters that are incorrectly separated
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Insert space between lowercase and uppercase letters
    text = re.sub(r'(?<=[.])(?=[A-Za-z])', ' ', text)  # Insert space after periods if not followed by space
    text = re.sub(r'(?<=[,])(?=[A-Za-z])', ' ', text)  # Insert space after commas if not followed by space
    text = re.sub(r'(?<=\w)(?=\d)', ' ', text)  # Insert space between words and digits
    text = re.sub(r'(?<=\d)(?=\w)', ' ', text)  # Insert space between digits and words
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def summarize(text, num_sentences=25):
    sentences = sent_tokenize(text)
    words = text.lower().split()
    
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and word.isalnum()]
    
    word_freq = Counter(words)
    
    sentence_scores = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            if word in word_freq:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_freq[word]
                else:
                    sentence_scores[sentence] += word_freq[word]
    
    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    
    summary_sentences = [sentence for sentence in sentences if sentence in summary_sentences]
    
    return ' '.join(summary_sentences)

st.title("Text Summarizer")

input_option = st.radio("Choose input method:", ("Text Input", "PDF Upload"))

if input_option == "Text Input":
    full_text = st.text_area("Enter your text here:", height=300)
else:
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        full_text = extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

if st.button("Summarize"):
    if full_text:
        st.write(f"Extracted text length: {len(full_text.split())} words")
        
        summary = summarize(full_text)
        
        st.subheader("Summary:")
        st.write(summary)
        
        st.write(f"Summary length: {len(summary.split())} words")
    else:
        st.warning("Please enter text or upload a PDF file.")