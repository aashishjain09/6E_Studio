import streamlit as st
import httpx
import base64

BACKEND_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="6E Creative Studio", layout="wide")


# ── API helpers ───────────────────────────────────────────────────────────────

def api_get(path):
    try:
        return httpx.get(f"{BACKEND_URL}{path}", timeout=15.0)
    except Exception:
        return None


def api_post(path, payload):
    try:
        return httpx.post(f"{BACKEND_URL}{path}", json=payload, timeout=30.0)
    except Exception:
        return None


def api_patch(path, payload):
    try:
        return httpx.patch(f"{BACKEND_URL}{path}", json=payload, timeout=15.0)
    except Exception:
        return None


def api_delete(path):
    try:
        return httpx.delete(f"{BACKEND_URL}{path}", timeout=15.0)
    except Exception:
        return None


# ── Navigation state ──────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "view" not in st.session_state:
    st.session_state.view = "projects"
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


# ── Sidepane renderers ────────────────────────────────────────────────────────
# Each renderer:
#   - Draws its own controls inside the left column
#   - Shows a Save Details button that PATCHes project metadata
#   - Returns (text_prompt, image_prompt) used by the Generate button

def _save_meta(pid, metadata):
    r = api_patch(f"/projects/{pid}", {"metadata": metadata})
    if r and r.status_code == 200:
        st.success("✅ Saved")
    else:
        st.error("Save failed — is the backend running?")


# ── 2.1 Social ────────────────────────────────────────────────────────────────
def sidepane_social(pid, project):
    meta = project.get("metadata") or {}
    st.markdown("#### 📱 Social Campaign")

    PLATFORMS = ["Instagram", "Twitter / X", "LinkedIn", "Facebook", "TikTok"]
    TONES     = ["Casual", "Professional", "Urgent", "Inspirational", "Humorous"]

    platform   = st.selectbox(
        "Platform", PLATFORMS,
        index=PLATFORMS.index(meta.get("platform", "Instagram")),
        key=f"{pid}_platform",
    )
    tone = st.selectbox(
        "Tone", TONES,
        index=TONES.index(meta.get("tone", "Casual")),
        key=f"{pid}_tone",
    )
    audience = st.text_input(
        "Target Audience", value=meta.get("audience", ""),
        placeholder="e.g. working professionals 25–35",
        key=f"{pid}_audience",
    )
    cta = st.text_input(
        "Call to Action", value=meta.get("cta", ""),
        placeholder="e.g. Book now · Learn more",
        key=f"{pid}_cta",
    )
    hashtags = st.text_input(
        "Hashtags", value=meta.get("hashtags", ""),
        placeholder="#brand #campaign",
        key=f"{pid}_hashtags",
    )
    char_limit = st.slider(
        "Character Limit", 50, 500,
        int(meta.get("char_limit", 280)),
        key=f"{pid}_char_limit",
    )

    if st.button("💾 Save Details", key=f"{pid}_save", width="stretch"):
        _save_meta(pid, dict(platform=platform, tone=tone, audience=audience,
                             cta=cta, hashtags=hashtags, char_limit=char_limit))

    text_prompt = (
        f"Write a {platform} post in a {tone} tone.\n"
        f"Campaign brief: {project['message']}\n"
        f"Target audience: {audience}.\n"
        f"CTA: '{cta}'. Keep it under {char_limit} characters. "
        f"Include hashtags: {hashtags}."
    )
    image_prompt = (
        f"{tone} social media campaign image for {platform}. "
        f"Subject: {project['message']}. "
        f"Professional, eye-catching, platform-native aesthetic."
    )
    return text_prompt, image_prompt


# ── 2.2 Copywriting ───────────────────────────────────────────────────────────
def sidepane_copywriting(pid, project):
    meta = project.get("metadata") or {}
    st.markdown("#### ✍️ Copywriting")

    CONTENT_TYPES = [
        "Blog Post", "Email Newsletter", "Ad Copy",
        "Product Description", "Press Release", "Social Caption",
    ]
    TONES = ["Professional", "Conversational", "Persuasive",
             "Informative", "Storytelling"]

    content_type = st.selectbox(
        "Content Type", CONTENT_TYPES,
        index=CONTENT_TYPES.index(meta.get("content_type", "Blog Post")),
        key=f"{pid}_content_type",
    )
    tone = st.selectbox(
        "Tone", TONES,
        index=TONES.index(meta.get("tone", "Professional")),
        key=f"{pid}_tone",
    )
    audience = st.text_input(
        "Target Audience", value=meta.get("audience", ""),
        placeholder="e.g. small business owners",
        key=f"{pid}_audience",
    )
    word_count = st.slider(
        "Target Word Count", 100, 2000,
        int(meta.get("word_count", 500)), step=50,
        key=f"{pid}_word_count",
    )
    key_messages = st.text_area(
        "Key Messages (one per line)", value=meta.get("key_messages", ""),
        placeholder="• Reliable\n• Affordable\n• Fast",
        height=90, key=f"{pid}_key_messages",
    )
    seo_keywords = st.text_input(
        "SEO Keywords", value=meta.get("seo_keywords", ""),
        placeholder="comma-separated",
        key=f"{pid}_seo_keywords",
    )

    if st.button("💾 Save Details", key=f"{pid}_save", width="stretch"):
        _save_meta(pid, dict(content_type=content_type, tone=tone,
                             audience=audience, word_count=word_count,
                             key_messages=key_messages, seo_keywords=seo_keywords))

    text_prompt = (
        f"Write a {content_type} in a {tone} tone.\n"
        f"Brief: {project['message']}\n"
        f"Target audience: {audience}. Target word count: ~{word_count}.\n"
        f"Key messages: {key_messages}.\n"
        f"SEO keywords to include: {seo_keywords}."
    )
    image_prompt = (
        f"Professional featured image for a {content_type} "
        f"about: {project['message']}. Clean, editorial style."
    )
    return text_prompt, image_prompt


# ── 2.3 Banner ────────────────────────────────────────────────────────────────
def sidepane_banner(pid, project):
    meta = project.get("metadata") or {}
    st.markdown("#### 🖼️ Banner")

    SIZES = [
        "728×90  Leaderboard", "300×250  Medium Rectangle",
        "160×600  Wide Skyscraper", "320×50  Mobile Banner",
        "1200×628  Social OG", "Custom",
    ]
    BG_STYLES = [
        "Solid Colour", "Gradient", "Image Background",
        "Minimal White", "Dark Premium",
    ]

    size = st.selectbox(
        "Banner Size", SIZES,
        index=SIZES.index(meta.get("size", "300×250  Medium Rectangle")),
        key=f"{pid}_size",
    )
    headline = st.text_input(
        "Headline", value=meta.get("headline", ""),
        placeholder="Main attention-grabbing text",
        key=f"{pid}_headline",
    )
    subheadline = st.text_input(
        "Subheadline", value=meta.get("subheadline", ""),
        placeholder="Supporting line",
        key=f"{pid}_subheadline",
    )
    cta_text = st.text_input(
        "CTA Button Text", value=meta.get("cta_text", ""),
        placeholder="Book Now · Shop Now · Learn More",
        key=f"{pid}_cta_text",
    )
    bg_style = st.selectbox(
        "Background Style", BG_STYLES,
        index=BG_STYLES.index(meta.get("bg_style", "Solid Colour")),
        key=f"{pid}_bg_style",
    )
    primary_col = st.color_picker(
        "Primary Colour",
        value=meta.get("primary_colour", "#1E3A8A"),
        key=f"{pid}_primary_colour",
    )

    if st.button("💾 Save Details", key=f"{pid}_save", width="stretch"):
        _save_meta(pid, dict(size=size, headline=headline, subheadline=subheadline,
                             cta_text=cta_text, bg_style=bg_style,
                             primary_colour=primary_col))

    text_prompt = (
        f"Write banner ad copy. Size: {size}. "
        f"Headline: '{headline}'. Subheadline: '{subheadline}'. CTA: '{cta_text}'. "
        f"Background: {bg_style}. Brief: {project['message']}."
    )
    image_prompt = (
        f"Digital banner advertisement, {size} format, "
        f"{bg_style} background in primary colour {primary_col}. "
        f"Headline: '{headline}'. Modern brand-safe design. "
        f"Brief: {project['message']}."
    )
    return text_prompt, image_prompt


# ── 2.4 Image Edit ────────────────────────────────────────────────────────────
def sidepane_image_edit(pid, project):
    meta = project.get("metadata") or {}
    st.markdown("#### 🎨 Image Edit")

    EDIT_TYPES = [
        "Remove Background", "Enhance Quality", "Colour Grading",
        "Add Text Overlay", "Style Transfer", "Retouch & Clean",
    ]
    STYLES = [
        "None", "Cinematic", "Vintage", "Clean & Minimal",
        "Bold & Vibrant", "Muted & Moody",
    ]

    edit_type = st.selectbox(
        "Edit Type", EDIT_TYPES,
        index=EDIT_TYPES.index(meta.get("edit_type", "Enhance Quality")),
        key=f"{pid}_edit_type",
    )
    instructions = st.text_area(
        "Edit Instructions", value=meta.get("instructions", ""),
        placeholder="Describe exactly what should change…",
        height=100, key=f"{pid}_instructions",
    )
    intensity = st.slider(
        "Edit Intensity", 1, 10,
        int(meta.get("intensity", 5)),
        key=f"{pid}_intensity",
    )
    style_ref = st.selectbox(
        "Style Reference", STYLES,
        index=STYLES.index(meta.get("style_ref", "None")),
        key=f"{pid}_style_ref",
    )

    st.markdown("---")
    st.markdown("##### 📤 Source Image")
    uploaded = st.file_uploader(
        "Upload source image",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"{pid}_src_img",
    )
    if uploaded:
        st.image(uploaded, caption="Source image", width="stretch")

    if st.button("💾 Save Details", key=f"{pid}_save", width="stretch"):
        _save_meta(pid, dict(edit_type=edit_type, instructions=instructions,
                             intensity=intensity, style_ref=style_ref))

    text_prompt = (
        f"Image editing task — {edit_type}.\n"
        f"Instructions: {instructions}.\n"
        f"Intensity: {intensity}/10. Style reference: {style_ref}."
    )
    image_prompt = (
        f"{edit_type} applied to an image. Instructions: {instructions}. "
        f"Style: {style_ref}. Intensity {intensity}/10. "
        f"Brief: {project['message']}."
    )
    return text_prompt, image_prompt


# ── 2.5 Image Generation ──────────────────────────────────────────────────────
def sidepane_image_generation(pid, project):
    meta = project.get("metadata") or {}
    st.markdown("#### 🖼️ Image Generation")

    STYLES  = [
        "Photorealistic", "Illustration", "Oil Painting", "Watercolour",
        "Digital Art", "Anime / Manga", "Minimalist", "Cinematic",
    ]
    MOODS   = [
        "Bright & Uplifting", "Dark & Moody", "Warm & Cozy",
        "Cold & Professional", "Dramatic", "Ethereal & Dreamy",
    ]
    RATIOS  = [
        "1:1  Square", "16:9  Landscape", "9:16  Portrait", "4:3  Standard",
    ]
    QUALITY = ["Draft", "Standard", "High", "Ultra"]

    style = st.selectbox(
        "Art Style", STYLES,
        index=STYLES.index(meta.get("style", "Photorealistic")),
        key=f"{pid}_art_style",
    )
    mood = st.selectbox(
        "Mood / Atmosphere", MOODS,
        index=MOODS.index(meta.get("mood", "Bright & Uplifting")),
        key=f"{pid}_mood",
    )
    ratio = st.selectbox(
        "Aspect Ratio", RATIOS,
        index=RATIOS.index(meta.get("ratio", "1:1  Square")),
        key=f"{pid}_ratio",
    )
    colours = st.text_input(
        "Colour Palette", value=meta.get("colours", ""),
        placeholder="e.g. navy blue, gold, white",
        key=f"{pid}_colours",
    )
    neg_prompt = st.text_area(
        "Negative Prompt (avoid)", value=meta.get("neg_prompt", ""),
        placeholder="blur, watermark, low quality, text…",
        height=68, key=f"{pid}_neg_prompt",
    )
    quality = st.select_slider(
        "Quality", QUALITY,
        value=meta.get("quality", "Standard"),
        key=f"{pid}_quality",
    )

    if st.button("💾 Save Details", key=f"{pid}_save", width="stretch"):
        _save_meta(pid, dict(style=style, mood=mood, ratio=ratio,
                             colours=colours, neg_prompt=neg_prompt, quality=quality))

    text_prompt = (
        f"Image generation brief: {project['message']}.\n"
        f"Style: {style}. Mood: {mood}. Aspect ratio: {ratio}.\n"
        f"Colour palette: {colours}. Quality: {quality}."
    )
    image_prompt = (
        f"{project['message']}. Art style: {style}. Mood: {mood}. "
        f"Colours: {colours}. Aspect ratio: {ratio}. "
        f"Negative prompt: {neg_prompt}."
    )
    return text_prompt, image_prompt


# ── Dispatch table and metadata ───────────────────────────────────────────────

SIDEPANE_RENDERERS = {
    "Social":           sidepane_social,
    "Copywriting":      sidepane_copywriting,
    "Banner":           sidepane_banner,
    "Image Edit":       sidepane_image_edit,
    "Image Generation": sidepane_image_generation,
}

TYPE_ICONS = {
    "Social":           "📱",
    "Copywriting":      "✍️",
    "Banner":           "🖼️",
    "Image Edit":       "🎨",
    "Image Generation": "✨",
}

STATUS_BADGE = {
    "draft":     "🟡 Draft",
    "generated": "🟢 Generated",
}


# ── Pages ─────────────────────────────────────────────────────────────────────

st.title("6E Creative Studio")

# ─────────────────────────────────────────────────────────────────────────────
# Landing
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    st.markdown("# Welcome to 6E Creative Studio")
    st.write("Quick prototype: click Log In to open the studio home.")
    if st.button("Log In"):
        go_home()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Home — project grid + explore
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "home":
    cols = st.columns([0.2, 1, 0.2])
    with cols[1]:
        nav = st.radio(
            "", ["Projects", "Explore"],
            index=0 if st.session_state.view == "projects" else 1,
            horizontal=True,
        )
        st.session_state.view = nav.lower()

    if st.session_state.view == "projects":
        st.header("Projects")

        resp = api_get("/projects")
        projects = []
        if resp is None or resp.status_code != 200:
            st.error("Could not load projects. Is the backend running?")
        else:
            projects = resp.json()

        st.markdown("---")
        if st.button("+ New Project", key="new_project_btn"):
            go_new_project()
            st.rerun()
        st.markdown("---")

        if not projects:
            st.info("No projects yet. Click New Project to create one.")
        else:
            grid = st.columns(3)
            for idx, project in enumerate(projects):
                ptype = project.get("project_type") or "Social"
                icon  = TYPE_ICONS.get(ptype, "📁")
                with grid[idx % 3]:
                    st.markdown(f"**{icon} {project['title']}**")
                    st.caption(f"{ptype} · {project['status']}")
                    preview = project["message"]
                    st.write(preview[:80] + ("…" if len(preview) > 80 else ""))
                    if project.get("generated_image_url"):
                        st.image(project["generated_image_url"],
                                 width="stretch")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("📂 Open", key=f"open-{project['id']}"):
                            go_studio(project["id"])
                            st.rerun()
                    with c2:
                        if st.button("🤖 Generate", key=f"gen-{project['id']}"):
                            payload = {"project_id": project["id"],
                                       "prompt": project["message"]}
                            gen = api_post("/generate", payload)
                            if gen is None:
                                st.error("Backend unreachable.")
                            elif gen.status_code == 200:
                                st.rerun()
                            else:
                                st.error(f"Failed: {gen.text}")
                    st.markdown("---")

    else:  # Explore
        st.header("Explore")
        resp = api_get("/explore")
        items = []
        if resp is None or resp.status_code != 200:
            st.error("Could not load explore data.")
        else:
            items = resp.json()

        if not items:
            st.info("No generated images yet.")
        else:
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i % 4]:
                    if item.get("generated_image_url"):
                        st.image(item["generated_image_url"],
                                 width="stretch")
                        st.caption(item["title"])

    st.sidebar.button("Log out", on_click=logout)

# ─────────────────────────────────────────────────────────────────────────────
# New Project
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "new_project":
    st.header("Create New Project")
    st.write("Fill in the details below, then open the studio to build it out.")

    with st.form("new_project_form"):
        title   = st.text_input("Project Title")
        message = st.text_area("Creative Brief / Campaign Message")
        channel = st.text_input("Channel / Audience (optional)")
        ptype   = st.selectbox(
            "Project Type",
            ["Social", "Copywriting", "Banner", "Image Edit", "Image Generation"],
        )
        submit = st.form_submit_button("Create Project")

    if submit:
        if not title.strip() or not message.strip():
            st.error("Title and creative brief are required.")
        else:
            payload = {"title": title, "message": message,
                       "channel": channel, "project_type": ptype}
            r = api_post("/projects", payload)
            if r is None:
                st.error("Could not reach backend.")
            elif r.status_code == 200:
                project = r.json()
                st.success("Project created! Opening studio…")
                go_studio(project["id"])
                st.rerun()
            else:
                st.error(f"Failed to create project: {r.text}")

# ─────────────────────────────────────────────────────────────────────────────
# Studio — two-column workspace
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "studio":

    # Top bar: back button + project heading + status
    nav_col, title_col, status_col = st.columns([0.08, 0.74, 0.18])
    with nav_col:
        if st.button("← Back"):
            go_home()
            st.rerun()

    project_id = st.session_state.current_project_id
    resp = api_get(f"/projects/{project_id}")

    if resp is None or resp.status_code != 200:
        with title_col:
            st.error("Could not load project. Is the backend running?")
        st.stop()

    project = resp.json()
    ptype   = project.get("project_type") or "Social"
    icon    = TYPE_ICONS.get(ptype, "📁")

    with title_col:
        st.markdown(f"## {icon} {project['title']}")
        ch = project.get("channel") or "No channel"
        st.caption(f"{ptype}  ·  {ch}  ·  Created {project['created_at'][:10]}")

    with status_col:
        badge = STATUS_BADGE.get(project["status"], project["status"])
        st.markdown(f"**{badge}**")

    st.markdown("---")

    # ── Two-column layout ─────────────────────────────────────────────────────
    left_col, right_col = st.columns([1, 2.5], gap="large")

    # ── Left: campaign brief + type-specific controls ─────────────────────────
    with left_col:

        with st.expander("📋 Campaign Brief", expanded=True):
            st.write(project["message"])
            if project.get("channel"):
                st.caption(f"Channel: {project['channel']}")

        st.markdown("---")

        # Dispatch to the correct sidepane renderer
        renderer = SIDEPANE_RENDERERS.get(ptype, sidepane_social)
        text_prompt, image_prompt = renderer(project_id, project)

        st.markdown("---")

        # Primary action — full-width at bottom of left column
        if st.button("🚀 Generate", key="generate_main",
                     type="primary", width="stretch"):
            with st.spinner("Generating content…"):
                payload = {"project_id": project_id, "prompt": text_prompt}
                gen = api_post("/generate", payload)
                if gen is None:
                    st.error("Backend unreachable.")
                elif gen.status_code == 200:
                    st.success("Generation complete!")
                    st.rerun()
                else:
                    st.error(f"Generation failed: {gen.text}")

    # ── Right: Preview / Assets / Info tabs ───────────────────────────────────
    with right_col:
        tab_preview, tab_assets, tab_info = st.tabs(
            ["🎨 Preview", "📁 Assets", "ℹ️ Project Info"]
        )

        # ── Preview ───────────────────────────────────────────────────────────
        with tab_preview:
            has_image = bool(project.get("generated_image_url"))
            has_text  = bool(project.get("generated_text"))

            if not has_image and not has_text:
                # Empty state
                st.markdown(
                    """
                    <div style="text-align:center;padding:80px 20px;color:#888;">
                        <p style="font-size:3rem;">🎨</p>
                        <p style="font-size:1.1rem;">No content generated yet.</p>
                        <p>Fill in the details on the left, then click
                        <strong>🚀 Generate</strong>.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                if has_image:
                    st.image(project["generated_image_url"],
                             caption="Generated image", width="stretch")

                if has_text:
                    st.markdown("---")
                    st.markdown("##### Generated Copy")
                    st.markdown(project["generated_text"])
                    if st.button("📋 Show raw (copy from here)", key="show_raw"):
                        st.code(project["generated_text"], language=None)

                st.markdown("---")
                with st.expander("✏️ Override prompt and re-generate"):
                    custom_prompt = st.text_area(
                        "Custom prompt", value=text_prompt,
                        height=130, key="custom_prompt_override",
                    )
                    if st.button("🔄 Re-generate", key="regen_custom"):
                        with st.spinner("Re-generating…"):
                            payload = {"project_id": project_id,
                                       "prompt": custom_prompt}
                            gen = api_post("/generate", payload)
                            if gen and gen.status_code == 200:
                                st.rerun()
                            else:
                                st.error("Re-generation failed.")

        # ── Assets ────────────────────────────────────────────────────────────
        with tab_assets:
            st.subheader("Project Assets")

            uploaded_file = st.file_uploader("Upload a file", key="asset_upload")
            if uploaded_file is not None:
                ext = uploaded_file.name.split(".")[-1].lower()
                ftype = (
                    "image"    if ext in {"png", "jpg", "jpeg", "gif", "webp"} else
                    "document" if ext in {"pdf", "doc", "docx", "txt"}         else
                    "video"    if ext in {"mp4", "avi", "mov"}                  else
                    "other"
                )
                if st.button("Upload", key="upload_btn"):
                    encoded = base64.b64encode(uploaded_file.read()).decode("utf-8")
                    payload = {"filename": uploaded_file.name,
                               "file_type": ftype, "content": encoded}
                    r = api_post(f"/projects/{project_id}/assets", payload)
                    if r and r.status_code == 200:
                        st.success(f"✅ '{uploaded_file.name}' uploaded!")
                        st.rerun()
                    else:
                        st.error("Upload failed.")

            st.markdown("---")
            assets = project.get("assets", [])
            if not assets:
                st.info("No assets yet. Upload one above.")
            else:
                for asset in assets:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.write(f"📎 **{asset['name']}** ({asset['file_type']})")
                    with c2:
                        st.caption(asset["created_at"][:10])
                    with c3:
                        if st.button("🗑️", key=f"del-{asset['id']}"):
                            r = api_delete(
                                f"/projects/{project_id}/assets/{asset['id']}")
                            if r and r.status_code == 200:
                                st.rerun()
                            else:
                                st.error("Delete failed.")

        # ── Project Info ──────────────────────────────────────────────────────
        with tab_info:
            st.subheader("Project Information")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**ID:** `{project['id']}`")
                st.write(f"**Type:** {ptype}")
                st.write(f"**Status:** {project['status']}")
            with c2:
                st.write(f"**Created:** {project['created_at'][:10]}")
                if project.get("channel"):
                    st.write(f"**Channel:** {project['channel']}")

            st.markdown("---")
            st.subheader("Edit Project Details")
            with st.form("edit_project_form"):
                new_title   = st.text_input("Title",   value=project["title"])
                new_message = st.text_area("Brief",    value=project["message"])
                new_channel = st.text_input("Channel", value=project.get("channel", ""))
                if st.form_submit_button("Update"):
                    r = api_patch(
                        f"/projects/{project_id}",
                        {"title": new_title, "message": new_message,
                         "channel": new_channel},
                    )
                    if r and r.status_code == 200:
                        st.success("Project updated!")
                        st.rerun()
                    else:
                        st.error("Update failed.")