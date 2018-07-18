import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

"""
 Blueprint 객체를 "auth"란 이름으로 생성, __name__에 정의되어 있음, 블루프린트와 연관된 모든 URL을 "/auth"로 시작하게 한다.
"""
bp = Blueprint("auth", __name__, url_prefix="/auth")

"""
	bp는 "/auth" 로 시작하는 URL
	route 함수를 통해 "/register" 와 연결시키고, 해당 URL에 "GET", "POST" 함수와 맵핑
	"/auth/register" URL에 Request가 오면 "register" 뷰를 보여주고, 요청에대한 응답 값을 리턴
"""
@bp.route("/register", methods = ("GET", "POST"))
def register():
	if request.method == "POST":	##유저가 Form을 제출하면, request.method가 "POST"가 됨
		username = request.form["username"]
		password = request.form["password"]
		db = get_db()
		error = None

		if not username:
			error = "Username is required."
		elif not password:
			error = "Password is required."
		elif db.execute(
			"SELECT id FROM user WHERE username = ?", (username, )
			).fetchone() is not None:
			##fetchone()은 1 Row를, fetchall()은 모든 결과들을 포함하는 1개의 List를 리턴
			error = "User {} is already registered.".format(username)

		if error is None:
			db.execute(
				"INSERT INTO user (username, Password) VALUES (?, ?)", (username, generate_password_hash(password))
			)
			db.commit()
			return redirect(url_for("auth.login"))		##Login 페이지로 리다이렉트 이동!

		flash(error)

	##유저가 초기에 "/auth/register"에 접속했을 때 렌더링할 템플릿
	return render_template("auth/register.html")



@bp.route("/login", methods = ("GET", "POST"))
def login():
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		db = get_db()
		error = None

		user = db.execute(
			"SELECT * FROM user WHERE username = ?", (username,)
		).fetchone()

		if user is None:
			error = "Incorrect username."
		elif not check_password_hash(user["password"], password):
			error = "Incorrect password."

		if error is None :
			session.clear()
			session["user_id"] = user["id"]
			return redirect(url_for("index"))

		flash(error)

	return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get("user_id")

	if user_id is None:
		g.user = None
	else:
		g.user = get_db().execute(
			"SELECT * FROM user WHERE id = ?", (user_id)
		).fetchone()

@bp.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("index"))

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("auth.login"))
		return view(**kwargs)

	return wrapped_view


