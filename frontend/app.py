import streamlit as st
import httpx
from uuid import UUID

BACKEND_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="6E Creative Studio", layout="wide")

# Compatibility for Streamlit versions without `st.experimental_rerun`
try:
    from streamlit.runtime.scriptrunner.script_runner import RerunException
except Exception:
    class RerunException(Exception):
        pass

def api_get(path):
    try:
        return httpx.get(f"{BACKEND_URL}{path}", timeout=15.0)
    except Exception as e:
        return None


def api_post(path, payload):
    try:
        return httpx.post(f"{BACKEND_URL}{path}", json=payload, timeout=30.0)
    except Exception as e:
        return None


# Initialize navigation state
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "view" not in st.session_state:
    st.session_state.view = "projects"  # projects or explore


def go_home():
    st.session_state.page = "home"
    st.session_state.view = "projects"


def go_new_project():
    st.session_state.page = "new_project"


def logout():
    st.session_state.page = "landing"


st.title("6E Creative Studio")

if st.session_state.page == "landing":
    st.markdown("# Welcome to 6E Creative Studio")
    st.write("Quick prototype: click Log In to open the studio home.")
    if st.button("Log In"):
        go_home()

elif st.session_state.page == "home":
    # Top navbar (simple)
    cols = st.columns([0.2, 1, 0.2])
    with cols[1]:
        nav = st.radio("", ["Projects", "Explore"], index=0 if st.session_state.view == "projects" else 1, horizontal=True)
        st.session_state.view = nav.lower()

    if st.session_state.view == "projects":
        st.header("Projects")

        # Fetch projects
        resp = api_get("/projects")
        projects = []
        if resp is None or resp.status_code != 200:
            st.error("Could not load projects. Is the backend running?")
        else:
            projects = resp.json()

        # Top row: New Project card
        st.markdown("---")
        cols = st.columns([1, 1, 1])
        with cols[0]:
            st.write(" ")
            if st.button("+ New Project", key="new_project_big"):
                go_new_project()

        st.markdown("---")

        if not projects:
            st.info("No projects yet. Click New Project to create one.")
        else:
            # Render projects in a 3-column grid
            num_cols = 3
            grid_cols = st.columns(num_cols)
            for idx, project in enumerate(projects):
                col = grid_cols[idx % num_cols]
                with col:
                    st.subheader(project["title"])
                    st.write(project["message"])
                    if project.get("channel"):
                        st.caption(f"Channel: {project['channel']}")
                    if project.get("generated_image_url"):
                        st.image(project["generated_image_url"], use_column_width=True)
                    if st.button("Generate assets", key=f"gen-{project['id']}"):
                        payload = {"project_id": project["id"], "prompt": project["message"]}
                        gen = api_post("/generate", payload)
                        if gen is None:
                            st.error("Generation request failed to reach backend.")
                        elif gen.status_code == 200:
                            raise RerunException()
                        else:
                            st.error(f"Generation failed: {gen.text}")

    else:
        # Explore view within home
        st.header("Explore")
        resp = api_get("/explore")
        items = []
        if resp is None or resp.status_code != 200:
            st.error("Could not load explore data. Is the backend running?")
        else:
            items = resp.json()

        if not items:
            st.info("No generated images yet.")
        else:
            # Masonry-like layout: distribute images across 4 columns
            cols_count = 4
            cols = st.columns(cols_count)
            for i, item in enumerate(items):
                target = cols[i % cols_count]
                with target:
                    if item.get("generated_image_url"):
                        target.image(item["generated_image_url"], use_column_width=True)
                    else:
                        target.write("(no image)")

    # small logout button
    st.sidebar.button("Log out", on_click=logout)

elif st.session_state.page == "new_project":
    st.header("Create New Project")
    st.write("Fill in the campaign details below.")

    with st.form("new_project_form"):
        title = st.text_input("Project title")
        message = st.text_area("Creative brief / campaign message")
        channel = st.text_input("Channel / audience (optional)")
        ptype = st.selectbox("Project type", ["Social", "Copywriting", "Banner", "Image Edit", "Image Generation"]) 
        submit = st.form_submit_button("Create")

    if submit:
        if not title.strip() or not message.strip():
            st.error("Title and creative brief are required.")
        else:
            payload = {"title": title, "message": message, "channel": channel}
            r = api_post("/projects", payload)
            if r is None:
                st.error("Could not reach backend to create project.")
            elif r.status_code == 200:
                st.success("Project created.")
                st.session_state.page = "home"
                raise RerunException()
            else:
                st.error(f"Failed to create project: {r.text}")

