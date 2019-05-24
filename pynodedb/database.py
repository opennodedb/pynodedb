from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Many to Many helper tables
link_node = db.Table('link_node',
                     db.Column('link_id', db.Integer, db.ForeignKey(
                         'links.id'), primary_key=True),
                     db.Column('node_id', db.Integer, db.ForeignKey(
                         'nodes.id'), primary_key=True),
                     )

node_subnet = db.Table('node_subnet',
                       db.Column('subnet_id', db.Integer, db.ForeignKey(
                           'subnets.id'), primary_key=True),
                       db.Column('node_id', db.Integer, db.ForeignKey(
                           'nodes.id'), primary_key=True),
                       )


class Node(db.Model):
    __tablename__ = 'nodes'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    region = db.Column(db.String(64))
    zone = db.Column(db.String(64))
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    elevation = db.Column(db.Float, nullable=True)
    antenna_height = db.Column('antHeight', db.Float, nullable=True)
    bgp_as = db.Column('asNum', db.Integer, nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Foreign Keys
    suburb_id = db.Column(db.Integer, db.ForeignKey('suburbs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))

    # Relationships
    hosts = db.relationship('Host', backref='hosts', lazy=True)

    # Many to many
    links = db.relationship('Link', secondary=link_node,
                            lazy='subquery',
                            backref=db.backref('links', lazy=True),
                            )
    subnets = db.relationship('Subnet', secondary=node_subnet,
                              lazy='subquery',
                              backref=db.backref('subnets', lazy=True),
                              )

    def __repr__(self):
        return f'<NameName {self.name}>'


class Suburb(db.Model):
    __tablename__ = 'suburbs'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    state = db.Column(db.String(255))
    postcode = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Relationships
    nodes = db.relationship('Node', backref='suburb', lazy=True)

    def __repr__(self):
        return f'<UserName {self.name}>'


class User(db.Model):
    __tablename__ = 'users'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Relationships
    nodes = db.relationship('Node', backref='user', lazy=True)

    def __repr__(self):
        return f'<UserName {self.name}>'


class Status(db.Model):
    __tablename__ = 'statuses'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Relationships
    nodes = db.relationship('Node', backref='status', lazy=True)

    def __repr__(self):
        return f'<UserName {self.name}>'


class Link(db.Model):
    __tablename__ = 'links'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(64))
    freq = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<LinkName {self.name}>'


class Subnet(db.Model):
    __tablename__ = 'subnets'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.Integer)
    mask = db.Column(db.Integer)
    type = db.Column(db.String(64))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Relationships
    hosts = db.relationship('Host', backref='status', lazy=True)

    def __repr__(self):
        return f'<SubnetAddr {self.addr}/{self.mask}>'


class Host(db.Model):
    __tablename__ = 'hosts'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    fqdn = db.Column(db.String(255))
    addr = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Foreign Keys
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    subnet_id = db.Column(db.Integer, db.ForeignKey('subnets.id'))

    def __repr__(self):
        return f'<SubnetAddr {self.addr}/{self.mask}>'
