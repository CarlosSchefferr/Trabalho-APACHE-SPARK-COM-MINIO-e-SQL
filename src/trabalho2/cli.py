from __future__ import annotations

import argparse

from .settings import get_settings


def run_extract() -> None:
    from .pipeline import build_spark_session, extract_all_tables_to_landing, stop_safely

    settings = get_settings()
    spark = build_spark_session(settings)
    try:
        tables = extract_all_tables_to_landing(spark, settings)
        print(f"Tabelas exportadas para landing-zone: {', '.join(tables)}")
    finally:
        stop_safely(spark)


def run_convert() -> None:
    from .pipeline import build_spark_session, convert_landing_to_delta, stop_safely

    settings = get_settings()
    spark = build_spark_session(settings)
    try:
        tables = convert_landing_to_delta(spark, settings)
        print(f"Tabelas convertidas para Delta Lake: {', '.join(tables)}")
    finally:
        stop_safely(spark)


def run_dml() -> None:
    from .pipeline import build_spark_session, replay_bronze_dml, stop_safely

    settings = get_settings()
    spark = build_spark_session(settings)
    try:
        operations = replay_bronze_dml(spark, settings)
        print(f"Operações aplicadas na camada bronze: {operations}")
    finally:
        stop_safely(spark)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pipeline do Trabalho 2: PostgreSQL -> MinIO CSV -> Delta Lake"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("extract", help="Extrai todas as tabelas do PostgreSQL para CSV no bucket landing-zone")
    subparsers.add_parser("convert", help="Converte todos os CSVs da landing-zone para Delta Lake no bucket bronze")
    subparsers.add_parser("dml", help="Reproduz operações de insert, update e delete na tabela Delta customers")
    subparsers.add_parser("all", help="Executa extract, convert e dml em sequência")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "extract":
        run_extract()
        return
    if args.command == "convert":
        run_convert()
        return
    if args.command == "dml":
        run_dml()
        return

    run_extract()
    run_convert()
    run_dml()


if __name__ == "__main__":
    main()
