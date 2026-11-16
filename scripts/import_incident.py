import csv
from pathlib import Path

from app.database import Base, SessionLocal, engine
from app.model import Incident

Base.metadata.create_all(bind=engine)

csv_file = Path("data/incidents.csv")

db = SessionLocal()

imported_count = 0
skipped_count = 0

try:
    with csv_file.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            existing_incident = (
                db.query(Incident)
                .filter(
                    Incident.titre  == row["titre"],
                    Incident.service == row["service"]
                )
                .first()
            )

            if existing_incident:
                skipped_count += 1
                continue

            incident = Incident(
                titre=row["titre"],
                service=row["service"],
                priorite=row["priorite"],
                status=row["status"],
                description=row["description"],
            )

            db.add(incident)
            imported_count += 1

    db.commit()

    print(f"{imported_count} incidents importés.")
    print(f"{skipped_count} incidents ignorés car déjà présents.")

finally:
    db.close()