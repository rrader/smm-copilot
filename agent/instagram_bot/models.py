from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    shortcode = Column(String, unique=True, index=True)
    caption = Column(String)
    url = Column(String)
    date = Column(DateTime)

    def __repr__(self):
        return f"<Post(shortcode='{self.shortcode}')>"
