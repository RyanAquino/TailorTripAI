FROM python:3.12-alpine

WORKDIR /api

ENV PYTHONPATH=..

RUN pip install poetry==1.8.3

COPY poetry.lock pyproject.toml ./

RUN poetry install --without dev

COPY api ./

ENTRYPOINT ["poetry", "run", "python", "main.py"]
