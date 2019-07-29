from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from app import login_manager
from app.database.db_models import User

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to view this site', 'danger')
                return redirect(url_for('users.login'))

            elif not current_user.allowed(access_level):
                flash(
                    'You do not have the right priviledges to access this page.', 'danger')
                return redirect(url_for('main.about'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# LUKAS: What is this and should it be in this file? It doesn't seem to fit with the rest of what is going on
# Max: Yes, because we have to tell login manager what user is currently active.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))