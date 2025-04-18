import streamlit as st
import pandas as pd
import base64
import pickle

# --- Page config ---
st.set_page_config(page_title="Bioactivity Prediction", layout="wide")

# --- Custom CSS for background and styling ---
st.markdown("""
    <style>
    /* Background image */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1581090700227-1e8e1f05c53b");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    
    /* Transparent background for containers */
    .main > div {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.15);
    }

    /* File upload styling */
    .css-1y0tads {
        background-color: rgba(255,255,255,0.8);
        border-radius: 10px;
        padding: 1rem;
    }

    /* Heading styling */
    h1, h2, h3 {
        color: #003366;
    }

    /* Download link */
    a {
        font-weight: bold;
        color: #0044cc;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# --- File download link ---
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">📥 Download Predictions</a>'
    return href

# --- Prediction logic ---
def build_model(input_data, chembl_ids):
    model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))
    predictions = model.predict(input_data)
    
    st.subheader('🔬 Prediction Results')
    results = pd.DataFrame({
        'chembl_id': chembl_ids,
        'pIC50': predictions
    }).sort_values(by='pIC50', ascending=False)

    st.write(results)
    st.markdown(filedownload(results), unsafe_allow_html=True)

# --- App title ---
st.markdown("<h1 style='text-align: center;'>💊 Molecular Bioactivity Predictor</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Upload your molecular descriptor CSV to get pIC50 predictions</h4>", unsafe_allow_html=True)

# --- Sidebar Upload ---
with st.sidebar:
    st.header("📁 Upload Your Data")
    uploaded_file = st.file_uploader("Upload .csv or .txt file (with precomputed descriptors)", type=['csv', 'txt'])

# --- Main content logic ---
if uploaded_file is not None:
    # Read the file depending on extension
    if uploaded_file.name.endswith('.csv'):
        desc = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.txt'):
        desc = pd.read_csv(uploaded_file, sep='\t')
    else:
        st.error("Unsupported file format. Please upload a .csv or .txt file.")
        st.stop()

    st.subheader('📄 Uploaded Descriptor Data')
    st.write(desc)
    st.write(f"Shape: {desc.shape}")

    try:
        descriptor_list = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[descriptor_list]

        st.subheader('✅ Descriptors Used by Model')
        st.write(desc_subset)
        st.write(f"Shape: {desc_subset.shape}")

        build_model(desc_subset, chembl_ids=desc.iloc[:, 0])  # assumes first column is chembl_id

    except Exception as e:
        st.error(f"⚠️ Error during processing: {e}")

else:
    st.info("👈 Upload a valid descriptor file to get started.")
