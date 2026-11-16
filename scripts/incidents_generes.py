import csv
import random
from datetime import timedelta
from pathlib import Path

from faker import Faker

fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

TOTAL_INCIDENTS = 150

services = [
    "payments-api",
    "customer-api",
    "auth-service",
    "reporting-service",
    "database-service",
    "storage-service",
]

priorites = ["Basse", "Moyenne", "Élevée", "Critique"]
statuses = ["Ouvert", "En cours", "Résolu"]

output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

output_file = output_folder / "incidents.csv"

with output_file.open("w", newline="", encoding="utf-8") as file:
    columns = [
        "id",
        "titre",
        "service",
        "priorite",
        "status",
        "cree_le",
        "resolu_le",
        "description",
    ]

    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()

    for incident_id in range(1, TOTAL_INCIDENTS + 1):
        status = random.choice(statuses)
        cree_le = fake.date_time_between(start_date="-60d", end_date="now")

        resolu_le = ""
        if status == "Résolu":
            resolu_le = (
                cree_le + timedelta(days=random.randint(1, 7))
            ).strftime("%Y-%m-%d %H:%M:%S")

        writer.writerow(
            {
                "id": incident_id,
                "titre": fake.sentence(nb_words=5).rstrip("."),
                "service": random.choice(services),
                "priorite": random.choice(priorites),
                "status": status,
                "cree_le": cree_le.strftime("%Y-%m-%d %H:%M:%S"),
                "resolu_le": resolu_le,
                "description": fake.sentence(nb_words=12),
            }
        )

print(f"{TOTAL_INCIDENTS} incidents générés dans : {output_file}")