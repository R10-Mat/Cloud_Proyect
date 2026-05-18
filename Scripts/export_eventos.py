#!/usr/bin/env python3
"""Export colección `eventos` (MongoDB / MS-EVENTOS) a S3 en formato JSON Lines."""

from __future__ import annotations

import base64
import json
import os
import sys
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from urllib.parse import quote_plus

import boto3
from pymongo import MongoClient

BUCKET = "last-mile-proy"


def _mongo_uri(host: str, port: int, user: str, password: str, db: str, auth_source: str) -> str:
    u = quote_plus(user)
    p = quote_plus(password)
    return f"mongodb://{u}:{p}@{host}:{port}/{db}?authSource={auth_source}"


def _mongo_to_plain(value: Any) -> Any:
    """Convierte recursivamente tipos BSON a tipos nativos de Python."""
    try:
        from bson.objectid import ObjectId
        if isinstance(value, ObjectId):
            return str(value)
    except ImportError:
        pass
    try:
        from bson.decimal128 import Decimal128
        if isinstance(value, Decimal128):
            return float(str(value.to_decimal()))
    except ImportError:
        pass
    if isinstance(value, dict):
        return {str(k): _mongo_to_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_mongo_to_plain(v) for v in value]
    if isinstance(value, tuple):
        return [_mongo_to_plain(v) for v in value]
    if isinstance(value, set):
        return [_mongo_to_plain(v) for v in value]
    return value


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
    return str(obj)


def _to_jsonl(docs: list[dict]) -> bytes:
    """Convierte lista de dicts a JSON Lines (un JSON por línea, sin indent)."""
    lines = [json.dumps(doc, ensure_ascii=False, default=_json_default) for doc in docs]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _s3_key(prefix: str, collection: str, ts: str) -> str:
    return f"{prefix}/{collection}/{collection}_{ts}.json"


def main() -> int:
    host = os.environ["MONGO_HOST"]
    port = int(os.environ.get("MONGO_PORT", "27017"))
    user = os.environ["MONGO_INITDB_ROOT_USERNAME"]
    password = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    db_name = os.environ["MONGO_DATABASE"]
    auth = os.environ.get("MONGO_AUTH_SOURCE", "admin")
    collection = os.environ.get("MONGO_COLLECTION", "eventos")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    uri = _mongo_uri(host, port, user, password, db_name, auth)
    client = MongoClient(uri, serverSelectionTimeoutMS=30_000)
    try:
        coll = client[db_name][collection]
        raw_docs = list(coll.find({}))
    finally:
        client.close()


    plain_docs = [_mongo_to_plain(doc) for doc in raw_docs]

    s3 = boto3.client("s3")

 
    body = _to_jsonl(plain_docs)
    key = _s3_key("BD-EVENTOS", collection, ts)
    s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType="application/json")
    print(f"OK s3://{BUCKET}/{key} ({len(plain_docs)} docs, {len(body)} bytes)")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyError as e:
        print(f"Falta variable de entorno requerida: {e.args[0]}", file=sys.stderr)
        raise SystemExit(2)
