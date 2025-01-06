import streamlit as st
import pandas as pd
from gradio_client import Client, handle_file
import os
from PIL import Image

# Initialize Hugging Face API Client
client = Client("m-ric/agent-data-analyst")

# Streamlit App Design
st.title("CSV File Analyzer")
st.write("Upload your CSV file, and we'll analyze it using an AI agent powered by Hugging Face.")

# File Upload Section
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Display file preview
    st.write("Preview of the uploaded file:")
    try:
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
    except Exception as e:
        st.error(f"Error reading the file: {e}")

    # API Interaction Section
    st.write("Send the file for analysis:")
    additional_notes = st.text_area("Additional Notes (Optional)", value="Hello!!")
    analyze_button = st.button("Analyze File")

    if analyze_button:
        with st.spinner("Analyzing..."):
            try:
                # Send the file and additional notes to the API
                result = client.predict(
                    file_input=handle_file(uploaded_file),
                    additional_notes=additional_notes,
                    api_name="/interact_with_agent"
                )

                # Process and Display API Results
                st.success("Analysis Complete!")
                
                # Display textual analysis
                if isinstance(result, list) and 'content' in result[-1]:
                    st.subheader("Analysis Results")
                    st.write(result[-1]['content'])
                
                # Check for any generated plots
                figures_dir = "./figures/"
                if os.path.exists(figures_dir):
                    st.subheader("Generated Figures")
                    for file in os.listdir(figures_dir):
                        if file.endswith(".png"):
                            st.image(Image.open(os.path.join(figures_dir, file)))
            
            except Exception as e:
                st.error(f"Error during analysis: {e}")
