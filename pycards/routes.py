from flask import Blueprint, request, redirect, url_for, render_template
from .models import get_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    db = get_db()
    cur = db.execute('SELECT content FROM excerpts')
    excerpts = cur.fetchall()
    return render_template('home.html', excerpts=[row[0] for row in excerpts])

@main_bp.route('/submit', methods=['POST'])
def submit():
    excerpt = request.form['excerpt']
    if excerpt:
        db = get_db()
        db.execute('INSERT INTO excerpts (content) VALUES (?)', [excerpt])
        db.commit()
    return redirect(url_for('main.home'))

@main_bp.route('/excerpts')
def show_excerpts():
    db = get_db()
    cur = db.execute('SELECT content FROM excerpts')
    excerpts = cur.fetchall()
    return render_template('excerpts.html', excerpts=[row[0] for row in excerpts])