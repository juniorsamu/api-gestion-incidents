from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import Base, SessionLocal, engine
from app.model import Incident
from app.schemas import IncidentCreation, IncidentMiseAJour, IncidentReponse
from app.security import verifier_token


# Crée les tables au démarrage si elles n'existent pas.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de suivi d'incidents",
    description="API professionnelle de suivi d'incidents.",
    version="1.0.0",
)


# Le gestionnaire de session SQLAlchemy est utilisé par FastAPI via Depends.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def incident_to_response(incident):
    return IncidentReponse(
        id=incident.id,
        titre=incident.titre,
        service=incident.service,
        priorite=incident.priorite,
        status=incident.status,
        description=incident.description,
    )


@app.get("/")
def Bienvenue():
    return {"message": "API de suivi d'incidents. Bienvenue!"}


@app.get("/etats")
def verification_etats():
    return {"status": "ok"}


@app.post(
    "/incidents",
    response_model=IncidentReponse,
    status_code=status.HTTP_201_CREATED,
)
def creation_incident(incident: IncidentCreation, db: Session = Depends(get_db)):
    # On crée un objet SQLAlchemy, pas un objet Pydantic de réponse.
    # Le modèle `Incident` correspond à la table SQLite.
    incident_db = Incident(**incident.model_dump())

    # Ajout en base de données puis sauvegarde.
    db.add(incident_db)
    db.commit()
    db.refresh(incident_db)

    # Conversion du modèle SQLAlchemy vers le schéma de sortie FastAPI.
    return IncidentReponse(
        id=incident_db.id,
        titre=incident_db.titre,
        service=incident_db.service,
        priorite=incident_db.priorite,
        description=incident_db.description,
        status=incident_db.status,
    )

@app.get("/incidents", response_model=list[IncidentReponse])
def get_incidents(
    status: str | None = None,
    priorite: str | None = None,
    titre: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status is not None:
        query = query.filter(Incident.status == status)

    if priorite is not None:
        query = query.filter(Incident.priorite == priorite)

    if titre is not None:
        query = query.filter(Incident.titre.ilike(f"%{titre.strip()}%"))

    incidents = (query.order_by(Incident.id.desc()).offset(skip).limit(limit).all())

    return [
        incident_to_response(incident)
        for incident in incidents
    ]


@app.get("/incidents/{incident_id}", response_model=IncidentReponse)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable"
        )

    return incident_to_response(incident)


@app.patch("/incidents/{incident_id}", response_model=IncidentReponse)
def modifier_incident(
    incident_id: int,
    donnees: IncidentMiseAJour,
    db: Session = Depends(get_db),
    _token: dict = Depends(verifier_token)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable"
        )

    modifications = donnees.model_dump(
        exclude_unset=True,
        mode="json"
    )

    for champ, valeur in modifications.items():
        setattr(incident, champ, valeur)

    db.commit()
    db.refresh(incident)

    return incident_to_response(incident)


@app.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def supprimer_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    _token: dict = Depends(verifier_token)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable"
        )

    db.delete(incident)
    db.commit()

    return None

@app.get("/statistiques")
def obtenir_statistiques(db: Session = Depends(get_db)):
    total = db.query(Incident).count()

    par_statut = {
        statut: nombre
        for statut, nombre in (
            db.query(
                Incident.status,
                func.count(Incident.id)
            )
            .group_by(Incident.status)
            .all()
        )
    }

    par_priorite = {
        priorite: nombre
        for priorite, nombre in (
            db.query(
                Incident.priorite,
                func.count(Incident.id)
            )
            .group_by(Incident.priorite)
            .all()
        )
    }

    return {
        "total": total,
        "par_statut": par_statut,
        "par_priorite": par_priorite
    }