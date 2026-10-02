# AI Career Interview Coach

An AI-powered resume analyzer and interview coach built with Streamlit and the Google Gemini API.

## Features

- Analyze a resume and use the results to prepare for interviews.
- Generate interview coaching with Gemini.
- Simple web interface built with Streamlit.

> Update this section to match the exact features currently implemented in `app.py`.

## Requirements

- Python
- A Google Gemini API key

## Getting started

1. Clone the repository and enter its directory:

   ```bash
   git clone https://github.com/Naveen-code-s/ai-career-interview-coach.git
   cd ai-career-interview-coach
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your Gemini API key using the environment variable expected by `app.py`. Keep the key private; do not commit it to Git.

5. Start the app:

   ```bash
   streamlit run app.py
   ```

## Configuration

Check `app.py` for the API key variable name and any other required settings. Store secrets in environment variables or a local secrets file that is excluded from version control.

## Tech stack

- Python
- Streamlit
- Google Gemini API

## Security

Do not upload resumes containing personal information unless you understand how the app and the configured AI provider handle that data. Never commit API keys or other secrets.

## License

No license file is currently documented. Add a `LICENSE` file if you want others to know how they may use, modify, or distribute this project.
