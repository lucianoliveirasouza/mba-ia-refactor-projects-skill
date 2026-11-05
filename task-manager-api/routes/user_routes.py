from flask import Blueprint, jsonify, request

from routes.serializers import serialize_task, serialize_task_summary, serialize_user
from utils.constants import Role
from utils.helpers import utcnow
from validators.user_validator import validate_login, validate_user_create, validate_user_update


def create_user_blueprint(controller, auth):
    bp = Blueprint('users', __name__)

    @bp.get('/users')
    def list_users():
        users = controller.list_users_with_task_count()
        return jsonify([{**serialize_user(user), 'task_count': count} for user, count in users]), 200

    @bp.get('/users/<int:user_id>')
    def get_user(user_id):
        data = serialize_user(controller.get_user(user_id))
        data['tasks'] = [serialize_task(t) for t in controller.get_user_tasks(user_id)]
        return jsonify(data), 200

    @bp.post('/users')
    def create_user():
        data = validate_user_create(request.get_json(silent=True))
        if data['role'] != Role.USER:  # atribuir papel privilegiado exige admin
            auth.ensure_admin()
        return jsonify(serialize_user(controller.create_user(data))), 201

    @bp.put('/users/<int:user_id>')
    def update_user(user_id):
        changes = validate_user_update(request.get_json(silent=True))
        if 'role' in changes:  # mudança de papel exige admin
            auth.ensure_admin()
        return jsonify(serialize_user(controller.update_user(user_id, changes))), 200

    @bp.delete('/users/<int:user_id>')
    @auth.require_admin
    def delete_user(user_id):
        controller.delete_user(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    @bp.get('/users/<int:user_id>/tasks')
    def get_user_tasks(user_id):
        now = utcnow()
        return jsonify([serialize_task_summary(t, now) for t in controller.get_user_tasks(user_id)]), 200

    @bp.post('/login')
    def login():
        credentials = validate_login(request.get_json(silent=True))
        user = controller.authenticate(credentials['email'], credentials['password'])
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': serialize_user(user),
            'token': auth.issue_token(user),
        }), 200

    return bp
