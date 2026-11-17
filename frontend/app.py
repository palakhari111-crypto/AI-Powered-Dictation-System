import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from frontend.services.api_client import api, request

st.set_page_config(page_title="AI Dictation", page_icon="📝", layout="wide")
st.title("📝 AI-Powered Dictation System")
st.caption("Listen. Write. Evaluate. Improve.")

if "token" not in st.session_state: st.session_state.token = None
if "user" not in st.session_state: st.session_state.user = None

def call(method, path, **kwargs):
    return api(method, path, st.session_state.token, **kwargs)

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

if not st.session_state.token:
    login_tab, register_tab = st.tabs(["Login", "Create account"])
    with login_tab:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            try:
                result = api("POST", "/auth/login", json={"email": email, "password": password})
                st.session_state.token, st.session_state.user = result["access_token"], result["user"]
                st.rerun()
            except Exception as e: st.error(str(e))
    with register_tab:
        with st.form("register"):
            name = st.text_input("Full name")
            email = st.text_input("Email address", key="reg_email")
            password = st.text_input("Password (minimum 8 characters)", type="password", key="reg_pass")
            role = st.selectbox("Register as", ["student", "teacher"])
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            try:
                api("POST", "/auth/register", json={"name": name, "email": email, "password": password, "role": role})
                st.success("Account created. Please log in.")
            except Exception as e: st.error(str(e))
    st.stop()

user = st.session_state.user
with st.sidebar:
    st.write(f"**{user['name']}**")
    st.caption(user["role"].title())
    if st.button("Logout", use_container_width=True): logout()

if user["role"] == "teacher":
    st.header("Teacher dashboard")
    t1, t2, t3 = st.tabs(["Classrooms", "Create dictation", "Submissions"])
    with t1:
        try: classrooms = call("GET", "/classrooms")
        except Exception as e: st.error(str(e)); classrooms = []
        with st.form("new_class"):
            name = st.text_input("Classroom name")
            desc = st.text_area("Description")
            create = st.form_submit_button("Create classroom")
        if create:
            try:
                c = call("POST", "/classrooms", json={"name": name, "description": desc})
                st.success(f"Created {c['name']}. Join code: {c['class_code']}")
                st.rerun()
            except Exception as e: st.error(str(e))
        if classrooms:
            st.subheader("Your classrooms")
            for c in classrooms:
                with st.expander(f"{c['name']}  ·  Code: {c['class_code']}"):
                    st.write(c["description"])
                    try:
                        students = call("GET", f"/classrooms/{c['id']}/students")
                        st.write(f"Students: {len(students)}")
                        for s in students: st.write(f"- {s['name']} ({s['email']})")
                    except Exception as e: st.error(str(e))
    with t2:
        try: classrooms = call("GET", "/classrooms")
        except Exception: classrooms = []
        if not classrooms:
            st.info("Create a classroom first.")
        else:
            options = {f"{c['name']} (ID {c['id']})": c["id"] for c in classrooms}
            with st.form("new_dictation"):
                classroom_id = st.selectbox("Classroom", list(options))
                title = st.text_input("Dictation title")
                description = st.text_area("Description")
                text = st.text_area("Verified dictation text", height=180)
                language = st.selectbox("Audio language", ["en", "hi", "fr", "es", "de"])
                difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"])
                replay = st.checkbox("Allow replay", True)
                max_replays = st.number_input("Maximum replays", min_value=0, max_value=20, value=3)
                create = st.form_submit_button("Create and publish")
            if create:
                try:
                    d = call("POST", "/dictations", json={"classroom_id": options[classroom_id], "title": title,
                        "description": description, "text": text, "language": language, "difficulty": difficulty,
                        "allow_replay": replay, "max_replays": int(max_replays)})
                    st.success(f"Dictation created (ID {d['id']}).")
                    if st.button("Generate audio now"):
                        call("POST", f"/dictations/{d['id']}/generate-audio")
                        st.success("Audio generated.")
                except Exception as e: st.error(str(e))
        st.caption("For this MVP, enter or paste verified text. Teacher-image OCR can be added through the same OCR service interface.")
    with t3:
        try: classrooms = call("GET", "/classrooms")
        except Exception: classrooms = []
        if classrooms:
            c = st.selectbox("Choose classroom", classrooms, format_func=lambda x: x["name"], key="report_class")
            try:
                rows = call("GET", f"/attempts/classroom/{c['id']}/summary")
                st.dataframe(rows, use_container_width=True)
            except Exception as e: st.error(str(e))
else:
    st.header("Student dashboard")
    join_tab, dict_tab, report_tab = st.tabs(["Join classroom", "Available dictations", "My reports"])
    with join_tab:
        with st.form("join"):
            code = st.text_input("Classroom join code").upper()
            join = st.form_submit_button("Join classroom")
        if join:
            try:
                result = call("POST", "/classrooms/join", json={"class_code": code})
                st.success(f"Joined {result['name']}")
            except Exception as e: st.error(str(e))
        try:
            st.subheader("My classrooms")
            st.write(call("GET", "/classrooms"))
        except Exception as e: st.error(str(e))
    with dict_tab:
        try: dictations = call("GET", "/dictations")
        except Exception as e: st.error(str(e)); dictations = []
        if not dictations: st.info("No published dictations yet. Join a classroom or ask your teacher to publish one.")
        for d in dictations:
            with st.expander(f"{d['title']} · {d['difficulty']}"):
                st.write(d["description"])
                if d["audio_available"]:
                    try:
                        r = request("GET", f"/dictations/{d['id']}/audio", st.session_state.token)
                        st.audio(r.content, format="audio/mp3")
                    except Exception as e: st.warning(str(e))
                if st.button("Start attempt", key=f"start_{d['id']}"):
                    try:
                        result = call("POST", f"/attempts/start/{d['id']}")
                        st.session_state.active_attempt = result["attempt_id"]
                        st.session_state.active_dictation = d["title"]
                        st.success(f"Attempt started. ID: {result['attempt_id']}")
                    except Exception as e: st.error(str(e))
        if st.session_state.get("active_attempt"):
            st.subheader(f"Submit handwriting · {st.session_state.get('active_dictation')}")
            uploaded = st.file_uploader("Upload a clear JPG or PNG photo of your handwritten page", type=["jpg", "jpeg", "png"])
            if st.button("Submit for evaluation", disabled=uploaded is None):
                try:
                    response = request("POST", f"/attempts/{st.session_state.active_attempt}/submission",
                        st.session_state.token, files={"image": (uploaded.name, uploaded.getvalue(), uploaded.type)})
                    result = response.json()
                    st.session_state.last_result = result
                    st.success("Submission processed.")
                    if result["needs_review"]: st.warning(result["ocr_message"])
                    st.write("Extracted text:", result["extracted_text"] or "No text extracted")
                    if result["evaluation"]: st.metric("Provisional score", f"{result['evaluation']['overall_score']}%")
                    else: st.info("No score generated. OCR needs review.")
                except Exception as e: st.error(str(e))
    with report_tab:
        attempt_id = st.number_input("Attempt ID", min_value=1, step=1)
        if st.button("Load report"):
            try:
                report = call("GET", f"/attempts/{int(attempt_id)}/report")
                st.json(report)
            except Exception as e: st.error(str(e))
