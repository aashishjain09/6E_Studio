import streamlit as st
import httpx

BACKEND_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="6E Creative Studio", layout="wide")

st.title("6E Creative Studio")
st.write("Create campaign posters and image concepts from a creative brief.")

page = st.sidebar.selectbox("Navigate", ["Landing", "Projects", "Explore"])

def api_get(path):
    return httpx.get(f"{BACKEND_URL}{path}", timeout=15.0)

def api_post(path, payload):
    return httpx.post(f"{BACKEND_URL}{path}", json=payload, timeout=30.0)

if page == "Landing":
    st.header("Welcome")
    st.markdown("Use the sidebar to open Projects or Explore.")
    st.info("No authentication is required for this prototype.")
    st.write("This app is built with Streamlit on the frontend and FastAPI on the backend.")

elif page == "Projects":
    st.header("Projects")
    with st.form("project_form"):
        title = st.text_input("Project title")
        message = st.text_area("Creative brief / campaign message")
        channel = st.text_input("Channel / audience (optional)")
        submit = st.form_submit_button("Create project")

    if submit:
        if not title.strip() or not message.strip():
            st.error("Both title and creative brief are required.")
        else:
            response = api_post("/projects", {"title": title, "message": message, "channel": channel})
            if response.status_code == 200:
                st.success("Project created successfully.")
            else:
                st.error(f"Unable to create project: {response.text}")

    st.markdown("---")
    projects_response = api_get("/projects")
    if projects_response.status_code != 200:
        st.error("Could not load projects. Is the backend running?")
    else:
        projects = projects_response.json()
        if not projects:
            st.info("No projects yet. Create a project to begin.")
        for project in projects:
            box = st.container()
            with box:
                st.subheader(project["title"])
                cols = st.columns([3, 1])
                with cols[0]:
                    st.write(project["message"])
                    if project.get("channel"):
                        st.caption(f"Channel: {project['channel']}")
                    if project.get("generated_text"):
                        st.markdown("**Generated copy:**")
                        st.write(project["generated_text"])
                    if project.get("generated_image_url"):
                        st.image(project["generated_image_url"], use_column_width=True)
                with cols[1]:
                    if st.button(f"Generate assets for {project['title']}", key=f"generate-{project['id']}"):
                        payload = {"project_id": project["id"], "prompt": project["message"]}
                        generate_response = api_post("/generate", payload)
                        if generate_response.status_code == 200:
                            st.experimental_rerun()
                        else:
                            st.error(f"Generation failed: {generate_response.text}")

elif page == "Explore":
    st.header("Explore generated output")
    response = api_get("/explore")
    if response.status_code != 200:
        st.error("Could not load explore data. Is the backend running?")
    else:
        items = response.json()
        if not items:
            st.info("No generated items yet. Create and generate a project first.")
        for item in items:
            st.markdown(f"### {item['title']}")
            cols = st.columns([2, 3])
            with cols[0]:
                st.write(item["message"])
                if item.get("generated_text"):
                    st.markdown("**Generated text**")
                    st.write(item["generated_text"])
            with cols[1]:
                if item.get("generated_image_url"):
                    st.image(item["generated_image_url"], caption=item["title"], use_column_width=True)
                else:
                    st.info("No image generated for this project yet.")
