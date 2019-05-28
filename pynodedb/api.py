from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import noload

from . import functions as f
from .database import db, Node

# Define BLueprint
bp = Blueprint('api', __name__, url_prefix='/api')


# Return Node by ID
@bp.route('node', methods=['GET', 'POST'])
@login_required
def node():
    # Defaults
    status = 'ERROR'
    errors = []
    data = {}

    # Get Node by ID
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
        status = 'OK'
    else:
        errors.append('node not found')

    # Build response and return as JSON
    response = {
        'status': status,
        'errors': errors,
        'data': data,
    }
    json = jsonify(response)
    return json


# Return all Nodes (Minimal dataset)
@bp.route('nodes/all', methods=['GET', 'POST'])
@login_required
def all_nodes():
    # Defaults
    status = 'ERROR'
    errors = []
    data = {}

    # Get Node by ID
    serialized_nodes = []
    nodes = db.session.query(Node).options(noload('*')).all()
    if nodes:
        # serialize data
        for node in nodes:
            serialized_nodes.append(node.to_dict())

        status = 'OK'
        data['nodes'] = serialized_nodes
    else:
        errors.append('An error occurred fetching Nodes from DB')

    # Build response and return as JSON
    response = {
        'status': status,
        'errors': errors,
        'data': data,
    }
    json = jsonify(response)
    return json
