import boto3
import os
import time
from typing import Any

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_OUTPUT = os.getenv("ATHENA_S3_OUTPUT_LOCATION", "s3://lastmile-athena-resultados/")
ATHENA_DATABASE = os.getenv("ATHENA_DATABASE", "lastmile_db")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "athena",
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    return _client


def ejecutar_query(sql: str, max_wait: int = 30) -> list[dict[str, Any]]:
    client = get_client()

    response = client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": ATHENA_DATABASE},
        ResultConfiguration={"OutputLocation": S3_OUTPUT},
    )
    execution_id = response["QueryExecutionId"]

    elapsed = 0
    while elapsed < max_wait:
        estado = client.get_query_execution(QueryExecutionId=execution_id)
        status = estado["QueryExecution"]["Status"]["State"]

        if status == "SUCCEEDED":
            break
        elif status in ("FAILED", "CANCELLED"):
            reason = estado["QueryExecution"]["Status"].get("StateChangeReason", "desconocido")
            raise RuntimeError(f"Query Athena {status}: {reason}")

        time.sleep(2)
        elapsed += 2
    else:
        raise TimeoutError("Timeout esperando resultado de Athena")

    results = client.get_query_results(QueryExecutionId=execution_id)
    rows = results["ResultSet"]["Rows"]

    if not rows:
        return []

    headers = [col["VarCharValue"] for col in rows[0]["Data"]]
    return [
        {headers[i]: cell.get("VarCharValue", "") for i, cell in enumerate(row["Data"])}
        for row in rows[1:]
    ]
