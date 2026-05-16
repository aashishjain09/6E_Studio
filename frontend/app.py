import streamlit as st
import httpx
from uuid import UUID
import base64
import io

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


def api_delete(path):
    try:
        return httpx.delete(f"{BACKEND_URL}{path}", timeout=15.0)
    except Exception as e:
        return None


# Initialize navigation state
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "view" not in st.session_state:
    st.session_state.view = "projects"  # projects or explore

if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None


def go_home():
    st.session_state.page = "home"
    st.session_state.view = "projects"
    st.session_state.current_project_id = None


def go_new_project():
    st.session_state.page = "new_project"


def go_studio(project_id):
    st.session_state.page = "studio"
    st.session_state.current_project_id = str(project_id)


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
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📂 Open Studio", key=f"studio-{project['id']}"):
                            go_studio(project["id"])
                            raise RerunException()
                    with col2:
                        if st.button("🤖 Generate", key=f"gen-{project['id']}"):
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
                project = r.json()
                st.success("Project created! Opening studio...")
                go_studio(project["id"])
                raise RerunException()
            else:
                st.error(f"Failed to create project: {r.text}")

elif st.session_state.page == "studio":
    # Back button
    if st.button("← Back to Projects"):
        go_home()

    project_id = st.session_state.current_project_id
    
    # Fetch the current project
    resp = api_get(f"/projects/{project_id}")
    if resp is None or resp.status_code != 200:
        st.error("Could not load project. Is the backend running?")
    else:
        project = resp.json()
        
        st.header(f"Studio: {project['title']}")
        st.write(f"*{project['message']}*")
        if project.get("channel"):
            st.caption(f"Channel: {project['channel']}")
        
        # Create tabs for different studio sections
        tab1, tab2, tab3, tab4 = st.tabs(["Project Info", "Assets", "AI Tools", "Generated Content"])
        
        with tab1:
            st.subheader("Project Information")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Project ID:** `{project['id']}`")
                st.write(f"**Status:** {project['status']}")
            with col2:
                st.write(f"**Created:** {project['created_at']}")
                if project.get("channel"):
                    st.write(f"**Channel:** {project['channel']}")
            
            st.markdown("---")
            st.subheader("Edit Project Details")
            with st.form("edit_project_form"):
                new_title = st.text_input("Title", value=project['title'])
                new_message = st.text_area("Brief", value=project['message'])
                new_channel = st.text_input("Channel", value=project.get('channel', ''))
                if st.form_submit_button("Update Project"):
                    st.info("✨ Project update coming soon! (backend endpoint needed)")
        
        with tab2:
            st.subheader("Project Assets")
            st.write("Manage images, documents, and media files for this project.")
            
            # Upload new asset
            st.markdown("##### Upload New Asset")
            uploaded_file = st.file_uploader("Choose a file", key="asset_upload")
            if uploaded_file is not None:
                # Determine file type
                file_ext = uploaded_file.name.split('.')[-1].lower()
                if file_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    file_type = 'image'
                elif file_ext in ['pdf', 'doc', 'docx', 'txt']:
                    file_type = 'document'
                elif file_ext in ['mp4', 'avi', 'mov']:
                    file_type = 'video'
                else:
                    file_type = 'other'
                
                # Read and encode file
                file_content = uploaded_file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                
                payload = {
                    "filename": uploaded_file.name,
                    "file_type": file_type,
                    "content": encoded_content
                }
                
                if st.button("Upload Asset", key="upload_btn"):
                    upload_resp = api_post(f"/projects/{project_id}/assets", payload)
                    if upload_resp is None:
                        st.error("Upload failed to reach backend.")
                    elif upload_resp.status_code == 200:
                        st.success(f"✅ Asset '{uploaded_file.name}' uploaded!")
                        raise RerunException()
                    else:
                        st.error(f"Upload failed: {upload_resp.text}")
            
            st.markdown("---")
            
            # List existing assets
            st.markdown("##### Existing Assets")
            assets = project.get("assets", [])
            if not assets:
                st.info("No assets yet. Upload one above.")
            else:
                for asset in assets:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"📎 **{asset['name']}** ({asset['file_type']})")
                    with col2:
                        st.caption(asset['created_at'][:10])
                    with col3:
                        if st.button("🗑️", key=f"del-asset-{asset['id']}"):
                            del_resp = api_delete(f"/projects/{project_id}/assets/{asset['id']}")
                            if del_resp is None or del_resp.status_code != 200:
                                st.error("Failed to delete asset.")
                            else:
                                st.success("Asset deleted!")
                                raise RerunException()
        
        with tab3:
            st.subheader("AI Tools & LLM Integration")
            st.write("Tools for generating and enhancing project content using AI.")
            
            st.markdown("##### LLM-Powered Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Generate Assets**")
                if st.button("🤖 Generate Text & Image", key="llm_generate"):
                    with st.spinner("Generating with AI..."):
                        payload = {"project_id": project_id, "prompt": project['message']}
                        gen_resp = api_post("/generate", payload)
                        if gen_resp is None:
                            st.error("Generation failed to reach backend.")
                        elif gen_resp.status_code == 200:
                            st.success("✅ Generation complete!")
                            raise RerunException()
                        else:
                            st.error(f"Generation failed: {gen_resp.text}")
                st.caption("Uses LLM to generate text and image based on brief")
            
            with col2:
                st.markdown("**Content Enhancement**")
                if st.button("✍️ Rewrite with AI", key="llm_rewrite"):
                    st.info("🔄 Rewrite feature - Coming soon! (colleague implementing)")
                st.caption("Improve and refine project message with AI suggestions")
            
            st.markdown("---")
            st.markdown("##### Upcoming LLM Features")
            st.info("""
            - 🎨 **Smart Image Variations**: Generate multiple style variations
            - 📝 **Caption Generator**: Auto-generate captions for assets
            - 🔍 **Sentiment Analysis**: Analyze message tone and audience fit
            - 💡 **Brainstorm Ideas**: Get AI suggestions for creative directions
            - 🌍 **Multi-language**: Translate content to other languages
            """)
        
        with tab4:
            st.subheader("Generated Content")
            
            if project.get("generated_text"):
                st.markdown("##### Generated Text")
                st.write(project["generated_text"])
            else:
                st.info("No generated text yet. Use AI Tools to generate content.")
            
            st.markdown("---")
            
            if project.get("generated_image_url"):
                st.markdown("##### Generated Image")
                st.image(project["generated_image_url"], use_column_width=True)
            else:
                st.info("No generated image yet. Use AI Tools to generate content.")

