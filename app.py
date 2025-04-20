import streamlit as st
import pandas as pd
import base64
import pickle

# Page config
st.set_page_config(page_title="Bioactivity Predictor", layout="wide")

# Custom CSS
st.markdown("""
<style>
/* Background image */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1581090700227-1e8e1f05c53b");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Transparent cards */
.main > div {
    background-color: rgba(255, 255, 255, 0.92);
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 0 10px rgba(0,0,0,0.15);
}

/* Headings and fonts */
h1, h2, h3 {
    color: #003366;
}
a {
    color: #0044cc;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# File downloader
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">📥 Download Predictions</a>'
    return href

# Model builder
def build_model(input_data, chembl_ids):
    model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))
    predictions = model.predict(input_data)
    
    st.subheader("🔬 Prediction Results")
    results = pd.DataFrame({
        'chembl_id': chembl_ids,
        'pIC50': predictions
    }).sort_values(by='pIC50', ascending=False)

    st.dataframe(results, use_container_width=True)
    st.markdown(filedownload(results), unsafe_allow_html=True)

# Logo + title
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8d/DNA_icon.png", width=80)
with col2:
    st.markdown("<h1 style='padding-top: 0.5rem;'>💊 Molecular Bioactivity Predictor</h1>", unsafe_allow_html=True)

st.markdown("<h4>Upload your molecular descriptors to predict bioactivity (pIC50)</h4>", unsafe_allow_html=True)

# Sidebar upload
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("Upload `.csv` or `.txt` file (precomputed descriptors)", type=['csv', 'txt'])

# Main logic
if uploaded_file is not None:
    # Try reading CSV or TXT
    if uploaded_file.name.endswith('.csv'):
        desc = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.txt'):
        desc = pd.read_csv(uploaded_file, sep='\t')
    else:
        st.error("Unsupported format.")
        st.stop()

    with st.expander("📄 View Uploaded Descriptor Data", expanded=False):
        st.write(desc)
        st.caption(f"Shape: {desc.shape}")

    try:
        # Load model descriptor list
        descriptor_list = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[descriptor_list]

        with st.expander("✅ Model Input Descriptors", expanded=False):
            st.write(desc_subset)
            st.caption(f"Shape: {desc_subset.shape}")

        build_model(desc_subset, chembl_ids=desc.iloc[:, 0])

    except Exception as e:
        st.error(f"Error during processing: {e}")

else:
    st.info("👈 Upload a descriptor file to begin.")

