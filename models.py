from sqlalchemy import Column, String, Text

from app import db


class Task(db.Model):

    __tablename__ = 'task'
    __tableargs__ = {
        'comment': 'Задачи'
    }

    task_id = Column(String, nullable=False, unique=True, primary_key=True)
    data = Column(Text, comment='Описание темы')

    def __repr__(self):
        return self.task_id


db.create_all()
