import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

# Load the API token
load_dotenv()
hf_token = os.getenv('huggingfacehub_api_token')

# Set up the Streamlit app title
st.set_page_config(page_title='E-Commerce Assistant')
st.sidebar.title('Product Description Generator')
# Initialize the Inference Client
client = InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct", api_key=hf_token)

# Create a sidebar for input fields
st.sidebar.header('Product Details')

# Collect the product details from user input with unique keys
brand_name = st.sidebar.text_input("Brand Name", key="brand_name").strip()
product_name = st.sidebar.text_input("Product Name", key="product_name").strip()
product_category = st.sidebar.text_input('Category', key="product_category").strip()
product_features = st.sidebar.text_area('Key Features', key="product_features").strip()

# Save tone in session state
if 'tone' not in st.session_state:
    st.session_state.tone = 'Professional'

tone = st.sidebar.radio('Choose the tone of description', 
                ('Professional', 'Friendly', 'Concise'), 
                index=('Professional', 'Friendly', 'Concise').index(st.session_state.tone),
                key="tone_choice")

st.session_state.tone = tone

# Max tokens control in sidebar
max_tokens = st.sidebar.slider('Size of text', min_value=100, max_value=1000, value=500, key="max_tokens")

# Initialize session state for storing descriptions and last inputs
if 'descriptions' not in st.session_state:
    st.session_state.descriptions = []
if 'last_inputs' not in st.session_state:
    st.session_state.last_inputs = (None, None, None, None)  # (product_name, product_category, product_features, tone)

# Define the function to create the prompt
def system_prompt_content(product_name, product_category, product_features, tone):
    prompt = f"""
    You are an expert e-commerce product description writer. Generate a {tone} product description using the following structured template:

    1. **Introduction**: Briefly describe the {product_name}, highlighting its main purpose and key selling points. The brand name is {brand_name}
    2. **Key Features**: Provide a list of key features for the {product_name}. Explain each feature clearly, emphasizing how it benefits the user. The features are: {product_features}.
    3. **Benefits**: Expand on why these features matter. Describe how they solve problems or enhance the customer experience. Focus on customer value.
    4. **Call to Action**: End the description with a strong call to action, encouraging the customer to make a purchase or learn more.

    Tailor the description based on the category of the product: {product_category}.
    Keep the tone {tone} as specified. Ensure the description is engaging, informative, and follows a clear structure.
    NOTE: Do not say anything other than description
    """
    return prompt
col1,col2=st.sidebar.columns([0.6,0.2])
with col1:
    generate_clicked=st.button("Generate")
with col2:
    clear_clicked=st.button("Clear")
# Generate description button
if generate_clicked:
    # Check if inputs have changed
    current_inputs = (product_name, product_category, product_features, tone, max_tokens)
    
    if current_inputs != st.session_state.last_inputs:
        if product_name and product_category and product_features:
            with st.spinner("Generating product description..."):
                try:
                    complete_prompt = system_prompt_content(product_name, product_category, product_features, tone)
                    response = client.text_generation(complete_prompt, max_new_tokens=max_tokens)

                    if response and isinstance(response, str):
                        st.session_state.descriptions.append(response)  # Append the new description
                        st.session_state.last_inputs = current_inputs  # Update last inputs
                    else:
                        st.error("Received an invalid response from the model.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all required details")
    else:
        st.warning("No changes detected in input parameters.")

# Clear button to reset all fields and descriptions
if clear_clicked:
    st.session_state.descriptions.clear()  # Clear stored descriptions
    st.session_state.last_inputs = (None, None, None, None)  # Reset last inputs
    # Clear inputs in the sidebar
    st.experimental_rerun()  # Refresh to clear the inputs

# Check if there are any descriptions to display
# Check if there are any descriptions to display
if st.session_state.descriptions:
    st.subheader("Generated Descriptions")
    
    # Reverse the descriptions so the latest one appears first
    total_descriptions = len(st.session_state.descriptions)
    for i, desc in enumerate(st.session_state.descriptions[::-1], 1):
        st.markdown(f"<h3>Description {total_descriptions - i + 1}:</h3>", unsafe_allow_html=True)
        st.write(desc)

 
