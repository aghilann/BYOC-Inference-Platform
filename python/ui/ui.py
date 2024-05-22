import streamlit as st
import requests

API_URL = "http://127.0.0.1"  # Update with your actual external IP address

st.set_page_config(
    page_title="ML Model Management",
    page_icon="🧠",
    # layout="wide",
    initial_sidebar_state="expanded",
)

with open('./bg.css') as f:
    css = f.read()

# Inject CSS into Streamlit
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def main():
    st.title("ML Model Management")

    st.sidebar.title("Actions")
    action = st.sidebar.selectbox("Select an action", ["Deploy Model", "Delete Model", "Get Model"])

    if action == "Deploy Model":
        deploy_model()

    elif action == "Delete Model":
        delete_model()

    elif action == "Get Model":
        get_model()


def deploy_model():
    st.subheader("Deploy a New Model")

    model_name = st.text_input("Model Name")
    model_version = st.text_input("Model Version")
    model_image_url = st.text_input("Docker Image URL")
    model_port = st.number_input("Exposed Port", min_value=0, max_value=65535)
    model_min_replicas = st.number_input("Min Replicas", min_value=0, max_value=10, value=1)
    model_max_replicas = st.number_input("Max Replicas", min_value=0, max_value=10, value=5)
    model_description = st.text_area("Description")
    model_author = st.text_input("Author")
    model_tags = st.text_input("Tags (comma-separated)")
    model_dependencies = st.text_area("Dependencies (key-value pairs, one per line)")
    model_framework = st.selectbox("Framework", ["TensorFlow", "PyTorch", "Scikit-Learn", "XGBoost"])
    model_license = st.selectbox("License", ["MIT", "Apache 2.0", "GPLv3", "BSD 3-Clause"])
    model_input_schema = st.text_area("Input Schema")
    model_output_schema = st.text_area("Output Schema")
    model_endpoint = st.text_area("Model Endpoint (e.g /predict)")
    model_hyperparameters = st.text_area("Hyperparameters (key-value pairs, one per line)")
    model_metrics = st.text_area("Metrics (key-value pairs, one per line)")
    model_environment_variables = st.text_area("Environment Variables (key-value pairs, one per line)")

    if st.button("Deploy"):
        tags = [tag.strip() for tag in model_tags.split(",") if tag.strip()]

        dependencies = parse_lines(model_dependencies)
        hyperparameters = parse_lines(model_hyperparameters)
        metrics = parse_lines(model_metrics)
        environment_variables = parse_lines(model_environment_variables)

        payload = {
            "image_url": model_image_url,
            "exposed_port": model_port,
            "name": model_name,
            "version": model_version,
            "min_replicas": model_min_replicas,
            "max_replicas": model_max_replicas,
            "description": model_description,
            "author": model_author,
            "tags": tags,
            "dependencies": dependencies,
            "framework": model_framework,
            "license": model_license,
            "input_schema": model_input_schema,
            "output_schema": model_output_schema,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
            "environment_variables": environment_variables,
            "model_endpoint": model_endpoint,
        }

        response = requests.post(f"{API_URL}/model", json=payload)
        handle_response(response)


def delete_model():
    st.subheader("Delete an Existing Model")

    model_name = st.text_input("Model Name")
    model_version = st.text_input("Model Version")

    if st.button("Delete"):
        response = requests.delete(f"{API_URL}/model/{model_name}/{model_version}")
        handle_response(response)


def get_model():
    st.subheader("Get Model Metadata")

    model_name = st.text_input("Model Name")
    model_version = st.text_input("Model Version")

    if st.button("Get Model"):
        response = requests.get(f"{API_URL}/model/{model_name}/{model_version}")
        handle_response(response)


def parse_lines(input_text):
    result = {}
    if input_text:
        for line in input_text.splitlines():
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result


def handle_response(response):
    if response.status_code == 200:
        st.success("Operation successful!")
        st.json(response.json())
    else:
        st.error(f"Error: {response.status_code} - {response.json().get('detail', 'Unknown error')}")


if __name__ == "__main__":
    main()
