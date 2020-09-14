from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = "diagnosticoQueratocono"

app.config['MYSQL_HOST'] = 'bv8xv3gi0rnln7uikpvy-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'us5ow3hmh4ksah0n'
app.config['MYSQL_PASSWORD'] = '31EQWftwDQCVQNy7Vduk'
app.config['MYSQL_DB'] = 'bv8xv3gi0rnln7uikpvy'

mysql = MYSQL(app)

