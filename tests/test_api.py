from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_est_disponible():
    reponse = client.get("/")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "message": "API de suivi d'incidents. Bienvenue!"
    }


def test_incident_inexistant_retourne_404():
    reponse = client.get("/incidents/999999")

    assert reponse.status_code == 404
    assert reponse.json() == {
        "detail": "Incident introuvable"
    }


def test_cycle_de_vie_incident():
    donnees_incident = {
        "titre": "Test automatique API",
        "service": "tests-api",
        "priorite": "Moyenne",
        "status": "Ouvert",
        "description": "Incident créé uniquement pour vérifier les tests."
    }

    creation = client.post("/incidents", json=donnees_incident)

    assert creation.status_code == 201

    incident = creation.json()
    incident_id = incident["id"]

    modification = client.patch(
        f"/incidents/{incident_id}",
        json={"status": "Résolu"}
    )

    assert modification.status_code == 200
    assert modification.json()["status"] == "Résolu"

    suppression = client.delete(f"/incidents/{incident_id}")

    assert suppression.status_code == 204

    verification = client.get(f"/incidents/{incident_id}")

    assert verification.status_code == 404


def test_statistiques_sont_coherentes():
    reponse = client.get("/statistiques")

    assert reponse.status_code == 200

    statistiques = reponse.json()

    assert "total" in statistiques
    assert "par_statut" in statistiques
    assert "par_priorite" in statistiques

    assert sum(statistiques["par_statut"].values()) == statistiques["total"]
    assert sum(statistiques["par_priorite"].values()) == statistiques["total"]