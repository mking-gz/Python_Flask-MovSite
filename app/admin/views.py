#codding:utf8
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm
from app.models import Admin, Tag, Movie
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os
import uuid
import datetime

#登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login",next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")+str(uuid.uuid4().hex)+fileinfo[-1]
    return filename

@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")

#登录   
@admin.route("/login/",methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html",form=form)

@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("admin", None)
    return redirect(url_for("admin.login"))

@admin.route("/pwd/")
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")

#添加标签
@admin.route("/tag/add/",methods=["GET", "POST"])
@admin_login_req
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash("名称已经存在! ", "err")
            return redirect(url_for('admin.tag_add'))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功! ", "ok")
        redirect(url_for('admin.tag_add'))
    return render_template("admin/tag_add.html", form=form)

#标签列表
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)

#添加电影
@admin.route("/movie/add/",methods=["GET","POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(int(app.config["UP_DIR"]),"rw")
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"]+url)
        form.logo.data.save(app.config["UP_DIR"]+logo)
        movie = Movie(
            title = data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功! ","ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)

#电影列表
@admin.route("/movie/list/<int:page>/", methods=["GET"])
@admin_login_req
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html",page_data=page_data)

@admin.route("/preview/add/")
@admin_login_req
def preview_add():
    return render_template("admin/preview_add.html")

@admin.route("/preview/list/")
@admin_login_req
def preview_list():
    return render_template("admin/preview_list.html")

@admin.route("/oplog/list/")
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")

@admin.route("/adminloginlog/list/")
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")

@admin.route("/userloginlog/list/")
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")

@admin.route("/admin/add/")
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")

@admin.route("/admin/list/")
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")