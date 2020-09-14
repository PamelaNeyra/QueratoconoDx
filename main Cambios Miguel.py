from flask import Flask
from flask import flash
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask_mysqldb import MySQL
from diagnostico.reglas import decidirRegla, decidirReglaFormeFruste, decidirReglaQueratocono, decidirReglaSubclinico, decidirReglaSano
#import bcrypt
#from diagnostico.arbol_diagnostico import diagnostico_queratocono
import json
import requests
import pandas as pd
import numpy as np

app = Flask(__name__)	

app.secret_key = "diagnosticoQueratocono"

app.config['MYSQL_HOST'] = 'btufaxde2xhfcwikca24-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'uzydheo8zso6krag'
app.config['MYSQL_PASSWORD'] = '2GNFCVgFYApDi1J5I4TM'
app.config['MYSQL_DB'] = 'btufaxde2xhfcwikca24'

mysql = MySQL(app)

#encriptado = bcrypt.gensalt()

@app.route('/')
def main():
	session.clear()
	if 'dni' in session:
		return render_template('principal_medico.html')
	else:
		return render_template('ingresar.html')

@app.route('/ingresar', methods=['GET','POST']) 		
def ingresar():
	cursor = mysql.connection.cursor()
	query1 = "SELECT id_clinica, nombre, direccion FROM clinica"
	cursor.execute(query1)
	lista_clinica = cursor.fetchall()
	cursor.close()

	if request.method == 'GET':
		if 'dni' in session:
			return render_template('principal_medico.html')
		else:
			return render_template('ingresar.html',lista_clinica=lista_clinica)
	else:
		correo = request.form['email']
		password = request.form['password']
		#password_encode = password.encode("utf-8")

		cur = mysql.connection.cursor()
		query = "SELECT dni_usuario, correo, password, tipo_usuario FROM usuario WHERE correo=%s"
		cur.execute(query,[correo])
		usuario = cur.fetchone()
		cur.close()

		#if(usuario!=None):
		#	password_encriptado_encode = usuario[2].encode()
		#	if (bcrypt.checkpw(password_encode,password_encriptado_encode)):
		#		session['dni'] = usuario[0]
		#		session['tipo_usuario'] = usuario[3]
		#		return redirect(url_for('principal'))
		#else:
		#	render_template('ingresar.html',lista_clinica=lista_clinica)
		if(usuario!=None):
			password_correcto = usuario[2]
			if password == password_correcto:
				session['dni'] = usuario[0]
				session['tipo_usuario'] = usuario[3]
				return redirect(url_for('principal'))
		else:
			render_template('ingresar.html',lista_clinica=lista_clinica)

	return render_template('ingresar.html',lista_clinica=lista_clinica)

@app.route('/registrar', methods=['GET','POST'])
def registrar():
	cursor = mysql.connection.cursor()
	query1 = "SELECT id_clinica, nombre, direccion FROM clinica"
	cursor.execute(query1)
	lista_clinica = cursor.fetchall()
	cursor.close()

	if request.method == 'POST':
		nombre = request.form['nombre']
		apellido_paterno = request.form['apellido_paterno']
		apellido_materno = request.form['apellido_materno']
		dni = request.form['dni']
		tipo_usuario = request.form.get('lista_usuario')
		tipo_medico = request.form['tipo_medico']
		clinica = request.form.get('lista_clinica')
		correo = request.form['email']
		password = request.form['password']
		#password_encode = password.encode("utf-8")
		#password_encriptado = bcrypt.hashpw(password_encode,encriptado)

		cur = mysql.connection.cursor()
		query2 = "INSERT into usuario (dni_usuario,correo,password,tipo_usuario,estado) VALUES (%s,%s,%s,%s,%s)"
		#cur.execute(query2,(dni,correo,password_encriptado,tipo_usuario.'1'))
		cur.execute(query2,(dni,correo,password,tipo_usuario,'1'))
		mysql.connection.commit()

		if tipo_usuario == "0":
			query = "INSERT into medico (dni_medico,id_clinica,nombre,apellido_paterno,apellido_materno,tipo_medico,tipo_usuario,consultorio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
			cur.execute(query,(dni,clinica,nombre,apellido_paterno,apellido_materno,tipo_medico,tipo_usuario,"C01"))
			mysql.connection.commit()
		else:
			query = "INSERT into tecnico (dni_tecnico,nombres,apellido_paterno,apellido_materno,tipo_usuario) VALUES (%s,%s,%s,%s,%s)"
			cur.execute(query,(dni,nombre,apellido_paterno,apellido_materno,tipo_usuario))
			mysql.connection.commit()	

		session['dni'] = dni
		session['tipo_usuario'] =tipo_usuario

		return redirect(url_for('principal'))

	return render_template('ingresar.html',lista_clinica=lista_clinica)

@app.route('/principal')
def principal():
	if session['tipo_usuario'] == '0':

		medico = session['dni']
		cur = mysql.connection.cursor()
		cur.callproc("obtenerPacientes",[medico])
		lista_pacientes = cur.fetchall()
		cur.close()

		cur = mysql.connection.cursor()
		cur.callproc("obtenerDatosDoctor",[medico])
		datos_medico = cur.fetchone()
		cur.close()

		"""cur = mysql.connection.cursor()
		cur.callproc("obtener_historial")
		datos_historial = cur.fetchall()
		cur.close()"""
		datos_historial = []

		return render_template('principal_medico.html',lista_pacientes=lista_pacientes,datos_medico=datos_medico,datos_historial=datos_historial)
	else:
		tecnico = session['dni']
		cur = mysql.connection.cursor()
		cur.callproc("obtener_tecnico",[tecnico])
		datos_tecnico = cur.fetchone()
		cur.close()

		return render_template('principal_tecnico.html',datos_tecnico=datos_tecnico)
	
	return render_template('principal_medico.html')

@app.route('/salir')
def salir():
	session.clear()
	return redirect(url_for('ingresar'))

@app.route('/agregaratencion', methods=['GET','POST'])
def agregaratencion():
	if request.method == 'POST':
		dni = request.form['dni']
		filename = request.form['fileName']
		cur = mysql.connection.cursor()
		cur.callproc("guardar_archivo",[filename])
		#cur.callproc("agregar_atencion",(dni,"Queratocono","Leve",filename))
		mysql.connection.commit()
		#respuesta = diagnostico_queratocono(filename)
		#print(respuesta)
		return redirect(url_for('principal'))
		
	return redirect(url_for('principal'))

@app.route('/agregarPaciente', methods=['GET','POST'])
def agregarPaciente():
	if request.method == 'POST':
		medico = session['dni']
		nombre = request.form['nombre']
		apellido_paterno = request.form['apellido_paterno']
		apellido_materno = request.form['apellido_materno']
		dni = request.form['dni']
		fecha_nac = request.form['fecha_nac']
		sexo = 'F'

		cur = mysql.connection.cursor()
		cur.callproc("agregar_paciente",(medico,dni,nombre,apellido_paterno,apellido_materno,fecha_nac,sexo))
		mysql.connection.commit()

		return redirect(url_for('principal'))

	return redirect(url_for('principal'))

@app.route('/diagnostico/')
@app.route('/diagnostico/<dni>')
def diagnostico(dni="Valor por defecto"):
	medico = session['dni']
	cur = mysql.connection.cursor()
	cur.callproc("obtenerDatosDoctor",[medico])
	datos_medico = cur.fetchone()
	cur.close()
	clasificacion = ''
	listas = []
	listas.append([])
	listas.append([])
	return render_template('diagnostico.html',dni=dni,datos_medico=datos_medico,clasificacion=clasificacion, info = listas, cantidad = 0)

@app.route('/diagnosticar',methods=['GET','POST'])
def diagnosticar():
	if request.method == 'POST':
		medico = session['dni']
		cur = mysql.connection.cursor()
		cur.callproc("obtenerDatosDoctor",[medico])
		datos_medico = cur.fetchone()
		cur.close()

		archivo = request.form['fileName']

		info = requests.get('https://rfprediccion.herokuapp.com/prediccion/'+archivo)
		
		json = info.json()
		df = pd.read_csv(archivo)
		registros = np.array(df[["Rh F (mm)","Rv F (mm)","Astig F (D)","Asph. Q F","Rh B (mm)","Rv B (mm)","K2 B (D)","Astig B (D)","Asph. Q B","Pachy Apex","Pachy Min","ISV","IVA","IHA","IHD","K1 (D)","K2 (D)","Astig","RPI Max","K max","I-S","AC Depth","Ecc Sup","Ecc Inf","Cor.Vol.","KPD","Ecc (Front)","Ecc (Back)","Sag. Height Mean [µm]","ACD Apex"]])
		#print(json)
		clasificacion = json['resultado'][0]['clasificacion'].upper()
		print(clasificacion)
		if clasificacion == "FORME FRUSTE":
			listas = decidirReglaFormeFruste(registros[0])
		elif clasificacion == "SUBCLINICO":
			listas = decidirReglaSubclinico(registros[0])
		elif clasificacion == "QUERATOCONO":
			listas = decidirReglaQueratocono(registros[0])
		elif clasificacion == "OJO SANO":
			listas = decidirReglaSano(registros[0])
		
		return render_template('diagnostico.html',clasificacion=clasificacion,datos_medico=datos_medico,info = listas, cantidad = len(listas[0]))

		"""i=0
		sag = 1475
		rhB = 6.8
		rhF = 8.07
		k1= 41.8
		pachy = 558
		kmax = 47.85
		if clasificacion == 'Forme Fruste':
			#Obtendré los valores del .csv y eso lo compararé
			#sag = valor
			#rhB = valor
			#rhF = valor
			#k1  = valor
			#pachy = valor
			#kamx = valor	
			if sag<=1468 and rhF>8.03 and k1<=41.9 and pachy>546:
				i = 'reglas0'
			elif rhF>8.03 and k1<=41.9 and kmax<=44.98 and rhB>6.59:
				i = 'reglas1'
			elif rhF>8.03 and k1<=41.9 and pachy>546 and rhB>6.59:
				i = 'reglas2'

			condicion = json[i][0]

		return condicion"""
	return "GG"

if __name__ == '__main__':
	app.run(debug = True) 

