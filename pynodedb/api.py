from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import noload

from . import functions as f
from .database import db, Node

# Define BLueprint
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('node', methods=['GET', 'POST'])
@login_required
def node():
    status = 'OK'
    errors = []
    data = {}

    node_id = request.form.get('node_id') or request.args.get('node_id')
    if node_id:
        request.form.get('node_id')
    else:
        errors.append('node_id not specified in request')

    node = None
    if node_id:
        node = db.session.query(Node).options(noload('*')).get(node_id)

    if node:
        data['node'] = node.to_dict()
    else:
        errors.append('node not found')

    if len(errors) > 0:
        status = 'ERROR'

    response = {
        'status': status,
        'errors': errors,
        'data': data,
    }
    json = jsonify(response)
    return json
