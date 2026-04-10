import html
import os
import tempfile

import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


st.set_page_config(
    page_title="Upload Hub",
    page_icon="UH",
    layout="wide",
    initial_sidebar_state="collapsed",
)


DRIVE_FOLDER_ID = "1SR5ynLevtLLtkOWtl6mrifIkw9eAbA0M"


def get_drive_instance():
    scope = ["https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    gauth = GoogleAuth()
    gauth.credentials = creds
    return GoogleDrive(gauth)


def format_file_size(size_in_bytes):
    if size_in_bytes is None:
        return "N/A"

    units = ["B", "KB", "MB", "GB"]
    size = float(size_in_bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"

    return f"{size:.1f} {units[unit_index]}"


def render_shell():
    st.markdown(
        """
        <style>
        :root {
            --bg: #07111f;
            --panel: rgba(9, 18, 32, 0.72);
            --panel-strong: rgba(14, 28, 49, 0.92);
            --stroke: rgba(255, 255, 255, 0.1);
            --stroke-strong: rgba(255, 255, 255, 0.18);
            --text: #edf4ff;
            --muted: #97a9c5;
            --accent: #4ef0c2;
            --accent-2: #67a8ff;
            --accent-3: #ffb347;
            --shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
            --radius-xl: 28px;
            --radius-lg: 22px;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(78, 240, 194, 0.18), transparent 25%),
                radial-gradient(circle at top right, rgba(103, 168, 255, 0.16), transparent 28%),
                radial-gradient(circle at bottom left, rgba(255, 179, 71, 0.12), transparent 22%),
                linear-gradient(180deg, #050b14 0%, #07111f 48%, #091626 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 1240px;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"] {
            display: none;
        }

        [data-testid="stFileUploader"] {
            border: 1px dashed rgba(255, 255, 255, 0.18);
            background: linear-gradient(180deg, rgba(13, 24, 42, 0.8), rgba(9, 18, 32, 0.9));
            border-radius: 24px;
            padding: 0.8rem 1rem 1rem;
            box-shadow: var(--shadow);
        }

        [data-testid="stFileUploader"] section {
            border: 0 !important;
            background: transparent !important;
        }

        [data-testid="stFileUploader"] button,
        [data-testid="stButton"] button {
            border: 0;
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
            color: #04101a;
            font-weight: 800;
            border-radius: 999px;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 18px 40px rgba(78, 240, 194, 0.22);
            transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
        }

        [data-testid="stFileUploader"] button:hover,
        [data-testid="stButton"] button:hover {
            transform: translateY(-1px);
            filter: brightness(1.03);
            box-shadow: 0 22px 48px rgba(78, 240, 194, 0.28);
        }

        [data-testid="stButton"] button:disabled {
            background: rgba(255, 255, 255, 0.12);
            color: rgba(255, 255, 255, 0.55);
            box-shadow: none;
        }

        [data-testid="stProgressBar"] {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
        }

        [data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--stroke);
            border-radius: 32px;
            padding: 2rem;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03)),
                var(--panel);
            box-shadow: var(--shadow);
        }

        .hero::before,
        .hero::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            pointer-events: none;
        }

        .hero::before {
            width: 320px;
            height: 320px;
            right: -120px;
            top: -140px;
            background: radial-gradient(circle, rgba(78, 240, 194, 0.28), transparent 65%);
        }

        .hero::after {
            width: 220px;
            height: 220px;
            left: -100px;
            bottom: -110px;
            background: radial-gradient(circle, rgba(103, 168, 255, 0.2), transparent 68%);
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 0.8rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--accent);
            font-weight: 800;
        }

        .eyebrow-dot {
            width: 10px;
            height: 10px;
            border-radius: 999px;
            background: var(--accent);
            box-shadow: 0 0 0 8px rgba(78, 240, 194, 0.12);
        }

        .hero h1 {
            margin: 0.7rem 0 0.5rem;
            font-size: clamp(2.2rem, 4vw, 4.4rem);
            line-height: 0.98;
            letter-spacing: -0.04em;
            color: var(--text);
        }

        .hero p {
            margin: 0;
            max-width: 760px;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.65;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .hero-card {
            border-radius: 22px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            background: rgba(6, 12, 22, 0.45);
            padding: 1rem 1.1rem;
            backdrop-filter: blur(14px);
        }

        .hero-card span {
            display: block;
            color: var(--muted);
            font-size: 0.86rem;
            margin-bottom: 0.35rem;
        }

        .hero-card strong {
            color: var(--text);
            font-size: 1.02rem;
            font-weight: 700;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            color: var(--text);
            margin: 0 0 0.75rem;
        }

        .panel {
            border: 1px solid var(--stroke);
            border-radius: var(--radius-xl);
            background: var(--panel);
            box-shadow: var(--shadow);
            padding: 1.2rem;
        }

        .upload-list {
            display: grid;
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .upload-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            border-radius: 18px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.03);
            padding: 0.9rem 1rem;
        }

        .upload-item .meta {
            min-width: 0;
        }

        .upload-item .meta strong {
            display: block;
            color: var(--text);
            font-size: 0.97rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .upload-item .meta span {
            display: block;
            color: var(--muted);
            font-size: 0.83rem;
            margin-top: 0.22rem;
        }

        .upload-pill {
            flex: 0 0 auto;
            border-radius: 999px;
            padding: 0.35rem 0.8rem;
            background: rgba(78, 240, 194, 0.12);
            color: var(--accent);
            border: 1px solid rgba(78, 240, 194, 0.18);
            font-size: 0.8rem;
            font-weight: 800;
        }

        .hint-box {
            margin-top: 1rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: linear-gradient(135deg, rgba(103, 168, 255, 0.12), rgba(78, 240, 194, 0.08));
            color: var(--text);
            padding: 1rem 1.1rem;
            line-height: 1.55;
        }

        .footer-note {
            color: var(--muted);
            font-size: 0.9rem;
        }

        @media (max-width: 900px) {
            .hero-grid {
                grid-template-columns: 1fr;
            }

            .upload-item {
                align-items: flex-start;
                flex-direction: column;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow"><span class="eyebrow-dot"></span> GPU Pipeline Upload Hub</div>
            <h1>Un singur loc pentru fisierele care pleaca spre Drive.</h1>
            <p>
                Interfata este gandita ca un dashboard curat si premium: incarci fisierele,
                le trimiti catre folderul Drive configurat si lasi backend-ul GPU sa le preia automat.
            </p>
            <div class="hero-grid">
                <div class="hero-card">
                    <span>Flux</span>
                    <strong>Upload rapid, fara pasi inutili</strong>
                </div>
                <div class="hero-card">
                    <span>Stare</span>
                    <strong>Progres vizibil pentru fiecare batch</strong>
                </div>
                <div class="hero-card">
                    <span>Destinatie</span>
                    <strong>Google Drive, folder dedicat</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.components.v1.html(
        """
        <div style="display:none" id="ui-ready"></div>
        <script>
            const marker = document.getElementById('ui-ready');
            if (marker) {
                marker.dataset.ready = 'true';
            }
        </script>
        """,
        height=0,
    )


def render_file_cards(uploaded_files):
    cards = []
    for file in uploaded_files:
        size = getattr(file, "size", None)
        cards.append(
            f"""
            <div class="upload-item">
                <div class="meta">
                    <strong>{html.escape(file.name)}</strong>
                    <span>{html.escape(file.type or 'unknown')} | {format_file_size(size)}</span>
                </div>
                <div class="upload-pill">Pregatit</div>
            </div>
            """
        )

    st.markdown('<div class="upload-list">' + ''.join(cards) + '</div>', unsafe_allow_html=True)


render_shell()

st.markdown('<div class="section-title">Incarca fisiere</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Alege fisierele pentru upload",
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    render_file_cards(uploaded_files)

    st.markdown(
        """
        <div class="hint-box">
            Dupa ce apesi pe buton, fisierele sunt trimise in folderul configurat din Google Drive.
            Daca lipseste credentials.json sau folderul nu este setat corect, uploadul va esua.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Trimite totul pe Drive", use_container_width=True):
        if DRIVE_FOLDER_ID == "ID_UL_FOLDERULUI_TAU_AICI":
            st.error("Seteaza DRIVE_FOLDER_ID in main.py inainte sa folosesti uploadul.")
        else:
            try:
                drive = get_drive_instance()
                progress_bar = st.progress(0)
                status = st.empty()

                for index, file in enumerate(uploaded_files):
                    status.markdown(
                        f"<div class='footer-note'>Se incarca: <strong>{html.escape(file.name)}</strong></div>",
                        unsafe_allow_html=True,
                    )

                    file_data = file.getvalue()
                    temp_file_path = None

                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name

                    try:
                        gfile = drive.CreateFile(
                            {
                                "title": file.name,
                                "parents": [{"id": DRIVE_FOLDER_ID}],
                            }
                        )

                        gfile.SetContentFile(temp_file_path)
                        gfile.Upload()
                        progress_bar.progress((index + 1) / len(uploaded_files))
                    finally:
                        if temp_file_path and os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)

                status.empty()
                st.success(f"Am incarcat {len(uploaded_files)} fisiere.")
            except FileNotFoundError:
                st.error("Nu gasesc credentials.json langa main.py.")
            except Exception as error:
                st.error(f"Eroare la incarcare: {error}")
else:
    st.markdown(
        """
        <div class="panel">
            <div class="section-title">Fluxul tau</div>
            <div class="footer-note">
                Selecteaza unul sau mai multe fisiere. Apoi le poti trimite direct in Google Drive,
                in folderul dedicat pentru pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="hint-box" style="margin-top: 1.2rem;">
        Backend-ul GPU poate citi fisierele imediat ce apar in Drive. Pastreaza folderul de destinatie
        separat si foloseste acelasi service account pentru acces stabil.
    </div>
    """,
    unsafe_allow_html=True,
)