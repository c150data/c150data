"""
Handles the admin page, specifically adding the database table views
"""
from flask_admin import Admin, AdminIndexView
from app import app, db
from app.database.db_models import User, Athlete, Workout, AuthToken, PrescribedTrainingDay
from flask import redirect, url_for, flash, request, render_template
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Landing admin page
        """
        if current_user.is_authenticated:
            return current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Please login as an administrator to access Admin pages', 'danger')
        return redirect(url_for('users.login'))


class AdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('users.login'), next=request.url)


admin = Admin(app, name='Admin Dashboard', index_view=MyAdminIndexView(
    template='admin/home.html'), template_mode='bootstrap3')

admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Athlete, db.session))
admin.add_view(AdminView(Workout, db.session))
admin.add_view(AdminView(AuthToken, db.session))
admin.add_view(AdminView(PrescribedTrainingDay, db.session))
