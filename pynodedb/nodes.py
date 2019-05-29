from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    abort,
    request,
)
from flask_login import login_required, current_user

# import local modules
from . import functions as f
from .database import Node

# Define BLueprint
bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/', methods=['GET'])
@login_required
def list():
    if not current_user.is_active:
        return redirect(url_for('home'))

    nodes = Node.query.filter_by(
        user_id=current_user.id).order_by('name').all()
    return render_template('nodes/list.html', nodes=nodes)


@bp.route('/all', methods=['GET'])
@login_required
def all():
    if current_user.in_group(3) and current_user.is_active:
        page = request.args.get('page')
        perpage = request.args.get('perpage') or 50
        pagination = None
        nodes = []

        if page:
            pagination = Node.query.order_by('name').paginate(
                int(page), int(perpage), False)
            nodes = pagination.items
        else:
            nodes = Node.query.order_by('name').all()

        return render_template('nodes/list.html', nodes=nodes, pagination=pagination)

    return abort(403)


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    if not current_user.is_active:
        return redirect(url_for('home'))

    node = Node.query.filter_by(id=id).first()
    return render_template('nodes/view.html', node=node)
