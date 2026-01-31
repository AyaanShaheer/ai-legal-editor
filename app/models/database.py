from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    blob_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.original_filename})>"


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    blob_path = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, doc_id={self.document_id}, version={self.version_number})>"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    instruction = Column(Text, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    patch_json = Column(Text, nullable=True)  # Store JSON as text
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(id={self.id}, status={self.status})>"
