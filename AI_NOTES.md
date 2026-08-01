# AI Usage Notes

I used Claude (Anthropic) to help build this project. Below is a breakdown of
what it generated, what I reviewed/changed and why, and what I chose not to use.

## 1. What was AI-generated vs. written by me

**AI-generated (initial versions):**
- Project scaffolding (`src/models.py`, `src/storage.py`, `src/main.py`, `tests/test_api.py`)
- The FastAPI route definitions and Pydantic models
- The pytest test suite structure and most individual test cases
- README.md structure and wording

**Written / decided by me:**
- I chose to keep FastAPI over Flask since the assignment listed it first and it gives
  free interactive Swagger docs at `/docs`, which covers the optional bonus with no
  extra code.
- I set up the actual dev environment myself (installed Python on Windows, since it
  wasn't installed at all had to enable "Add python.exe to PATH" during install,
  create the venv, activate it).
- When `pip install` failed trying to compile `pydantic-core` from source (my machine
  didn't have a Rust toolchain or the MSVC linker), I decided to relax the pinned
  package versions in `requirements.txt` rather than install Visual Studio Build Tools
  or downgrade Python  since my Python (3.14) was newer than the pinned package
  versions supported, and unpinned versions let pip fetch pre-built wheels instead of
  compiling anything.
- After that, `starlette`'s test client raised an error asking for a package called
  `httpx2` instead of `httpx` I installed it and re-ran the tests rather than
  guessing at a workaround.
- After getting everything working, I ran `pip freeze > requirements.txt` to lock in
  the exact versions that actually work on my machine, so the file reflects reality
  instead of guessed version numbers.

## 2. What I validated, tested, or changed in the AI's output, and why

- Ran `pytest` myself on my own machine  all 13 tests passed.
- Started the server (`uvicorn`) and manually tested **every endpoint** through the
  Swagger UI at `/docs`, not just the automated tests:
  - `POST /expenses`  created two expenses, got back `201` with server-assigned ids
  - `GET /expenses` confirmed both showed up
  - `GET /expenses?category=Travel`  confirmed filtering excluded the other category
  - `GET /expenses/totals` confirmed overall total and per-category totals were
    arithmetically correct (1 + 20 = 21)
  - `DELETE /expenses/1` confirmed `204` on success
  - `DELETE /expenses/1` again confirmed `404` with a clear error message, since
    the assignment implies this should be a real error, not a silent success
- Caught and fixed a real bug during review: the first version of `models.py` named
  a field `date` with type annotation `date` (from `datetime import date`), which
  made Pydantic fail at import time with an `unevaluable-type-annotation` error.
  Fixed by importing the type as `date_type` to avoid the name collision. This
  wasn't something I could've caught just by reading the code it only showed up
  when I actually ran the tests, which is why I made a point of running everything
  myself rather than trusting that AI-generated code works because it looks correct.

## 3. AI suggestions I decided not to use, and why

- The project used an auto-incrementing integer id scheme (never reused after
  delete) rather than UUIDs. I considered switching to UUIDs but decided the
  simpler integer ids were fine here this is a single-process, non-concurrent
  assignment, and small integers are much easier to read and test through curl
  and Swagger than long UUID strings.
- When `pip install` first failed, one option would have been to install Visual
  Studio Build Tools to compile `pydantic-core` from source, which is the "proper"
  fix for that specific error message. I chose the faster route (relaxing version
  pins so pip could fetch a pre-built wheel) since it got a working environment in
  minutes instead of a much larger download/install.

---
*Verified end-to-end on my own machine (Windows, Python 3.14) on 31 July 2026 
environment set up from scratch, dependencies installed, all 13 automated tests
passed, and all 5 endpoints manually exercised through the Swagger UI, including
the delete-then-delete-again 404 case.*