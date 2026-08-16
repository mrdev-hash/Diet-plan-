# 🥗 AI Diet Planner (Streamlit + Gemini)

A simple Streamlit app that takes basic user stats (age, weight, height, sex,
goal, activity level, dietary restrictions) and generates a personalized
daily meal plan using the Gemini API.

## 1. Get a Gemini API key
Free key: https://aistudio.google.com/apikey

## 2. Run locally

```bash
git clone <your-repo-url>
cd diet-planner-app
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and paste your real API key

streamlit run app.py
```

If you skip the secrets file, the app will show a password field in the
sidebar where you can paste the key directly (handy for quick local testing).

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: AI diet planner"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

`.gitignore` already excludes your real `secrets.toml`, so your API key
won't be committed by accident.

## 4. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app**, pick this repo, branch `main`, file `app.py`.
3. Before/after deploying, go to **App settings → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```
4. Save — the app redeploys automatically and the key loads from
   `st.secrets`, so users never see or need to enter it.

## Project structure

```
diet-planner-app/
├── app.py                          # Streamlit app
├── requirements.txt                # Dependencies
├── .gitignore                      # Keeps secrets.toml out of git
├── .streamlit/
│   └── secrets.toml.example        # Template — copy to secrets.toml
└── README.md
```

## Notes

- The model is prompted to return structured JSON so the plan renders as
  clean cards/sections rather than raw text.
- Dietary restrictions are respected as a hard constraint in the prompt.
- A fixed disclaimer is shown in the UI itself (not left to the model) so
  it always appears.
