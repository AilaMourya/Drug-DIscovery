import streamlit as st
import pandas as pd
import base64
import pickle

# --- Helper: File download link ---
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# --- Load model and make predictions ---
def build_model(input_data, chembl_ids):
    # Load pre-trained model
    model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))
    
    # Make predictions
    predictions = model.predict(input_data)
    
    # Output
    st.subheader('🔬 Prediction Output')
    results = pd.DataFrame({
        'chembl_id': chembl_ids,
        'pIC50': predictions
    }).sort_values(by='pIC50', ascending=False)

    st.write(results)
    st.markdown(filedownload(results), unsafe_allow_html=True)

# --- Page Title ---
st.markdown("# 💊 Compounds Bioactivity Prediction")

# --- Sidebar: File Upload ---
with st.sidebar.header('📁 Upload Descriptor CSV'):
    uploaded_file = st.sidebar.file_uploader("Upload CSV file with molecular descriptors", type=['csv'])

# --- Main logic ---
if uploaded_file is not None:
    desc = pd.read_csv(uploaded_file)

    st.subheader('📄 Uploaded Descriptor Data')
    st.write(desc)
    st.write(f"Shape: {desc.shape}")

    try:
        # Read descriptor list used in model
        descriptor_list = list(pd.read_csv('descriptor_list.csv').columns)
        
        # Extract required features
        desc_subset = desc[descriptor_list]

        # Display selected subset
        st.subheader('✅ Subset of Descriptors Used by Model')
        st.write(desc_subset)
        st.write(f"Shape: {desc_subset.shape}")

        # Predict
        build_model(desc_subset, chembl_ids=desc.iloc[:, 0])  # assumes first column is chembl_id

    except Exception as e:
        st.error(f"⚠️ Error during processing: {e}")
else:
    st.info("👈 Upload your descriptor CSV file in the sidebar to begin.")

