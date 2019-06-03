from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    abort,
    request,
    jsonify,
)
from flask_login import login_required, current_user

# import local modules
from . import functions as f
from .database import db, Node, Suburb, User, Status

# Define BLueprint
bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/', defaults={'filter': None, 'filter_id': None})
@bp.route('/<filter>/<filter_id>')
def list(filter=None, filter_id=None):
    if not current_user.is_active:
        return redirect(url_for('home'))

    page = request.args.get('page') or 1
    perpage = request.args.get('perpage') or 50
    pagination = None
    nodes = []
    sort = request.args.get('sort') or 'nodes.name'
    sort_direction = request.args.get('sort_direction') or 'asc'

    field_list = {
        'id': {
            'name': 'ID',
            'db_name': 'nodes.id',
        },
        'name': {
            'name': 'Name',
            'db_name': 'nodes.name',
        },
        'suburb': {
            'name': 'Suburb',
            'db_name': 'suburbs.name',
        },
        'manager': {
            'name': 'Manager',
            'db_name': 'users.name',
        },
        'status': {
            'name': 'Status',
            'db_name': 'statuses.name',
        },
        'region': {
            'name': 'Region',
            'db_name': 'nodes.region',
        },
        'zone': {
            'name': 'Zone',
            'db_name': 'nodes.zone',
        },
        'lat': {
            'name': 'Lat',
            'db_name': 'nodes.lat',
        },
        'lng': {
            'name': 'Lng',
            'db_name': 'nodes.lng',
        },
        'elevation': {
            'name': 'Elevation',
            'db_name': 'nodes.elevation',
        },
        'antenna_height': {
            'name': 'Antenna Height',
            'db_name': 'nodes.antHeight',
        },
        'bgp_as': {
            'name': 'BGP AS',
            'db_name': 'nodes.asNum',
        },
    }

    # Filter query as requested of return for this user
    if filter == 'all':
        page_title = f'All Nodes'
        nodes_query = Node.query.join(Suburb, User, Status).order_by(
            db.text(f'{sort} {sort_direction}'))
    elif filter == 'suburb':
        suburb = Suburb.query.filter_by(name=filter_id).first()
        page_title = f'Nodes in {suburb.name.title()} {suburb.state} {suburb.postcode}'
        nodes_query = Node.query.filter_by(
            suburb_id=suburb.id).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'user':
        user = User.query.filter_by(name=filter_id).first()
        page_title = f'Nodes Managed by {user.name}'
        nodes_query = Node.query.filter_by(
            user_id=user.id).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'status':
        status = Status.query.filter_by(name=filter_id).first()
        page_title = f'{status.name.title()} Nodes'
        nodes_query = Node.query.filter_by(
            status_id=status.id).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'region':
        region = filter_id
        page_title = f'Nodes in the {f.compass_to_name(region)} Region'
        nodes_query = Node.query.filter_by(
            region=region).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'zone':
        zone = filter_id
        page_title = f'Nodes in the {zone.title()} Zone'
        nodes_query = Node.query.filter_by(
            zone=zone).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    else:
        page_title = f'Your Nodes'
        nodes_query = Node.query.filter_by(
            user_id=current_user.id).join(Suburb, User, Status).order_by(db.text(f'{sort} {sort_direction}'))

    # Paginate results if required
    if page == 'all':
        nodes = nodes_query.all()
    else:
        pagination = nodes_query.paginate(int(page), int(perpage), False)
        nodes = pagination.items

    # Return template
    return render_template(
        'nodes/list.html',
        nodes=nodes,
        field_list=field_list,
        sort={'field': sort, 'direction': sort_direction},
        page=page,
        page_title=page_title,
        pagination=pagination,
    )


@bp.route('/all')
@login_required
def all():
    return list('all')


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    if not current_user.is_active:
        return redirect(url_for('home'))

    node = Node.query.filter_by(id=id).first()
    return render_template('nodes/view.html', node=node)
