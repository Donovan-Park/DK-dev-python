import sqlite3

import click

from flask import current_app, g
"""
current_app 은 Request를 처리하는 "플라스크 App"을 가리키는 객체
g 는 각 Request마다 가지는 특별한 객체 : 데이터를 저장
"""
from flask.cli import with_appcontext

def get_db():
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types = sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	db = g.pop("db", None)		# g dict.에 "db" 키를 가진 element가 없다면 None을 리턴

	if db is not None:
		db.close()

def init_db():
	db = get_db()

	with current_app.open_resource("schema.sql") as f:
		db.executescript(f.read().decode("utf8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
	init_db()
	click.echo("Initialized the database.")


def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command);


