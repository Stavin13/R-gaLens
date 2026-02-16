from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import os
import json
from app.api.dependencies import get_db
from app.core import models
from app.core.config import settings
from app.services.timeline_service import timeline_builder
from app.utils.logger import logger

router = APIRouter()

async def build_timeline_task(name: str, db: Session):
    try:
        events = db.query(models.Event).all()
        timeline_data = timeline_builder.build_timeline(events)
        
        file_path = os.path.join(settings.TIMELINE_DIR, f"{name.replace(' ', '_')}.json")
        with open(file_path, "w") as f:
            json.dump(timeline_data, f)
            
        db_timeline = models.Timeline(
            name=name,
            description=f"Generated from {len(events)} events",
            data=timeline_data,
            file_path=file_path
        )
        db.add(db_timeline)
        db.commit()
        logger.info(f"Successfully built timeline: {name}")
    except Exception as e:
        logger.error(f"Error building timeline {name}: {e}")

@router.get("/build")
@router.post("/build")
async def build_timeline(
    name: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    background_tasks.add_task(build_timeline_task, name, db)
    return {"message": "Timeline build started", "name": name}

@router.get("/")
async def list_timelines(db: Session = Depends(get_db)):
    return db.query(models.Timeline).all()

@router.get("/{id}")
async def get_timeline(id: int, db: Session = Depends(get_db)):
    tl = db.query(models.Timeline).filter(models.Timeline.id == id).first()
    if not tl:
        raise HTTPException(status_code=404, detail="Timeline not found")
    return tl
