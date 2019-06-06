from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy_serializer import SerializerMixin

from . import functions as f

db = SQLAlchemy()


# Many to Many helper tables
class LinkNode(db.Model):
    __tablename__ = 'link_node'

    link_id = db.Column(INTEGER(unsigned=True), db.ForeignKey(
        'links.id'), primary_key=True)
    node_id = db.Column(INTEGER(unsigned=True), db.ForeignKey(
        'nodes.id'), primary_key=True)
    interface_id = db.Column(INTEGER(unsigned=True), db.ForeignKey(
        'interfaces.id'))

    # Relationships
    link = db.relationship("Link", back_populates="nodes", lazy=True)
    node = db.relationship("Node", back_populates="links", lazy=True)
    interface = db.relationship("Interface", lazy=True)
    db.relationship("Interface", back_populates="links", lazy=True)
    db.relationship("Interface", back_populates="nodes", lazy=True)


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
    links = db.relationship('LinkNode', back_populates="node", lazy=True)
    subnets = db.relationship('Subnet', secondary=node_subnet,
                              lazy='subquery',
                              backref=db.backref('subnets', lazy=True),
                              )

    # Psuedo-randomise location of Node
    def privacy_lat(self, user):
        lat = float(f'{self.lat:.2f}') + self.id / 100000
        if user.id == self.user_id or user.in_group(3):
            lat = self.lat
        return lat

    # Psuedo-randomise location of Node
    def privacy_lng(self, user):
        lng = float(f'{self.lng:.2f}') + self.id / 100000
        if user.id == self.user_id or user.in_group(3):
            lng = self.lng
        return lng

    def __repr__(self):
        return f'<NodeName {self.name}>'


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
        expires_at = self.expires_at or datetime.fromtimestamp(0)

        if expires_at > datetime.now():
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


class Link(db.Model, SerializerMixin):
    __tablename__ = 'links'

    # Columns
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
    name = db.Column(db.String(255))
    type = db.Column(db.String(64))
    freq = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Many to many
    nodes = db.relationship('LinkNode', back_populates="link", lazy=True)

    def __repr__(self):
        return f'<LinkName {self.name}>'


class Subnet(db.Model, SerializerMixin):
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
    hosts = db.relationship('Host', backref='subnet', lazy=True)

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

    # Relationships
    interfaces = db.relationship('Interface', backref='host', lazy=True)
    host_aliases = db.relationship('HostAlias', backref='host', lazy=True)

    def __repr__(self):
        return f'<HostAddr {self.addr}>'


class HostAlias(db.Model):
    __tablename__ = 'host_aliases'

    # Columns
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Foreign Keys
    host_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('hosts.id'))

    def __repr__(self):
        return f'<HostALiasName {self.name}>'


class Interface(db.Model):
    __tablename__ = 'interfaces'

    # Columns
    id = db.Column(INTEGER(unsigned=True),
                   primary_key=True, autoincrement=False)
    type = db.Column(db.String(64))
    ssid = db.Column(db.String(255))
    mode = db.Column(db.String(64))
    protocol = db.Column(db.String(64))
    freq = db.Column(INTEGER(unsigned=True))
    passphrase = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    # Foreign Keys
    host_id = db.Column(INTEGER(unsigned=True), db.ForeignKey('hosts.id'))

    # Many to Many
    links = db.relationship('LinkNode', lazy=True)
    nodes = db.relationship('LinkNode', lazy=True)

    def __repr__(self):
        return f'<InterfaceType {self.type}>'


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
