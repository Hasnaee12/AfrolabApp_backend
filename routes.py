from flask import Blueprint, request, jsonify
from models import db, Department, Collaborator, TaskDefinition, Task, Attendance, Report, Equipment
from datetime import datetime, time

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
            'department_id': user.department_id,
            'departmentName': department_name if user.department_id else None
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
        print('Received data:', data) 
        required_fields = ['name', 'email', 'password', 'phone_number','role', 'department_id']
        
        # Check for missing required fields
        for field in required_fields:
            if field not in data:
                print(f'Missing required field: {field}')  # Debug log
                return jsonify({'error': f'Missing required field: {field}'}), 400

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
        required_fields = ['name', 'email', 'password', 'phone_number','role', 'department_id']

        # Check for missing required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        collaborator.name = data['name']
        collaborator.email = data['email']
        collaborator.phone_number = data.get('phone_number')
        collaborator.role = data['role']
        collaborator.password = data['password']
        collaborator.department_id = data['department_id']
        db.session.commit()
        return jsonify({'message': 'Collaborator updated successfully'}), 200
    elif request.method == 'DELETE':
        db.session.delete(collaborator)
        db.session.commit()
        return jsonify({'message': 'Collaborator deleted successfully'}), 200
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
    id = request.args.get('id') 
    department_id = request.args.get('department_id')  
    # Filter by id if provided
    if id:
        task_definition = TaskDefinition.query.get(id)
        if task_definition:
            return jsonify([{
                'id': task_definition.id,
                'name': task_definition.name,
                'department_id': task_definition.department_id
            }])
        else:
            return jsonify({'message': 'Task Definition not found'}), 404
    elif department_id:
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

def parse_time(time_str):
    """Parses a time string in HH:MM:SS format."""
    return datetime.strptime(time_str, "%H:%M:%S").time()
    
# Task Routes
@main.route('/tasks', methods=['GET', 'POST', 'PUT'])
def manage_tasks():
    if request.method == 'POST':
        data = request.json
        task_data = data.get('task')  # Extract task data from request object
# Debugging: Print received time values
        print("Received start_time:", task_data.get('start_time'))
        print("Received end_time:", task_data.get('end_time'))
        try:
            start_time = parse_time(task_data['start_time'])
            end_time = parse_time(task_data['end_time'])
        except ValueError as e:
            print(f"Failed to parse time: {e}")
            return jsonify({'error': 'Invalid time format'}), 400

        task_definition_id = task_data.get('task_definition_id')
        if not task_definition_id:
            return jsonify({'error': 'Task definition ID is required'}), 400

        task_definition = TaskDefinition.query.get(task_definition_id)
        if not task_definition:
            return jsonify({'error': 'Task definition not found'}), 404

        try:
            new_task = Task(
                task_definition_id=task_definition_id,
                client=task_data.get('client'),
                location=task_data.get('location'),
                start_time=start_time,
                end_time=end_time,
                collaborator_id=task_data.get('collaborator_id')
            )

            # Handle equipment IDs
            equipment_ids = task_data.get('equipment_ids', [])
            if equipment_ids:
                new_task.equipments = [Equipment.query.get(eid) for eid in equipment_ids]

            db.session.add(new_task)
            db.session.commit()
            return jsonify({'message': 'Task created successfully'}), 201

        except Exception as e:
            print(f"Error creating task: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to create task'}), 500
    elif request.method == 'PUT':
        data = request.json
        task_data = data.get('task')  # Extract task data from request object
        task_id = task_data.get('id')
        task = Task.query.get(task_id)

        if task:
            task.task_definition_id = task_data.get('task_definition_id')
            task.client = task_data.get('client')
            task.location = task_data.get('location')
            task.start_time = parse_time(task_data['start_time'])
            task.end_time = parse_time(task_data['end_time'])
            task.collaborator_id = task_data.get('collaborator_id')

            # Handle equipment IDs
            equipment_ids = task_data.get('equipment_ids', [])
            task.equipments = [Equipment.query.get(eid) for eid in equipment_ids]

            db.session.commit()
            return jsonify({'message': 'Task updated successfully'}), 200
        return jsonify({'message': 'Task not found'}), 404
    # GET method for retrieving tasks
    collaborator_id = request.args.get('collaborator_id')

    if collaborator_id:
        tasks = Task.query.filter_by(collaborator_id=collaborator_id).all()
        if tasks:
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
        else:
            return jsonify({'message': 'No tasks found for the specified collaborator_id'}), 404
    else:
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
    id = request.args.get('id')  
    # Filter by id if provided
    if id:
        equipment = Equipment.query.filter_by(id=id).all()
        if equipment:
            return jsonify([{'id': equip.id, 'name': equip.name} for equip in equipment])
        else:
            return jsonify({'message': 'Equipment not found'}), 404
    else:
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
            date=data.get('date'),
            status=data.get('status'),
            collaborator_id=data.get('collaborator_id')
        )
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({'message': 'Attendance recorded successfully'}), 201

    elif request.method == 'PUT':
        data = request.json
        attendance = Attendance.query.get(data.get('id'))
        if attendance:
            attendance.date = data.get('date')
            attendance.status = data.get('status')
            attendance.collaborator_id = data.get('collaborator_id')
            db.session.commit()
            return jsonify({'message': 'Attendance updated successfully'}), 200
        return jsonify({'message': 'Attendance record not found'}), 404

    collaborator_id = request.args.get('collaborator_id')

    if collaborator_id:
        attendance_records = Attendance.query.filter_by(collaborator_id=collaborator_id).all()
        if attendance_records:
            return jsonify([{
                'id': att.id, 
                'date': att.date, 
                'status': att.status, 
                'collaborator_id': att.collaborator_id
            } for att in attendance_records])
        else:
            return jsonify({'message': 'No attendance records found for the specified collaborator_id'}), 404
    else:
        attendance_records = Attendance.query.all()
        return jsonify([{
            'id': att.id, 
            'date': att.date, 
            'status': att.status, 
            'collaborator_id': att.collaborator_id
        } for att in attendance_records])

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
    return jsonify([{
        'id': report.id,
        'date': report.date.strftime('%Y-%m-%d'),
        'tasks': report.tasks,
        'attendance': report.attendance,
        'collaborator_id': report.collaborator_id
    } for report in reports]), 200
    
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
    supervisor = Collaborator.query.filter_by(role='superuser').first()
    employee = Collaborator.query.filter_by(role='employee').first()
    return jsonify({
        'adminName': admin.name if admin else '',
        'supervisorName': supervisor.name if supervisor else '',
        'employeeName': employee.name if employee else '' 
    })
