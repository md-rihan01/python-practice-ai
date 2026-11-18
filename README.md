# Python Practice Chapters

A collection of small Python exercises and projects, organized by topic. The notebooks and scripts are intended to be explored in order, from Python fundamentals through databases and web APIs.

## Chapters

| Folder | Topic | Files |
| --- | --- | --- |
| `1_datatypes` | Data types and a student results exercise | `students-result.ipynb` |
| `2_function` | Functions and a chai bill exercise | `chai-bill.ipynb` |
| `3_class` | Classes and objects | `youtubechannel.ipynb` |
| `4_LLM` | Large language model exercises and a Streamlit app | `LLM.ipynb`, `app.py` |
| `5_error-handling` | Error handling practice | `Untitled.ipynb` |
| `6_chatbot-memory` | Chatbot with memory and a Streamlit app | `chatbot.ipynb`, `app.py` |
| `7_file-handiling` | File handling and action-item examples | `main.ipynb`, `meeting.txt` |
| `8_api-calling` | Calling APIs from Python | `api.ipynb` |
| `9_fastapi` | A FastAPI project | `main.py` and `pyproject.toml` |
| `10_database` | Database practice | `database.ipynb` |

## Getting started

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Open the `chapters` folder in your editor or notebook environment.
3. Start with `1_datatypes` and move through the numbered folders. Open `.ipynb` files with Jupyter or VS Code.

Python version and dependencies vary by chapter. For the FastAPI project, open a terminal in `chapters/9_fastapi` and use [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run uvicorn main:app --reload
```

For the Streamlit projects, open a terminal in the relevant folder (`chapters/4_LLM` or `chapters/6_chatbot-memory`), install that folder's requirements, then run its app:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Some LLM exercises and apps require a provider API key. Configure the key locally in an environment file or your shell, following the variable name used by that chapter. Never commit API keys or other secrets.

## Notes

- Each chapter is a small, independent practice project; it may have its own setup requirements.
- `chapters/7_file-handiling` demonstrates reading and writing local files. Run its notebook from that folder so its example file paths resolve as expected.
- Generated data files, such as the database in `10_database`, are included as practice material.
