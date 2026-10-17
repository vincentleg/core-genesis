FROM python:3.12-slim
WORKDIR /app
COPY core_genesis ./core_genesis
COPY web ./web
COPY scripts ./scripts
COPY tests ./tests
COPY pricing.json ./pricing.json
COPY budget/ledger.json ./budget/ledger.json
RUN useradd --create-home genesis && mkdir experiments && chown -R genesis:genesis experiments budget
USER genesis
EXPOSE 8080
CMD ["python", "-m", "core_genesis.server", "--host", "0.0.0.0"]
