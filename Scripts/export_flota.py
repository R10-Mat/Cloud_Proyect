#!/usr/bin/env python3
"""Export tablas `conductores` y `vehiculos` (MySQL / MS-FLOTA) a S3 en formato JSON Lines."""

from __future__ import annotations

import base64
import json
import os
import sys
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

import boto3
import pymysql
from pymysql.cursors import DictCursor

BUCKET = "last-mile-proy"


def _json_default(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        if obj.is_nan() or obj.is_infinite():
            return str(obj)
        return float(obj)
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, (bytes, memoryview)):
        return base64.b64encode(bytes(obj)).decode("ascii")
    if isinstance(obj, set):
        return list(obj)
    return str(obj)


def _to_jsonl(rows: list[dict]) -> bytes:
    """Convierte lista de dicts a JSON Lines (un JSON por línea, sin indent)."""
    lines = [json.dumps(row, ensure_ascii=False, default=_json_default) for row in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _s3_key(prefix: str, table: str, ts: str) -> str:
    return f"{prefix}/{table}/{table}_{ts}.json"


def main() -> int:
    host = os.environ["MYSQL_HOST"]
    port = int(os.environ.get("MYSQL_PORT", "3306"))
    db = os.environ["MYSQL_DATABASE"]
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    conn = pymysql.connect(
        host=host, port=port, user=user, password=password,
        database=db, charset="utf8mb4", cursorclass=DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM conductores ORDER BY id ASC")
            conductores = cur.fetchall()

            cur.execute("SELECT * FROM vehiculos ORDER BY id ASC")
            vehiculos = cur.fetchall()
    finally:
        conn.close()

    s3 = boto3.client("s3")


    body_c = _to_jsonl(conductores)
    key_c = _s3_key("BD-FLOTA", "conductores", ts)
    s3.put_object(Bucket=BUCKET, Key=key_c, Body=body_c, ContentType="application/json")
    print(f"OK s3://{BUCKET}/{key_c} ({len(conductores)} rows, {len(body_c)} bytes)")


    body_v = _to_jsonl(vehiculos)
    key_v = _s3_key("BD-FLOTA", "vehiculos", ts)
    s3.put_object(Bucket=BUCKET, Key=key_v, Body=body_v, ContentType="application/json")
    print(f"OK s3://{BUCKET}/{key_v} ({len(vehiculos)} rows, {len(body_v)} bytes)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyError as e:
        print(f"Falta variable de entorno requerida: {e.args[0]}", file=sys.stderr)
        raise SystemExit(2)
