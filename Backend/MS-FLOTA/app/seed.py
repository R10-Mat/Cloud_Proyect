from app.database import SessionLocal
from app.models.flota import Conductor
from sqlalchemy.exc import IntegrityError
import os

TARGET = 20000
BATCH_SIZE = 1000

def generate_conductor(idx: int) -> Conductor:
    nombre = f"Conductor {idx}"
    licencia = f"LIC{idx:07d}"
    telefono = f"+34{600000000 + idx}"
    return Conductor(nombre=nombre, licencia=licencia, telefono=telefono)

def main():
    db = SessionLocal()
    try:
        existing = db.query(Conductor).count()
        print(f"Existing conductores: {existing}")
        if existing >= TARGET:
            print("Target already met — nothing to do.")
            return

        to_create = TARGET - existing
        print(f"Will create {to_create} conductores in batches of {BATCH_SIZE}...")

        created = 0
        start_idx = existing + 1
        while created < to_create:
            batch = []
            for i in range(min(BATCH_SIZE, to_create - created)):
                idx = start_idx + created + i
                batch.append(generate_conductor(idx))

            try:
                db.bulk_save_objects(batch)
                db.commit()
            except IntegrityError as e:
                db.rollback()
                # Try inserting one-by-one to skip duplicates
                for obj in batch:
                    try:
                        db.add(obj)
                        db.commit()
                    except IntegrityError:
                        db.rollback()
            created += len(batch)
            print(f"Inserted {created}/{to_create}")

        print("Seeding complete.")
    finally:
        db.close()

if __name__ == '__main__':
    main()
