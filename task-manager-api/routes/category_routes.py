from flask import Blueprint, jsonify, request

from routes.serializers import serialize_category
from validators.category_validator import validate_category_create, validate_category_update


def create_category_blueprint(controller):
    bp = Blueprint('categories', __name__)

    @bp.get('/categories')
    def list_categories():
        categories = controller.list_categories_with_task_count()
        return jsonify([{**serialize_category(c), 'task_count': count} for c, count in categories]), 200

    @bp.post('/categories')
    def create_category():
        data = validate_category_create(request.get_json(silent=True))
        return jsonify(serialize_category(controller.create_category(data))), 201

    @bp.put('/categories/<int:category_id>')
    def update_category(category_id):
        changes = validate_category_update(request.get_json(silent=True))
        return jsonify(serialize_category(controller.update_category(category_id, changes))), 200

    @bp.delete('/categories/<int:category_id>')
    def delete_category(category_id):
        controller.delete_category(category_id)
        return jsonify({'message': 'Categoria deletada'}), 200

    return bp
