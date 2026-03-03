import os
from werkzeug.utils import secure_filename
from models import db, User, Dish, Category
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_villanos' # Cambia esto a algo más seguro en el futuro
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
# Configuración para subida de imágenes
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

# Función para verificar que el archivo sea una imagen válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Redirige aquí si intentan entrar al panel sin sesión

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inicializar base de datos y crear admin por defecto
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password=generate_password_hash('1234'))
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
def index():
    # Enviamos las categorías. El HTML se encargará de filtrar los platos activos.
    categorias = Category.query.all()
    return render_template('index.html', categorias=categorias, nombre_local="Los Villanos")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya inició sesión, lo mandamos directo al panel
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Verificamos si el usuario existe y la contraseña coincide
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
        
        # --- LÓGICA DE LA IMAGEN ---
        image_file = request.files.get('image') # Capturamos el archivo del formulario
        filename = None
        
        # Si enviaron un archivo y tiene una extensión válida
        if image_file and allowed_file(image_file.filename):
            # secure_filename limpia el nombre (ej: "Mi foto!!.jpg" -> "Mi_foto.jpg")
            filename = secure_filename(image_file.filename) 
            # Guardamos el archivo físico en la carpeta
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # ---------------------------
        
        nuevo_plato = Dish(
            name=name, 
            category_id=category_id, 
            price=price, 
            description=description,
            image_file=filename # Guardamos el nombre en la BD
        )
        db.session.add(nuevo_plato)
        db.session.commit()
        
        flash('Plato agregado exitosamente', 'success')
        return redirect(url_for('admin'))

    platos = Dish.query.all()
    categorias = Category.query.all() # Obtenemos las categorías
    return render_template('admin.html', platos=platos, categorias=categorias)
    if request.method == 'POST':
        # Capturamos los datos que vienen del formulario HTML
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        description = request.form.get('description')
        
        # Creamos el nuevo plato y lo guardamos en la base de datos
        nuevo_plato = Dish(name=name, category=category, price=price, description=description)
        db.session.add(nuevo_plato)
        db.session.commit()
        
        flash('Plato agregado exitosamente', 'success')
        return redirect(url_for('admin')) # Recargamos la página para ver el plato nuevo

    # Obtenemos los 3 platos con más vistas, ordenados de mayor a menor
    top_platos = Dish.query.order_by(Dish.views.desc()).limit(3).all()
    
    # Recuerda agregar top_platos al return
    return render_template('admin.html', platos=platos, categorias=categorias, top_platos=top_platos)


# Ruta para editar un plato existente
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    plato = Dish.query.get_or_404(id)
    
    if request.method == 'POST':
        plato.name = request.form.get('name')
        plato.category_id = request.form.get('category_id') # CORRECCIÓN: Ahora es category_id
        plato.price = request.form.get('price')
        plato.description = request.form.get('description')
        plato.is_active = True if request.form.get('is_active') == 'on' else False
        
        # --- LÓGICA DE LA IMAGEN AL EDITAR ---
        image_file = request.files.get('image')
        # Solo guardamos y sobreescribimos si el usuario subió un archivo nuevo
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            plato.image_file = filename 
        # -------------------------------------
        
        db.session.commit()
        flash('Plato actualizado correctamente', 'success')
        return redirect(url_for('admin'))
        
    # CORRECCIÓN: Buscamos las categorías y se las enviamos al HTML
    categorias = Category.query.all()
    return render_template('edit.html', plato=plato, categorias=categorias, nombre_local="Los Villanos")
    plato = Dish.query.get_or_404(id)
    
    if request.method == 'POST':
        plato.name = request.form.get('name')
        plato.category = request.form.get('category_id')
        plato.price = request.form.get('price')
        plato.description = request.form.get('description')
        
        # Capturamos el switch. Si viene 'on', es True. Si viene None, es False.
        plato.is_active = True if request.form.get('is_active') == 'on' else False
        
        db.session.commit()
        flash('Plato actualizado correctamente', 'success')
        return redirect(url_for('admin'))
        
    return render_template('edit.html', plato=plato, nombre_local="Los Villanos")

# Ruta para eliminar un plato
@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    plato = Dish.query.get_or_404(id)
    db.session.delete(plato)
    db.session.commit()
    flash('Plato eliminado del menú', 'danger')
    return redirect(url_for('admin'))

# --- RUTAS DE CATEGORÍAS ---

@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    if request.method == 'POST':
        name = request.form.get('name')
        
        # Pequeña validación para no crear categorías duplicadas
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

@app.route('/api/view/<int:id>', methods=['POST'])
def track_view(id):
    plato = Dish.query.get(id)
    if plato:
        plato.views += 1
        db.session.commit()
        return {'status': 'success'}
    return {'status': 'error'}, 404


if __name__ == '__main__':
    app.run(debug=True)