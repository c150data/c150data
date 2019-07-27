from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps

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
