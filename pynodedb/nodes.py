import pynodedb.functions as f
from pynodedb.database import Node

from flask import (
    Blueprint, render_template
)


bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/', methods=['GET'])
def node_list():
    nodes = Node.query.all()

    return render_template('nodes/nodes.html', nodes=nodes)


@bp.route('/view/<id>', methods=['GET'])
def view_node(id):
    node = Node.query.filter_by(id=id).first()

    return render_template('nodes/view_node.html', node=node)
