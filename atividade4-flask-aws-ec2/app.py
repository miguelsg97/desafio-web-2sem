import os

import pymysql
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)


def get_connection():
    """Abre uma conexão nova com o MySQL usando as variáveis do .env."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sobrenos")
def sobrenos():
    return render_template("sobrenos.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        assunto = request.form["assunto"]
        mensagem = request.form["mensagem"].strip()

        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # consulta parametrizada: nunca concatenar valores na string SQL
                cur.execute(
                    "INSERT INTO contatos (nome, email, assunto, mensagem) "
                    "VALUES (%s, %s, %s, %s)",
                    (nome, email, assunto, mensagem),
                )
            conn.commit()
        except pymysql.MySQLError:
            app.logger.exception("Erro ao gravar contato no banco")
            return render_template("contato.html", erro=True), 500
        finally:
            if conn is not None:
                conn.close()

        return redirect(url_for("contato", enviado=1))

    return render_template("contato.html", enviado=request.args.get("enviado"))


@app.route("/listar")
def listar():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(
                "SELECT id, nome, email, assunto, mensagem "
                "FROM contatos ORDER BY id DESC"
            )
            contatos = cur.fetchall()
    except pymysql.MySQLError:
        app.logger.exception("Erro ao consultar contatos no banco")
        return render_template("listar.html", erro=True, contatos=[]), 500
    finally:
        if conn is not None:
            conn.close()

    return render_template("listar.html", contatos=contatos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
