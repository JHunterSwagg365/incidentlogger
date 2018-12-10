import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request,abort
from incidentlogger import app, db, bcrypt
from incidentlogger.forms import RegistrationForm, LoginForm, IncidentForm, UpdateAccountForm
from incidentlogger.models import User, Incident
from flask_login import login_user, current_user, logout_user, login_required

categories = ['Technology']

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Incident.query.order_by(Incident.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Try again', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/incident/create", methods=['GET', 'POST'])
@login_required
def incident():
    form = IncidentForm()
    if form.validate_on_submit():
        post = Incident(contact= current_user.username ,category= form.category.data,title=form.title.data, content=form.content.data, state='Inactive' ,tags=form.tags.data , current_assignee=' ' , history="Created by " + current_user.username,author=current_user)
        if form.category.data not in  categories:
            categories.append(form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('incident.html', title='New Incident',
                           form=form, categories=categories ,legend='New Incident')


@app.route("/incident/<int:incident_id>")
def incident_post(incident_id):
    post = Incident.query.get_or_404(incident_id)
    return render_template('incident_post.html', title= post.title, post=post)

@app.route("/incident/<int:incident_id>/update", methods=['GET','POST'])
@login_required
def incident_update(incident_id):
    post = Incident.query.get_or_404(incident_id)
    #if post.author != current_user:
    #    abort(403)
    form = IncidentForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.tags = form.tags.data
        post.history = post.history + '\n Updated by ' + current_user.username
        post.state = 'Active'
        post.current_assignee = current_user.username
        if form.category.data not in  categories:
            categories.append(form.category.data)
        db.session.commit()
        flash('Your Post has been updated', 'success')
        return redirect(url_for('incident_post', incident_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category
        form.tags.data = post.tags
    return render_template('incident.html', title='Update Incident',
                           form=form, legend='Update Incident')


@app.route("/incident/<int:incident_id>/delete", methods=['POST'])
@login_required
def incident_delete(incident_id):
    post = Incident.query.get_or_404(incident_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your Post has been deleted', 'success')
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics' , picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Incident.query.filter_by(author=user)\
    .order_by(Incident.date_posted.desc())\
    .paginate(page=page, per_page=5)
    return render_template('contact_posts.html', posts=posts, user=username)
