from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# import local modules
from . import functions as f
from .database import Node

# Define BLueprint
bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/', methods=['GET'])
@login_required
def list():
    nodes = current_user.nodes
    return render_template('nodes/nodes.html', nodes=nodes)


@bp.route('/all', methods=['GET'])
@login_required
def all():
    if current_user.in_group(3):
        nodes = Node.query.all()
        return render_template('nodes/nodes.html', nodes=nodes)

    return redirect(url_for('home')), 403


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    node = Node.query.filter_by(id=id).first()
    return render_template('nodes/view_node.html', node=node)
