#!/bin/bash
# This script installs dependencies and runs the Streamlit app.

# Navigate to the script's directory
cd "$(dirname "$0")"

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the Streamlit app
streamlit run streamlit_app.py