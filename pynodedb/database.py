from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy_serializer import SerializerMixin

from . import functions as f

db = SQLAlchemy()

# Many to Many helper tables
link_node = db.Table('link_node',
                     db.Column('link_id', INTEGER(unsigned=True), db.ForeignKey(
                         'links.id'), primary_key=True),
                     db.Column('node_id', INTEGER(unsigned=True), db.ForeignKey(
                         'nodes.id'), primary_key=True),
                     )

node_subnet = db.Table('node_subnet',
                       db.Column('subnet_id', INTEGER(unsigned=True), db.ForeignKey(
                           'subnets.id'), primary_key=True),
                       db.Column('node_id', INTEGER(unsigned=True), db.ForeignKey(
                           'nodes.id'), primary_key=True),
                       )

group_user = db.Table('group_user',
                      db.Column('group_id', INTEGER(unsigned=True), db.ForeignKey(
                          'groups.id'), primary_key=True),
                      db.Column('user_id', INTEGER(unsigned=True), db.ForeignKey(
                          'users.id'), primary_key=True),
                      )


# Define tables
class Node(db.Model, SerializerMixin):
    __tablename__ = 'nodes'

    # Columns
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
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
    suburb_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('suburbs.id'))
    user_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('users.id'))
    status_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('statuses.id'))

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
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
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
    id = db.Column(INTEGER(unsigned=True), nullable=False,
                   primary_key=True, autoincrement=False)
    name = db.Column(db.String(255))
    firstname = db.Column(db.String(255))
    surname = db.Column(db.String(255))
    email = db.Column(db.String(255))
    secondary_email = db.Column(db.String(255))
    joined_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Relationships
    nodes = db.relationship('Node', backref='user', lazy=True)

    # Many to many
    groups = db.relationship('Group', secondary=group_user,
                             lazy='subquery',
                             backref=db.backref('groups', lazy=True),
                             )

    def __repr__(self):
        return f'<UserName {self.name}>'

    # Check if user is active
    @property
    def is_active(self):
        if self.expires_at > datetime.now():
            return True
        return False

    # A logged in user is authenticated
    @property
    def is_authenticated(self):
        return True

    # A logged in user can't be anonymous
    @property
    def is_anonymous(self):
        return False

    # Return user_id as a Unicode string
    def get_id(self):
        return f'{self.id}'

    # Return User object based on user_id
    def get(id):
        user = User.query.get(id)
        return user

    # Determine if user is in a group by group_id
    def in_group(self, group_id):
        for group in self.groups:
            if group.id == group_id:
                return True

        return False


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(INTEGER(unsigned=True), nullable=False,
                   primary_key=True, autoincrement=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<GroupName {self.name}>'


class Status(db.Model):
    __tablename__ = 'statuses'

    # Columns
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
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
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
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
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
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
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
    name = db.Column(db.String(255))
    fqdn = db.Column(db.String(255))
    addr = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Foreign Keys
    node_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('nodes.id'))
    subnet_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('subnets.id'))

    def __repr__(self):
        return f'<HostAddr {self.addr}>'


# OAuth token storage
class OAuthToken(db.Model):
    __tablename__ = 'oauth_tokens'

    user_id = db.Column(INTEGER(unsigned=True), nullable=False, primary_key=True)

    token_type = db.Column(db.String(20))
    access_token = db.Column(db.String(2048), nullable=False)
    refresh_token = db.Column(db.String(1024))
    expires_at = db.Column(db.Integer, default=0)

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    def __repr__(self):
        return f'<UserId {self.user_id}>'
