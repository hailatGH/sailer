FROM python:3.13-slim-bullseye

ENV PIPX_BIN_DIR=/root/.local/bin
ENV PATH=${PIPX_BIN_DIR}:${PATH}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y gnupg2 age \
    && apt-key adv --fetch-keys https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y postgresql-client-17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pipx \
    && pipx ensurepath \
    && pipx install poetry

WORKDIR /app

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

ENTRYPOINT ["poetry", "run", "python", "sailer"]