import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
load_dotenv()
hf_token=os.getenv('huggingfacehub_api_token')
client=InferenceClient(model="meta-llama/Llama-3.1-70B-Instruct",api_key=hf_token)

st.title('E-Commerce Assistant')

# Collect the product details from user input
product_name=st.text_input("Product Name")
product_category = st.text_input('Category')
product_features=st.text_area('Key Features')

tone=st.radio('Choose the tone of description',('Professional','Casual','Detailed','Concise'))


if st.button('Generate Description'):
    if product_name and product_category and product_features:
        system_message=f"""You are a helpful AI assistant in E-Commerce that generates {tone.lower()} product descriptions.
        Note: Do not say anything other than the description."""
        user_message=f"""
        Write a {tone.lower()} product description for a {product_name} in the {product_category} category.
        Features: {product_features}
        """
        with st.spinner("Generating product description..."):
            # call the chat completion model
            try:
                # response=client.chat_completion(
                #     messages=[{"role":'system','content':system_message},
                #               {"role":"user","content":user_message}]

                # )
                response=client.text_generation(system_message+user_message, max_new_tokens=1000)
                st.subheader("Description")
                # st.write(response.choices[0].message.content)
                st.write(response)
            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.warning("Please fill in all required details")