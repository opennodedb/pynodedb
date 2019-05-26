from flask import Blueprint, render_template
from flask_login import login_required

# import local modules
from .database import Node


bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/', methods=['GET'])
@login_required
def list():
    nodes = Node.query.all()

    return render_template('nodes/nodes.html', nodes=nodes)


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    node = Node.query.filter_by(id=id).first()

    return render_template('nodes/view_node.html', node=node)
