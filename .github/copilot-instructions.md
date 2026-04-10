# Project Guidelines

## Code Style
- Keep changes small and focused in `main.py` unless the app grows into multiple modules.
- Preserve the existing Streamlit-first structure and keep UI logic straightforward.
- Match the file's current tone and formatting; existing inline comments are brief and mostly Romanian.

## Architecture
- This workspace is a single-file Streamlit app that uploads files to Google Drive using a service account.
- The main flow is: user selects files in the UI, the app authenticates with Google Drive, then uploads each file to a configured folder.
- Treat `credentials.json` as a local secret file that must sit next to `main.py`.
- Treat the Drive folder ID placeholder in `main.py` as required configuration before the app can work.

## Build and Test
- Run the app with `streamlit run main.py`.
- There is no separate build step or test suite in the workspace.

## Conventions
- Do not assume the Google Drive credentials or folder ID are valid unless they are explicitly provided.
- Keep upload behavior compatible with both text and binary files.
- If adding documentation, prefer a short README link or a focused note over duplicating setup details here.