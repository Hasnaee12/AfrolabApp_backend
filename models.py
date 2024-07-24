from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Collaborator(db.Model):
    __tablename__ = 'collaborator'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'department_id': self.department_id,
            }

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class TaskDefinition(db.Model):
    __tablename__ = 'task_definitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)   
    task_definition_id = db.Column(db.Integer, db.ForeignKey('task_definitions.id'))
    client = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)  # Adding the date column
    collaborator_id = db.Column(db.Integer, db.ForeignKey('collaborator.id'))
# Define many-to-many relationship with Equipment
    equipments = db.relationship('TaskEquipment', back_populates='task')

class TaskEquipment(db.Model):
    __tablename__ = 'task_equipments'
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
    usage_count = db.Column(db.Integer, nullable=False)
    task = db.relationship('Task', back_populates='equipments')
    equipment = db.relationship('Equipment')

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    collaborator_id = db.Column(db.Integer, db.ForeignKey('collaborator.id'))

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    tasks = db.Column(db.JSON)
    attendance = db.Column(db.JSON)
    collaborator_id = db.Column(db.Integer, db.ForeignKey('collaborator.id'))
