# Data pipeline for text sentiment classification

The initial plan for this project is to solve the architectural puzzle required to ingest, classify, warehouse, and visualize reddit comment sentiment

## Initial setup

- Local environment setup
  - install `requirements.txt`
  - run tests `pytest -s -v`
- Reddit API Auth 
  - rename `praw.ini.template` to `praw.ini`
  - create a Reddit API Key
  - update `praw.ini`