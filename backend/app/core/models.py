from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    path = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="uploaded")  # uploaded, processing, processed, failed
    metadata_json = Column(JSON, nullable=True)
    decade = Column(Integer, nullable=True)

    nlp_result = relationship("NLPResult", back_populates="document", uselist=False)
    events = relationship("Event", back_populates="document")

class NLPResult(Base):
    __tablename__ = "nlp_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    entities = Column(JSON)  # List of {text, label}
    events_raw = Column(JSON)
    summary = Column(String)
    topics = Column(JSON)

    document = relationship("Document", back_populates="nlp_result")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    title = Column(String)
    description = Column(String)
    date_str = Column(String)
    normalized_date = Column(String, nullable=True)  # ISO format
    event_type = Column(String)
    confidence = Column(Float)
    entities = Column(JSON)
    sentence = Column(String)

    document = relationship("Document", back_populates="events")

class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(JSON)
    file_path = Column(String)
