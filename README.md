# Trabalho 2 - Apache Spark com MinIO e Delta Lake

Este repositório implementa o **Trabalho 2** como um projeto independente do trabalho 1.
A solução utiliza um **banco relacional PostgreSQL**, exporta **todas as tabelas** para o bucket
`landing-zone` em **CSV**, converte os arquivos para **Delta Lake** no bucket `bronze` e, por fim,
reproduz operações de **insert**, **update** e **delete** em uma tabela Delta.

## Arquitetura

```text
PostgreSQL -> MinIO landing-zone (CSV) -> MinIO bronze (Delta Lake) -> DML na camada bronze
```

## Estrutura do projeto

```text
.
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── .python-version
├── mkdocs.yml
├── docs/
│   └── index.md
├── sql/
│   └── init/
│       └── 01_schema.sql
├── src/
│   └── trabalho2/
│       ├── __init__.py
│       ├── cli.py
│       ├── pipeline.py
│       └── settings.py
└── tests/
    └── test_settings.py
```

## O que foi implementado

1. **Extração de todas as tabelas relacionais** do PostgreSQL (`customers`, `products`, `orders`).
2. **Gravação em CSV** no bucket `landing-zone` do MinIO.
3. **Leitura dos CSVs** da `landing-zone` e **conversão para Delta Lake** no bucket `bronze`.
4. **Reprodução de DML** na tabela Delta `customers` com:
   - `insert` de um novo cliente;
   - `update` do cliente `id = 1`;
   - `delete` do cliente `id = 2`.
5. **README e MKDOCS** próprios deste repositório, conforme solicitado.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.11
- Java 11 ou superior

## Configuração do ambiente

1. Copie as variáveis de ambiente:

   ```bash
   cp /home/runner/work/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL/.env.example /home/runner/work/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL/.env
   ```

2. Suba PostgreSQL + MinIO + criação dos buckets:

   ```bash
   cd /home/runner/work/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL/Trabalho-APACHE-SPARK-COM-MINIO-e-SQL
   docker compose up -d
   ```

3. Instale as dependências Python:

   ```bash
   pip install -e .
   ```

## Execução

Execute os comandos abaixo na raiz do repositório:

```bash
python -m trabalho2.cli extract
python -m trabalho2.cli convert
python -m trabalho2.cli dml
```

Ou execute tudo em sequência:

```bash
python -m trabalho2.cli all
```

## Resultado esperado

- O bucket **`landing-zone`** conterá uma pasta CSV para cada tabela do PostgreSQL.
- O bucket **`bronze`** conterá uma tabela Delta para cada tabela extraída.
- A tabela Delta `customers` refletirá as operações de `insert`, `update` e `delete`.

## Documentação MkDocs

```bash
mkdocs serve
```

## Validação local usada neste repositório

```bash
PYTHONPATH=src python -m unittest discover -s tests
python -m compileall src tests
```
