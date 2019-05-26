from flask import Blueprint, url_for, redirect, request
from authlib.flask.client import OAuth
from flask_login import (
    login_user, logout_user, login_required, AnonymousUserMixin
)

# import local modules
from . import functions as f
from . import database


oauth = OAuth()
bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.remote.authorize_redirect(redirect_uri)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@bp.route('/oauth/authorize')
def authorize():
    # Check for errors
    if request.args.getlist('error'):
        return request.args.getlist('error')[0]

    token = oauth.remote.authorize_access_token()

    # Get user profile
    user_response = oauth.remote.get('user')
    user_data = user_response.json()
    save_user_profile(user_data)
    user_id = user_data['id']

    # Save user token
    user_token = database.OAuthToken.query.get(user_id)
    if user_token is None:
        user_token = database.OAuthToken(user_id=user_id)
        database.db.session.add(user_token)

    user_token.token_type = token['token_type']
    user_token.access_token = token['access_token']
    user_token.refresh_token = token['refresh_token']
    user_token.expires_at = token['expires_at']

    database.db.session.commit()

    # Log user in
    user = database.User.query.get(user_data['id'])
    login_user(user, remember=True)

    return redirect(url_for('home'))


# Save user profile to database
def save_user_profile(user_data):
    # Update user
    user = database.User.query.get(user_data['id'])
    if user is None:
        user = database.User()
        database.db.session.add(user)

    user.id = user_data['id']
    user.name = user_data['username']
    user.firstname = user_data['firstname']
    user.surname = user_data['surname']
    user.email = f"{user_data['username']}@air-stream.org"
    user.secondary_email = user_data['email']
    user.joined_at = user_data['joined_at']
    user.expires_at = user_data['expires_at']
    user.created_at = user_data['created_at']
    user.updated_at = user_data['updated_at']

    # Update groups
    for group_data in user_data['groups']:
        group = database.Group.query.get(group_data['id'])
        if group is None:
            group = database.Group()
            database.db.session.add(group)

        group.id = group_data['id']
        group.name = group_data['name']
        group.created_at = group_data['created_at']
        group.updated_at = group_data['updated_at']

        # Add group to user
        user.groups.append(group)

    # Save to database
    database.db.session.commit()


# Defne Anonymous User atttibutes
class AnonymousUser(AnonymousUserMixin):
    @property
    def name(self):
        return 'Anonymous'
