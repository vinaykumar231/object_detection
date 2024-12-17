from sqlalchemy import Column, Integer, String, Float, Enum, JSON, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class MediaUpload(Base):
    __tablename__ = "media_upload"

    upload_id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(255), nullable=False)
    unit_id = Column(Integer, nullable=False)
    property_id = Column(Integer, nullable=False)
    media_type = Column(Enum("image", "video", name="media_type"), nullable=False)
    media_url = Column(String(500), nullable=False)
    uploaded_at = Column(TIMESTAMP, default=func.now())

    detection_results = relationship("DetectionResults", back_populates="media_upload", cascade="all, delete")


class DetectionResults(Base):
    __tablename__ = "detection_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    upload_id = Column(Integer,ForeignKey("media_upload.upload_id", ondelete="CASCADE"),nullable=False)
    detected_items = Column(JSON, nullable=False)
    detected_count = Column(Integer, nullable=False)
    bounding_box_summary = Column(JSON, nullable=True)
    image_with_bounding_box_url = Column(String(500), nullable=True)
    detected_at = Column(TIMESTAMP, default=func.now())

    media_upload = relationship("MediaUpload", back_populates="detection_results")
    detected_objects = relationship("DetectedObjects", back_populates="detection_results", cascade="all, delete")


class DetectedObjects(Base):
    __tablename__ = "detected_objects"

    object_id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, ForeignKey("detection_results.result_id", ondelete="CASCADE"),nullable=False)
    label = Column(String(255), nullable=False)
    ymin = Column(Float, nullable=False)
    xmin = Column(Float, nullable=False)
    ymax = Column(Float, nullable=False)
    xmax = Column(Float, nullable=False)

    detection_results = relationship("DetectionResults", back_populates="detected_objects")
