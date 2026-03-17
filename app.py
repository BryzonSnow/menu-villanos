import os
from werkzeug.utils import secure_filename
from models import db, User, Dish, Category, Configuracion
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_villanos'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads' #cambiar en produccion
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
    # Usuario por defecto
    if not User.query.filter_by(username='demo_admin').first():
        clave_segura = generate_password_hash('demo1234')
        nuevo_usuario = User(username='demo_admin', password=clave_segura)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
 # Configuración por defecto del WhatsApp
    if not Configuracion.query.first():
        config_inicial = Configuracion(
            whatsapp_numero="56964257112", 
            whatsapp_mensaje="Hola! Estaba viendo el menú digital y me gustaría hacer un pedido.",
            whatsapp_activo=True
        )
        db.session.add(config_inicial)
        db.session.commit()

@app.route('/')
def index():
    categorias = Category.query.all()
    config = Configuracion.query.first()
    return render_template('index.html', categorias=categorias, config=config, nombre_local="Los Villanos")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            
    return render_template('login.html', nombre_local="Los Villanos")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        description = request.form.get('description')
        
        precio_socio_str = request.form.get('precio_socio')
        precio_socio = int(precio_socio_str) if precio_socio_str and precio_socio_str.strip() != '' else None
        
        image_file = request.files.get('image')
        filename = None
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename) 
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        nuevo_plato = Dish(
            name=name, 
            category_id=category_id, 
            price=price, 
            precio_socio=precio_socio,
            description=description,
            image_file=filename
        )
        db.session.add(nuevo_plato)
        db.session.commit()
        
        flash('Plato agregado exitosamente', 'success')
        return redirect(url_for('admin'))

    platos = Dish.query.all()
    categorias = Category.query.all()
    config = Configuracion.query.first()
    return render_template('admin.html', platos=platos, categorias=categorias, config=config)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    plato = Dish.query.get_or_404(id)
    
    if request.method == 'POST':
        plato.name = request.form.get('name')
        plato.category_id = request.form.get('category_id')
        plato.price = request.form.get('price')
        plato.description = request.form.get('description')
        plato.is_active = True if request.form.get('is_active') == 'on' else False
        
        precio_socio_str = request.form.get('precio_socio')
        plato.precio_socio = int(precio_socio_str) if precio_socio_str and precio_socio_str.strip() != '' else None
        
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            plato.image_file = filename 
        
        db.session.commit()
        flash('Plato actualizado correctamente', 'success')
        return redirect(url_for('admin'))
        
    categorias = Category.query.all()
    return render_template('edit.html', plato=plato, categorias=categorias, nombre_local="Los Villanos")

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    plato = Dish.query.get_or_404(id)
    db.session.delete(plato)
    db.session.commit()
    flash('Plato eliminado del menú', 'danger')
    return redirect(url_for('admin'))

@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    if request.method == 'POST':
        name = request.form.get('name')
        categoria_existente = Category.query.filter_by(name=name).first()
        if categoria_existente:
            flash('Esa categoría ya existe.', 'warning')
        else:
            nueva_categoria = Category(name=name)
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría creada exitosamente.', 'success')
        return redirect(url_for('categorias'))

    categorias = Category.query.all()
    return render_template('categorias.html', categorias=categorias, nombre_local="Los Villanos")

@app.route('/delete_categoria/<int:id>', methods=['POST'])
@login_required
def delete_categoria(id):
    categoria = Category.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada.', 'danger')
    return redirect(url_for('categorias'))

# --- NUEVA RUTA DE CONFIGURACIÓN WHATSAPP ---
@app.route('/configuracion', methods=['GET', 'POST'])
@login_required
def configuracion():
    config = Configuracion.query.first()
    if request.method == 'POST':
        config.whatsapp_numero = request.form.get('whatsapp_numero')
        config.whatsapp_mensaje = request.form.get('whatsapp_mensaje') 
        config.whatsapp_activo = 'whatsapp_activo' in request.form 
        db.session.commit()
        flash('Configuración guardada exitosamente.', 'success')
        return redirect(url_for('configuracion'))
        
    return render_template('configuracion.html', config=config, nombre_local="Los Villanos")
if __name__ == '__main__':
    app.run(debug=True)