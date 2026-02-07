from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('El correo electrónico ya está registrado.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check if it's the first user to make it admin (optional logic, hard to check count efficiently without extra query)
        # Simplified: just create user. Admin must be set in DB manually or via logic
        
        new_user = User.create(email=email, password=password)
        
        if new_user:
            flash('Cuenta creada exitosamente. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error al crear la cuenta. Inténtalo de nuevo.', 'danger')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
