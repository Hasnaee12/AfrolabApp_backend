"""from app import create_app
from models import db, TaskDefinition, Department, Equipment

app = create_app()

departments = {
    'Technique': [
        {'name': "Nombre d'étalonnages" },
        {'name': "Nombre de réparations" },
        {'name': "Nombre d'installations" },
        {'name': "Nombre de livraisons"},
        {'name': 'Formations'}
    ],
    'Commercial': [
        {'name': 'Nombre de visites commerciales' },
        {'name': 'Montant de commandes' },
        {'name': 'Montant de ventes/livraisons' }
    ],
    'Financier': [
        {'name': 'Montant de recouvrement' }
    ],
}

equipment_list = [ 'Calibreur de température', 'Calibreur de pression',  'Oscilloscope',  'Multimètre', 'Étalon de fréquence', 'Soudure']
@app.before_first_request
def create_tables():
    db.create_all()
    # Insert departments if not already present
    if not Department.query.filter_by(name='Technique').first():
        db.session.add(Department(name='Technique'))
    if not Department.query.filter_by(name='Commercial').first():
        db.session.add(Department(name='Commercial'))
    if not Department.query.filter_by(name='Financier').first():
        db.session.add(Department(name='Financier'))
    db.session.commit()
    
with app.app_context():
    for dept_name, tasks in departments.items():
        department = Department.query.filter_by(name=dept_name).first()
        if department:
            for task in tasks:
                task_def = TaskDefinition(name=task['name'], department_id=department.id)
                db.session.add(task_def)
    
    for equipment_name in equipment_list:
        equipment = Equipment(name=equipment_name)
        db.session.add(equipment)
    
    db.session.commit()
    
if __name__ == "__main__":
    app.run(debug=True)
    """