from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from auth.service import AuthService
from utils.security import is_authenticated

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Renders registration view and handles account creation POST requests."""
    if is_authenticated():
        return redirect(url_for('chat_view'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        success, message, user = AuthService.register_user(username, password, confirm_password)
        if success and user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(message, 'success')
            return redirect(url_for('chat_view'))

        flash(message, 'error')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Renders login view and handles authentication POST requests."""
    if is_authenticated():
        return redirect(url_for('chat_view'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        success, message, user = AuthService.authenticate_user(username, password)
        if success and user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash(message, 'success')
            return redirect(url_for('chat_view'))

        flash(message, 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logs out current user by clearing session."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))
