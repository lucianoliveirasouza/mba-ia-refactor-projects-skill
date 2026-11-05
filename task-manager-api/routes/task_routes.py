from flask import Blueprint, jsonify, request

from routes.serializers import serialize_task
from utils.helpers import utcnow
from validators.task_validator import validate_search_params, validate_task_create, validate_task_update


def create_task_blueprint(controller):
    bp = Blueprint('tasks', __name__)

    @bp.get('/tasks')
    def list_tasks():
        now = utcnow()
        tasks = controller.list_tasks()
        return jsonify([serialize_task(t, overdue=True, relations=True, now=now) for t in tasks]), 200

    @bp.get('/tasks/<int:task_id>')
    def get_task(task_id):
        return jsonify(serialize_task(controller.get_task(task_id), overdue=True)), 200

    @bp.post('/tasks')
    def create_task():
        data = validate_task_create(request.get_json(silent=True))
        return jsonify(serialize_task(controller.create_task(data))), 201

    @bp.put('/tasks/<int:task_id>')
    def update_task(task_id):
        changes = validate_task_update(request.get_json(silent=True))
        return jsonify(serialize_task(controller.update_task(task_id, changes))), 200

    @bp.delete('/tasks/<int:task_id>')
    def delete_task(task_id):
        controller.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    @bp.get('/tasks/search')
    def search_tasks():
        filters = validate_search_params(request.args)
        return jsonify([serialize_task(t) for t in controller.search_tasks(**filters)]), 200

    @bp.get('/tasks/stats')
    def task_stats():
        return jsonify(controller.stats()), 200

    return bp
