import streamlit as st
import requests


API_URL = "http://0.0.0.0:8000"  # Update with your actual external IP address
def main():
    st.title("ML Model Management")

    st.sidebar.title("Actions")
    action = st.sidebar.selectbox("Select an action", ["Deploy Model", "Delete Model", "Get Model"])

    if action == "Deploy Model":
        st.subheader("Deploy a New Model")

        model_name = st.text_input("Model Name")
        model_version = st.text_input("Model Version")
        model_image_url = st.text_input("Docker Image URL",)
        model_port = st.number_input("Exposed Port", min_value=0, max_value=65535)

        if st.button("Deploy"):
            model = {
                "image_url": model_image_url,
                "exposed_port": model_port,
                "name": model_name,
                "version": model_version,
            }
            response = requests.post(f"{API_URL}/model", json=model)
            if response.status_code == 200:
                st.success("Model deployed successfully!")
                st.json(response.json())
            else:
                st.error(f"Error: {response.status_code} - {response.json()['detail']}")

    elif action == "Delete Model":
        st.subheader("Delete an Existing Model")

        model_name = st.text_input("Model Name")
        model_version = st.text_input("Model Version")

        if st.button("Delete"):
            response = requests.delete(f"{API_URL}/model/{model_name}/{model_version}")
            if response.status_code == 200:
                st.success("Model deleted successfully!")
                st.json(response.json())
            else:
                st.error(f"Error: {response.status_code} - {response.json()['detail']}")

    elif action == "Get Model":
        st.subheader("Get Model Metadata")

        model_name = st.text_input("Model Name")
        model_version = st.text_input("Model Version")

        if st.button("Get Model"):
            response = requests.get(f"{API_URL}/model/{model_name}/{model_version}")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error(f"Error: {response.status_code} - {response.json()['detail']}")


if __name__ == "__main__":
    main()