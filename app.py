from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from db import Database

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
db = Database()

# Sample data initialization
with app.app_context():
    if not db.get_all_users():
        db.create_user('alice', 'Alice Smith')
        db.create_user('bob', 'Bob Johnson')
        db.create_user('charlie', 'Charlie Brown')

# ======================
# API Endpoints
# ======================

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(db.get_all_users())

@app.route('/api/users/<username>', methods=['GET'])
def api_get_user(username):
    user = db.get_user(username)
    return jsonify(user) if user else ('User not found', 404)

# ======================
# Frontend Routes
# ======================

@app.route('/')
def home():
    users = db.get_all_users()
    current_user = None
    if 'username' in session:
        current_user = db.get_user(session['username'])
    return render_template('index.html', users=users, current_user=current_user)

@app.route('/user/<username>')
def user_profile(username):
    user = db.get_user(username)
    if not user:
        return "User not found", 404

    current_user = None
    is_following = False

    if 'username' in session:
        current_user = db.get_user(session['username'])
        if current_user and current_user['username'] != username:
            following = db.get_following(current_user['username'])
            is_following = any(f['username'] == username for f in following)

    posts = db.get_posts_by_user(username)
    followers = db.get_followers(username)
    following = db.get_following(username)

    return render_template('profile.html',
                           user=user,
                           posts=posts,
                           followers=followers,
                           following=following,
                           current_user=current_user,
                           is_following=is_following)

@app.route('/user/<username>/feed')
def user_feed(username):
    user = db.get_user(username)
    feed = db.get_feed(username)
    return render_template('feed.html', user=user, feed=feed)

@app.route('/create_post', methods=['POST'])
def create_post():
    username = request.form['username']
    content = request.form['content']
    db.create_post(username, content)
    return redirect(url_for('user_profile', username=username))

@app.route('/login/<username>')
def login(username):
    session['username'] = username
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/follow', methods=['POST'])
def follow():
    follower = request.form['follower_username']
    followee = request.form['followee_username']

    following = db.get_following(follower)
    is_following = any(f['username'] == followee for f in following)

    if is_following:
        db.unfollow_user(follower, followee)
    else:
        db.follow_user(follower, followee)

    return redirect(url_for('user_profile', username=followee))

# ======================
# HTML Templates
# ======================
@app.route('/templates/<template_name>')
def serve_template(template_name):
    return render_template(template_name)

# Jinja global renderers (if still needed)
app.jinja_env.globals.update(
    render_index=lambda: render_template('index.html', users=db.get_all_users()),
    render_profile=lambda username: render_template(
        'profile.html',
        user=db.get_user(username),
        posts=db.get_posts_by_user(username),
        followers=db.get_followers(username),
        following=db.get_following(username)
    )
)

if __name__ == '__main__':
    app.run(debug=True)