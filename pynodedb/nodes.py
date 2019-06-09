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
from sqlalchemy.orm import noload, joinedload

# import local modules
from . import functions as f
from .database import (
    db,
    Node,
    Suburb,
    User,
    Status,
    Subnet,
    Host,
    Link,
    Interface,
)

# Define BLueprint
bp = Blueprint('nodes', __name__, url_prefix='/nodes')


@bp.route('/all', defaults={'filter': 'all', 'filter_id': None}, methods=(['POST', 'GET']))
@bp.route('/', defaults={'filter': None, 'filter_id': None}, methods=(['POST', 'GET']))
@bp.route('/<filter>/<filter_id>', methods=(['POST', 'GET']))
@login_required
def list(filter=None, filter_id=None):
    if not current_user.is_active:
        return redirect(url_for('home'))

    page = request.args.get('page') or 1
    perpage = request.args.get('perpage') or 50
    pagination = None
    nodes = []
    sort = request.args.get('sort') or 'nodes.name'
    sort_direction = request.args.get('sort_direction') or 'asc'

    search_query = request.form.get('search_query')
    search_filter = db.text('')
    if search_query:
        search_filter = db.or_(
            Node.id == f.safe_int(search_query),
            Node.name.like(f'%{search_query}%'),
            Suburb.name.like(f'{search_query}%'),
            User.name.like(f'{search_query}%'),
        )

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
            'extra_classes': 'hidden-xs hidden-sm',
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
            'extra_classes': 'hidden-xs hidden-sm hidden-md',
        },
        'zone': {
            'name': 'Zone',
            'db_name': 'nodes.zone',
            'extra_classes': 'hidden-xs hidden-sm hidden-md',
        },
        'lat': {
            'name': 'Lat',
            'db_name': 'nodes.lat',
            'extra_classes': 'hidden-xs',
        },
        'lng': {
            'name': 'Lng',
            'db_name': 'nodes.lng',
            'extra_classes': 'hidden-xs',
        },
        'elevation': {
            'name': 'Elevation',
            'db_name': 'nodes.elevation',
            'extra_classes': 'hidden-xs',
        },
        'antenna_height': {
            'name': 'Antenna Height',
            'db_name': 'nodes.antHeight',
            'extra_classes': 'hidden-xs',
        },
        'bgp_as': {
            'name': 'BGP AS',
            'db_name': 'nodes.asNum',
            'extra_classes': 'hidden-xs hidden-sm',
        },
    }

    # Filter query as requested of return for this user
    if filter == 'all':
        page_title = f'All Nodes'
        nodes_query = Node.query.join(Suburb, User, Status).filter(
            search_filter).order_by(db.text(f'{sort} {sort_direction}'))
    elif filter == 'suburb':
        suburb = Suburb.query.filter_by(name=filter_id).first()
        page_title = f'Nodes in {suburb.name.title()} {suburb.state} {suburb.postcode}'
        nodes_query = Node.query.filter(
            Suburb.id == suburb.id, search_filter).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'user':
        user = User.query.filter_by(name=filter_id).first()
        page_title = f'Nodes Managed by {user.name}'
        nodes_query = Node.query.filter(
            User.id == user.id, search_filter).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'status':
        status = Status.query.filter_by(name=filter_id).first()
        page_title = f'{status.name.title()} Nodes'
        nodes_query = Node.query.filter(
            Status.id == status.id, search_filter).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'region':
        region = filter_id
        page_title = f'Nodes in the {f.compass_to_name(region)} Region'
        nodes_query = Node.query.filter(
            Node.region == region, search_filter).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    elif filter == 'zone':
        zone = filter_id
        page_title = f'Nodes in the {zone.title()} Zone'
        nodes_query = Node.query.filter(
            Node.zone == zone, search_filter).join(Suburb, User, Status).order_by(
                db.text(f'{sort} {sort_direction}'))
    else:
        page_title = f'Your Nodes'
        nodes_query = Node.query.filter(
            User.id == current_user.id, search_filter
        ).join(Suburb, User, Status).order_by(db.text(f'{sort} {sort_direction}'))

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


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    if not current_user.is_active:
        return redirect(url_for('home'))

    node = Node.query.filter_by(id=id).first()

    # Build list of links
    aps = []
    bbs = []
    for host in node.hosts:
        for interface in host.interfaces:
            clients = []

            # Iterate AP links
            for interface_link in interface.links:
                # Get AP/Client link pair
                client_links = Link.query.filter_by(id=interface_link.link_id).all()
                for client_link in client_links:
                    # Iterate over AP/client link pair and pluck the client Node object
                    for client in client_link.nodes:
                        if client.node.id != node.id:
                            clients.append(client)

            link = {
                'host': host,
                'interface': interface,
                'clients': clients,
            }

            if interface.mode == 'AP':
                aps.append(link)
            elif interface.mode == 'BB' or interface.mode == 'CL':
                bbs.append(link)

            break

    return render_template('nodes/view.html', node=node, aps=aps, bbs=bbs)
