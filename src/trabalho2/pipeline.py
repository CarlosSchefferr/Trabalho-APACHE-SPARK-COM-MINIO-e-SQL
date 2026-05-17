from __future__ import annotations

import boto3
from delta import configure_spark_with_delta_pip
from delta.tables import DeltaTable

from .settings import Settings

JDBC_DRIVER = "org.postgresql.Driver"
TABLES_QUERY = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name
""".strip()


def build_spark_session(settings: Settings):
    from pyspark.sql import SparkSession

    builder = (
        SparkSession.builder.appName(settings.spark_app_name)
        .master("local[*]")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3,org.apache.hadoop:hadoop-aws:3.3.4")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.hadoop.fs.s3a.endpoint", settings.minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", settings.minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", settings.minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", settings.minio_endpoint.startswith("https"))
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


def minio_client(settings: Settings):
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        region_name=settings.minio_region,
    )


def ensure_bucket(client, bucket_name: str) -> None:
    buckets = {bucket["Name"] for bucket in client.list_buckets().get("Buckets", [])}
    if bucket_name not in buckets:
        client.create_bucket(Bucket=bucket_name)


def list_tables(spark, settings: Settings) -> list[str]:
    table_frame = (
        spark.read.format("jdbc")
        .option("url", settings.jdbc_url)
        .option("query", TABLES_QUERY)
        .option("user", settings.postgres_user)
        .option("password", settings.postgres_password)
        .option("driver", JDBC_DRIVER)
        .load()
    )
    return [row.table_name for row in table_frame.collect()]


def extract_all_tables_to_landing(spark, settings: Settings) -> list[str]:
    client = minio_client(settings)
    ensure_bucket(client, settings.landing_bucket)

    exported_tables: list[str] = []
    for table_name in list_tables(spark, settings):
        (
            spark.read.format("jdbc")
            .option("url", settings.jdbc_url)
            .option("dbtable", table_name)
            .option("user", settings.postgres_user)
            .option("password", settings.postgres_password)
            .option("driver", JDBC_DRIVER)
            .load()
            .coalesce(1)
            .write.mode("overwrite")
            .option("header", "true")
            .csv(f"s3a://{settings.landing_bucket}/{table_name}")
        )
        exported_tables.append(table_name)

    return exported_tables


def list_landing_tables(client, bucket_name: str) -> list[str]:
    paginator = client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Delimiter="/")
    tables: list[str] = []
    for page in pages:
        for prefix in page.get("CommonPrefixes", []):
            tables.append(prefix["Prefix"].rstrip("/"))
    return sorted(tables)


def convert_landing_to_delta(spark, settings: Settings) -> list[str]:
    client = minio_client(settings)
    ensure_bucket(client, settings.bronze_bucket)

    converted_tables: list[str] = []
    for table_name in list_landing_tables(client, settings.landing_bucket):
        (
            spark.read.option("header", "true")
            .csv(f"s3a://{settings.landing_bucket}/{table_name}")
            .write.format("delta")
            .mode("overwrite")
            .save(f"s3a://{settings.bronze_bucket}/{table_name}")
        )
        converted_tables.append(table_name)

    return converted_tables


def replay_bronze_customer_dml(spark, settings: Settings) -> dict[str, str]:
    bronze_path = f"s3a://{settings.bronze_bucket}/customers"
    schema = "id INT, name STRING, city STRING, status STRING"
    delta_table = DeltaTable.forPath(spark, bronze_path)

    spark.createDataFrame(
        [(999, "Novo Cliente", "Curitiba", "active")],
        schema=schema,
    ).write.format("delta").mode("append").save(bronze_path)

    delta_table.update(
        condition="id = 1",
        set={"city": "'Porto Alegre'", "status": "'vip'"},
    )
    delta_table.delete("id = 2")

    return {
        "insert": "id = 999",
        "update": "id = 1",
        "delete": "id = 2",
    }


def stop_safely(spark) -> None:
    if spark is not None:
        spark.stop()
