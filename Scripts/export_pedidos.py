#!/usr/bin/env python3
"""Export tablas `pedidos` y `detalle_paquetes` (PostgreSQL / MS-PEDIDOS) a S3 en formato JSON Lines."""

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
import psycopg2
from psycopg2.extras import RealDictCursor

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
    lines = [json.dumps(dict(row), ensure_ascii=False, default=_json_default) for row in rows]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _s3_key(prefix: str, table: str, ts: str) -> str:
    return f"{prefix}/{table}/{table}_{ts}.json"


def main() -> int:
    host = os.environ["POSTGRES_HOST"]
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    db = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=password)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM pedidos ORDER BY id ASC")
            pedidos = cur.fetchall()

            cur.execute("SELECT * FROM detalle_paquetes ORDER BY id ASC")
            paquetes = cur.fetchall()
    finally:
        conn.close()

    s3 = boto3.client("s3")


    body_p = _to_jsonl(pedidos)
    key_p = _s3_key("BD-PEDIDOS", "pedidos", ts)
    s3.put_object(Bucket=BUCKET, Key=key_p, Body=body_p, ContentType="application/json")
    print(f"OK s3://{BUCKET}/{key_p} ({len(pedidos)} rows, {len(body_p)} bytes)")


    body_d = _to_jsonl(paquetes)
    key_d = _s3_key("BD-PEDIDOS", "detalle_paquetes", ts)
    s3.put_object(Bucket=BUCKET, Key=key_d, Body=body_d, ContentType="application/json")
    print(f"OK s3://{BUCKET}/{key_d} ({len(paquetes)} rows, {len(body_d)} bytes)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyError as e:
        print(f"Falta variable de entorno requerida: {e.args[0]}", file=sys.stderr)
        raise SystemExit(2)
