from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime
from database import Base


class ResearchResult(Base):
    __tablename__ = "research_results"

    id = Column(String, primary_key=True)
    input = Column(Text, nullable=False)
    input_type = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    status = Column(String, nullable=False, default='complete')
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to frontend-compatible dict"""
        return {
            'id': self.id,
            'input': self.input,
            'type': self.input_type,
            'mode': self.mode,
            'content': self.content,
            'title': self.title,
            'status': self.status,
            'timestamp': int(self.created_at.timestamp() * 1000),
            'created_at': self.created_at.isoformat(),
        }
