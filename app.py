from flask import Flask, render_template, request, redirect, url_for, session, g
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
import numpy as np
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "dermaglow_secret"

DATABASE = os.path.join(app.root_path, "database.db")
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

model = load_model("models/skin_model.keras")

classes = [
    "Dark Spots",
    "Acne",
    "Blackheads",
    "Whiteheads",
    "Pigmentation",
    "Pores",
    "Facial Redness",
    "Fine Lines",
    "Eye Bags",
    "Sunburn"
]

recommendations = {
    "Dark Spots": [
        "Use a vitamin C serum every morning to brighten dark spots.",
        "Apply aloe vera gel with a few drops of lemon juice for gentle fading.",
        "Wear broad-spectrum SPF 30+ daily to prevent new discoloration.",
        "Incorporate niacinamide into your routine to even skin tone.",
        "Use a gentle exfoliant once a week to remove dead skin cells."
    ],
    "Acne": [
        "Cleanse twice daily with a gentle, salicylic acid formula.",
        "Use tea tree oil as a spot treatment on active blemishes.",
        "Keep skin hydrated with a non-comedogenic moisturizer.",
        "Avoid touching or picking at acne to prevent irritation.",
        "Support skin health with plenty of water and a balanced diet."
    ],
    "Blackheads": [
        "Steam your face before cleansing to soften blackheads.",
        "Use a clay mask weekly to draw out impurities.",
        "Try a BHA exfoliant to clear pores gently.",
        "Keep pillowcases and towels clean to reduce oil buildup.",
        "Avoid heavy creams that can clog pores further."
    ],
    "Whiteheads": [
        "Apply a warm compress to soften whiteheads before cleansing.",
        "Use a gentle exfoliator to help clear blocked pores.",
        "Choose oil-free skincare products to prevent further buildup.",
        "Use a lightweight moisturizer to balance hydration.",
        "Consider benzoyl peroxide or sulfur treatments for stubborn areas."
    ],
    "Pigmentation": [
        "Apply sunscreen every morning to protect against UV damage.",
        "Use vitamin C serum to brighten and fade discoloration.",
        "Try niacinamide to improve tone and texture.",
        "Reveal fresh skin with gentle exfoliation once a week.",
        "Soothe skin with aloe vera after sun exposure."
    ],
    "Pores": [
        "Use a clay mask once a week to minimize pore appearance.",
        "Apply niacinamide toner to help tighten and refine pores.",
        "Rinse with cold water or use an ice cube massage for a quick refresh.",
        "Avoid heavy makeup that can trap oil in pores.",
        "Keep skin clean and hydrated with lightweight, non-comedogenic products."
    ],
    "Facial Redness": [
        "Soothe skin with chilled cucumber slices or chamomile compresses.",
        "Use fragrance-free, calming moisturizers to reduce irritation.",
        "Avoid harsh active ingredients until redness subsides.",
        "Apply a cool compress after heat or sun exposure.",
        "Protect skin barrier with gentle, moisturizing products."
    ],
    "Fine Lines": [
        "Apply a retinol or bakuchiol product at night to support collagen.",
        "Keep skin well-hydrated with a rich moisturizer.",
        "Use sunscreen daily to prevent further photoaging.",
        "Massage the face gently to support circulation.",
        "Add an antioxidant serum to help protect skin from free radicals."
    ],
    "Eye Bags": [
        "Place chilled green tea bags or cold spoons on the eyes.",
        "Use a caffeine eye cream to help reduce puffiness.",
        "Sleep with your head slightly elevated to improve drainage.",
        "Stay hydrated and reduce excess salt before bed.",
        "Gently massage the under-eye area to stimulate circulation."
    ],
    "Sunburn": [
        "Apply cool aloe vera gel to calm and hydrate sunburned skin.",
        "Use cool compresses to reduce heat and discomfort.",
        "Moisturize with a gentle, fragrance-free lotion.",
        "Avoid further sun exposure until skin heals fully.",
        "Drink plenty of fluids to support skin recovery."
    ],
}

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Create users table if it doesn't exist
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            age INTEGER,
            profile_image TEXT,
            created_at TEXT
        )
        """
    )

    # Create predictions history table
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image TEXT,
            disease TEXT,
            remedy TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    # Ensure columns exist for older databases (safe ALTERs)
    cur = db.execute("PRAGMA table_info(users)").fetchall()
    cols = [r[1] for r in cur]
    if 'age' not in cols:
        try:
            db.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        except Exception:
            pass
    if 'profile_image' not in cols:
        try:
            db.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
        except Exception:
            pass

    db.commit()


def get_user_by_email(email):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user_by_id(user_id):
    if not user_id:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def current_user():
    user_id = session.get('user_id')
    return get_user_by_id(user_id) if user_id else None


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return render_template('login.html', error='Please enter both email and password.')

        user = get_user_by_email(email)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            return redirect(url_for('home'))

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        age = request.form.get('age', '').strip()

        if not name or not email or not password:
            return render_template('register.html', error='Name, email and password are required.')

        if get_user_by_email(email):
            return render_template('register.html', error='That email is already registered.')

        # store optional age if provided
        age_value = None
        try:
            age_value = int(age) if age else None
        except ValueError:
            return render_template('register.html', error='Age must be a number.')

        db = get_db()
        cursor = db.execute(
            "INSERT INTO users (name, email, password, age, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (name, email, password, age_value)
        )
        db.commit()
        session['user_id'] = cursor.lastrowid
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        file = request.files.get('profile_image')

        if not name:
            return render_template('profile.html', error='Name is required.', user=user)

        age_value = None
        try:
            age_value = int(age) if age else None
        except ValueError:
            return render_template('profile.html', error='Age must be a whole number.', user=user)

        profile_image_filename = user['profile_image'] if user and 'profile_image' in user.keys() else None
        if file and file.filename:
            if allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                profile_image_filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, profile_image_filename))
            else:
                return render_template('profile.html', error='Profile image must be PNG/JPG/JPEG.', user=user)

        db = get_db()
        db.execute(
            "UPDATE users SET name = ?, age = ?, profile_image = ? WHERE id = ?",
            (name, age_value, profile_image_filename, user['id'])
        )
        db.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/home')
def home():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    history = db.execute(
        "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC",
        (user['id'],)
    ).fetchall()
    return render_template('home.html', user=user, history=history)


@app.route('/predict', methods=['POST'])
def predict():
    user = current_user()
    if not user:
        return redirect(url_for('login'))

    file = request.files.get('image')
    if not file or file.filename == '':
        return render_template('home.html', user=user, error='Please upload an image to analyze.')

    if not allowed_file(file.filename):
        return render_template('home.html', user=user, error='Please upload a PNG, JPG, or JPEG image.')

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    img = image.load_img(filepath, target_size=(224, 224))
    img = image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)
    index = int(np.argmax(prediction[0]))
    disease = classes[index] if index < len(classes) else 'Skin concern'
    remedy = recommendations.get(disease, [
        "Keep skin hydrated and protected from the sun.",
        "Use gentle, fragrance-free products to avoid irritation.",
        "Avoid picking or irritating the affected area.",
        "Apply sunscreen daily to support healing and prevention.",
        "Consult a dermatologist if symptoms persist or worsen."
    ])

    image_url = url_for('static', filename=f'uploads/{filename}')

    # Save prediction history for the user
    try:
        db = get_db()
        db.execute(
            "INSERT INTO predictions (user_id, image, disease, remedy, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (user['id'], filename, disease, "\n".join(remedy))
        )
        db.commit()
    except Exception:
        # non-fatal: ignore history saving errors
        pass

    return render_template('result.html', disease=disease, image_url=image_url, remedy=remedy)


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
