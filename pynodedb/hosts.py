from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
)
from flask_login import login_required, current_user

# import local modules
from .database import (
    Host,
)


# Define BLueprint
bp = Blueprint('hosts', __name__, url_prefix='/hosts')


@bp.route('/view/<id>', methods=['GET'])
@login_required
def view(id):
    if not current_user.is_active:
        return redirect(url_for('home'))

    host = Host.query.filter_by(id=id).first()

    return render_template('hosts/view.html', host=host)
