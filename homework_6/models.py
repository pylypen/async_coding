from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, JSON

Base = declarative_base()


class CVE(Base):
    __tablename__ = 'cves'

    id = Column(String, primary_key=True)
    date_published = Column(DateTime)
    date_updated = Column(DateTime)
    title = Column(String)
    description = Column(Text)
    problem_types = Column(JSON)

