from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import noload, joinedload

from . import functions as f
from .database import db, Node, Link

# Define BLueprint
bp = Blueprint('api', __name__, url_prefix='/api')


# Return Node by ID
@bp.route('node', methods=['GET', 'POST'])
@login_required
def node():
    # Check user hasn't expired
    if not current_user.is_active:
        abort(403)

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
    # Check user hasn't expired
    if not current_user.is_active:
        abort(403)

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
            serialized_nodes.append({
                'id': node.id,
                'user_id': node.user_id,
                'status_id': node.status_id,
                'name': node.name,
                'lat': node.privacy_lat(current_user),
                'lng': node.privacy_lng(current_user),
            })

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


# Return all Links (Minimal dataset)
@bp.route('links/all', methods=['GET', 'POST'])
@login_required
def all_links():
    # Check user hasn't expired
    if not current_user.is_active:
        abort(403)

    # Defaults
    status = 'ERROR'
    errors = []
    data = {}

    # Get Node by ID
    serialized_links = []
    links = Link.query.all()
    if links:
        # serialize data
        for link in links:
            nodes = []
            for linked_node in link.nodes:
                nodes.append({
                    'id': linked_node.node.id,
                    'lat': linked_node.node.privacy_lat(current_user),
                    'lng': linked_node.node.privacy_lng(current_user),
                    'status_id': linked_node.node.status_id,
                })

            serialized_links.append({
                'id': link.id,
                'type': link.type,
                'nodes': nodes,
            })

        status = 'OK'
        data['links'] = serialized_links
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
