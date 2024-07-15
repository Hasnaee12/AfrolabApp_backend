from flask import Blueprint, request, jsonify
from models import db, Department, Collaborator, TaskDefinition, Task, Attendance, Report, Equipment
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    print(f"Received email: {email} and password: {password}")  # Debugging

    user = Collaborator.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.name}")  # Debugging
    if user and password == user.password:
        department = Department.query.get(user.department_id)
        department_name = department.name if department else None
        return jsonify({
            'message': 'Login successful',
            'role': user.role,
            'name': user.name,
            'userId': user.id,
            'department_id': department.id,
            'departmentName': department_name
        }), 200
    return jsonify({'message': 'Invalid email or password'}), 401

# Department Routes
@main.route('/departments', methods=['GET', 'POST'])
def manage_departments():
    if request.method == 'POST':
        data = request.json
        new_department = Department(name=data['name'])
        db.session.add(new_department)
        db.session.commit()
        return jsonify({'message': 'Department created successfully'}), 201
    departments = Department.query.all()
    return jsonify([{'id': dept.id, 'name': dept.name} for dept in departments])

# Collaborator Routes
@main.route('/collaborators', methods=['GET', 'POST'])
def manage_collaborators():
    if request.method == 'POST':
        data = request.json
        new_collaborator = Collaborator(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            phone_number=data.get('phone_number'),
            role=data['role'],
            department_id=data['department_id']
        )
        db.session.add(new_collaborator)
        db.session.commit()
        return jsonify({'message': 'Collaborator created successfully'}), 201

    # Handling GET request
    role = request.args.get('role')
    department_id = request.args.get('department_id')  
    id = request.args.get('id')  

    query = Collaborator.query

    # Filter by role if provided
    if role:
        query = query.filter_by(role=role)
    
    # Filter by department_id if provided
    if department_id:
        query = query.filter_by(department_id=department_id)
    # Filter by id if provided
    if id:
        query = query.filter_by(id=id)

    collaborators = query.all()
    
    # Format the response
    return jsonify([{
        'id': collab.id,
        'name': collab.name,
        'email': collab.email,
        'phone_number':collab.phone_number,
        'role': collab.role,
        'password': collab.password,
        'department_id': collab.department_id,
        
    } for collab in collaborators])

@main.route('/collaborators/<int:id>', methods=['PUT', 'DELETE'])
def update_or_delete_collaborator(id):
    collaborator = Collaborator.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        collaborator.name = data['name']
        collaborator.email = data['email']
        collaborator.phone_number = data.get('phone_number')
        collaborator.role = data['role']
        collaborator.department_id = data['department_id']
        db.session.commit()
        return jsonify({'message': 'Collaborator updated successfully'})
    elif request.method == 'DELETE':
        db.session.delete(collaborator)
        db.session.commit()
        return jsonify({'message': 'Collaborator deleted successfully'})
# Task Definition Routes
@main.route('/task_definitions', methods=['GET', 'POST', 'PUT'])
def manage_task_definitions():
    if request.method == 'POST':
        data = request.json
        new_task_definition = TaskDefinition(
            name=data['name'],
            department_id=data['department_id']
        )
        db.session.add(new_task_definition)
        db.session.commit()
        return jsonify({'message': 'Task Definition created successfully'}), 201
    elif request.method == 'PUT':
        data = request.json
        task_definition = TaskDefinition.query.get(data['id'])
        if task_definition:
            task_definition.name = data['name']
            task_definition.department_id = data['department_id']
            db.session.commit()
            return jsonify({'message': 'Task Definition updated successfully'}), 200
        return jsonify({'message': 'Task Definition not found'}), 404
   
    # GET method with optional department_id filter
    department_id = request.args.get('department_id')
    if department_id:
        task_definitions = TaskDefinition.query.filter_by(department_id=department_id).all()
    else:
        task_definitions = TaskDefinition.query.all()

    # Convert task definitions to JSON format
    task_definitions_json = [{'id': task_def.id, 'name': task_def.name, 'department_id': task_def.department_id} for task_def in task_definitions]
    return jsonify(task_definitions_json)
@main.route('/task_definitions/<int:id>', methods=['DELETE'])
def delete_task_definition(id):
    task_definition = TaskDefinition.query.get(id)
    if not task_definition:
        return jsonify({'message': 'Task Definition not found'}), 404

    db.session.delete(task_definition)
    db.session.commit()
    return jsonify({'message': 'Task Definition deleted successfully'}), 200


# Task Routes
@main.route('/tasks', methods=['GET', 'POST', 'PUT'])
def manage_tasks():
    if request.method == 'POST':
        data = request.json
        task_data = data.get('task')  # Extract task data from request object

        new_task = Task(
            task_definition_id=task_data.get('task_definition_id'),
            client=task_data.get('client'),
            location=task_data.get('location'),
            start_time=datetime.fromisoformat(task_data['start_time']),
            end_time=datetime.fromisoformat(task_data['end_time']),
            collaborator_id=task_data.get('collaborator_id')
        )

        # Handle equipment IDs
        equipment_ids = task_data.get('equipment_ids', [])
        if equipment_ids:
            new_task.equipments = [Equipment.query.get(eid) for eid in equipment_ids]

        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully'}), 201

    elif request.method == 'PUT':
        data = request.json
        task_data = data.get('task')  # Extract task data from request object
        task_id = task_data.get('id')
        task = Task.query.get(task_id)

        if task:
            task.task_definition_id = task_data.get('task_definition_id')
            task.client = task_data.get('client')
            task.location = task_data.get('location')
            task.start_time = datetime.fromisoformat(task_data['start_time'])
            task.end_time = datetime.fromisoformat(task_data['end_time'])
            task.collaborator_id = task_data.get('collaborator_id')

            # Handle equipment IDs
            equipment_ids = task_data.get('equipment_ids', [])
            task.equipments = [Equipment.query.get(eid) for eid in equipment_ids]

            db.session.commit()
            return jsonify({'message': 'Task updated successfully'}), 200
        return jsonify({'message': 'Task not found'}), 404

    

       

    # GET method for retrieving all tasks
    tasks = Task.query.all()
    return jsonify([{
        'id': task.id,
        'task_definition_id': task.task_definition_id,
        'equipment_ids': [equipment.id for equipment in task.equipments],
        'client': task.client,
        'location': task.location,
        'start_time': task.start_time.isoformat(),
        'end_time': task.end_time.isoformat(),
        'collaborator_id': task.collaborator_id
    } for task in tasks])

@main.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'message': 'task not found'}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'task deleted successfully'}), 200

# Equipment Routes
@main.route('/equipment', methods=['GET', 'POST', 'PUT'])
def manage_equipment():
    if request.method == 'POST':
        data = request.json
        new_equipment = Equipment(
            name=data['name']
        )
        db.session.add(new_equipment)
        db.session.commit()
        return jsonify({'message': 'Equipment created successfully'}), 201

    elif request.method == 'PUT':
        data = request.json
        equipment = Equipment.query.get(data['id'])
        if equipment:
            equipment.name = data['name']
            db.session.commit()
            return jsonify({'message': 'Equipment updated successfully'}), 200
        return jsonify({'message': 'Equipment not found'}), 404
    # GET request
    equipment = Equipment.query.all()
    return jsonify([{'id': equip.id, 'name': equip.name} for equip in equipment])

@main.route('/equipment/<int:id>', methods=['DELETE'])
def delete_equipment(id):
    equipment = Equipment.query.get(id)
    if not equipment:
        return jsonify({'message': 'equipment not found'}), 404

    db.session.delete(equipment)
    db.session.commit()
    return jsonify({'message': 'equipment deleted successfully'}), 200

# Attendance Routes
@main.route('/attendance', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_attendance():
    if request.method == 'POST':
        data = request.json
        new_attendance = Attendance(
            date=data['date'],
            status=data['status'],
            collaborator_id=data['collaborator_id']
        )
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({'message': 'Attendance recorded successfully'}), 201
    elif request.method == 'PUT':
        data = request.json
        attendance = Attendance.query.get(data['id'])
        if attendance:
            attendance.date = data['date']
            attendance.status = data['status']
            attendance.collaborator_id = data['collaborator_id']
            db.session.commit()
            return jsonify({'message': 'Attendance updated successfully'}), 200
        return jsonify({'message': 'Attendance record not found'}), 404
    
    attendance_records = Attendance.query.all()
    return jsonify([{'id': att.id, 'date': att.date, 'status': att.status, 'collaborator_id': att.collaborator_id} for att in attendance_records])
@main.route('/attendance/<int:id>', methods=['DELETE'])
def delete_attendance(id):
    attendance = Attendance.query.get(id)
    if not attendance:
        return jsonify({'message': 'attendance not found'}), 404

    db.session.delete(attendance)
    db.session.commit()
    return jsonify({'message': 'attendance deleted successfully'}), 200
# Report Routes
@main.route('/reports', methods=['GET', 'POST', 'PUT'])
def manage_reports():
    if request.method == 'POST':
        data = request.json
        new_report = Report(
            date=data['date'],
            tasks=data['tasks'],
            attendance=data['attendance'],
            collaborator_id=data['collaborator_id']
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({'message': 'Report created successfully'}), 201
    elif request.method == 'PUT':
        data = request.json
        report = Report.query.get(data['id'])
        if report:
            report.date = data['date']
            report.tasks = data['tasks']
            report.attendance = data['attendance']
            report.collaborator_id = data['collaborator_id']
            db.session.commit()
            return jsonify({'message': 'Report updated successfully'}), 200
        return jsonify({'message': 'Report not found'}), 404
    
    
    reports = Report.query.all()
    return jsonify([{'id': rep.id, 'date': rep.date, 'tasks': rep.tasks, 'attendance': rep.attendance, 'collaborator_id': rep.collaborator_id} for rep in reports])
@main.route('/report/<int:id>', methods=['DELETE'])
def delete_report(id):
    report = Report.query.get(id)
    if not report:
        return jsonify({'message': 'report not found'}), 404

    db.session.delete(report)
    db.session.commit()
    return jsonify({'message': 'report deleted successfully'}), 200
@main.route('/user/info', methods=['GET'])
def get_user_info():
    # Exemple de récupération du nom de l'administrateur et du superviseur
    admin = Collaborator.query.filter_by(role='admin').first()
    supervisor = Collaborator.query.filter_by(role='supervisor').first()
    employee = Collaborator.query.filter_by(role='employee').first()
    return jsonify({
        'adminName': admin.name if admin else '',
        'supervisorName': supervisor.name if supervisor else '',
        'employeeName': employee.name if employee else '' 
    })
