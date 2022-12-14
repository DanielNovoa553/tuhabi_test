import pymysql
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app, support_credentials=True)


'#-------------------------------------------Conexion Base de Datos---------------------------------------------------'


def connectdb():
    return pymysql.connect(host='3.130.126.210',
                                port=3309,
                                db='habi_db',
                                user='pruebas',
                                password='VGbt3Day5R',
                               )


'#-------------------------------------------------Funciones--------------------------------------------------------'


def validateJson(inputIn, field):
    print('Se valida el campo -> ' + field)
    if inputIn and field in inputIn:
        print(inputIn[field])
        print(type(inputIn[field]))
        if inputIn[field] == '':
            return False
        else:
            if type(inputIn[field]) == bool:
                print('El campo es un booleano')
                return str(inputIn[field])
            if type(inputIn[field]) == list:
                print('El campo es una lista')
                return inputIn[field]
            if type(inputIn[field]) == str:
                print('El campo es un string')
                return inputIn[field]
            if type(inputIn[field]) == int:
                print('El campo es un numero')
                return inputIn[field]
            else:
                return inputIn[field]
    else:
        return False


def getInput(inputIn):
    if inputIn == False:
        return False
    else:
        return str(inputIn)


'#--------------------------------------------Servicio Raiz-----------------------------------------------------------'


@app.route("/", methods=['POST', 'GET'])
def principal_metodo():
    return "Servicio Raiz tuhabi"


'#---------------------------------------------Obtener item por id-----------------------------------------------------'


@app.route("/getitem", methods=['GET'])
@cross_origin(supports_credentials=True)
def getitem():

    global id, estado
    print('getitem')
    output = {'response': False}
    inputIn = request.get_json(silent=True)
    con = connectdb()
    if con == False:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()
    print('Se valida JSON de entrada')
    if inputIn is not None:
        print('Hay un JSON de entrada')

        # property_id
        property_id = getInput(validateJson(inputIn, 'property_id'))
        if property_id == False:
            output['property_id'] = 'No se proporciono el campo o esta vacio'
            return jsonify(output), 400

    else:
        print('No se proporciono JSON')
        output['body'] = 'No se proporciono body'
        return jsonify(output), 400

    try:
        print('Se realiza consulta a la base ')
        query = f"SELECT * FROM status_history WHERE property_id = {property_id}   " \
                f"order by update_date DESC"
        print(query)
        cur.execute(query)
        item = cur.fetchone()
        print(item)

        if item is None:

            print(' Error no se encontro la informacion del item')
            output['message'] = 'Error no se encontro la informacion del item'
            return jsonify(output), 401

        else:
            print('Se encontro la informacion')
            id = item[0]
            property_id = item[1]
            status_id = item[2]
            if status_id == 1 or status_id == 2 :
                print('El estado del item no puede ser visializado')
                output['message'] = 'El estado del item no puede ser visializado'
                return jsonify(output), 202
            update_date = item[3].strftime('%d-%m-%Y %H:%M:%S')

            if status_id == 3:
                estado = 'pre_venta'

            if status_id == 4:
                estado = 'en_venta'

            if status_id == 5:
                estado = 'vendido'

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener los items')
        output['message'] = 'Ocurrio un error al obtener los items '
        return jsonify(output), 500

    output["id"] = id
    output["property_id"] = property_id
    output["status_id"] = status_id
    output["update_date"] = update_date
    output["estado"] = estado
    output['message'] = 'Se obtuvieron correctamente los items'
    output['response'] = True
    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


'#----------------------------------------Obtener items por flitros----------------------------------------------------'


@app.route("/getitems", methods=['GET'])
@cross_origin(supports_credentials=True)
def getitems():

    global city
    print('getitems')
    output = {'response': False}
    propertyarray = []
    inputIn = request.get_json(silent=True)
    con = connectdb()
    if con == False:
        output['message'] = 'No se puede conectar a la BD'
        return jsonify(output), 401

    cur = con.cursor()
    print('Se valida JSON de entrada')
    if inputIn is not None:
        print('Hay un JSON de entrada')
        # date
        if 'date' in inputIn and inputIn['date'] != '':
            flag_date = True
            date = inputIn['date']
        else:
            flag_date = False
            date = None

        # city
        if 'city' in inputIn and inputIn['city'] != '':
            flag_city = True
            city = inputIn['city']
        else:
            flag_city = False
            city = None

        # state
        if 'state' in inputIn and inputIn['state'] != '':
            flag_state = True
            state = inputIn['state']
        else:
            flag_state = False
            state = None

    else:
        print('No se proporciono JSON')
        output['body'] = 'No se proporciono body'
        return jsonify(output), 400

    try:

        if not flag_date and not flag_state and not flag_city:
            query = f"select * ,MAX(update_date) update_date  from " \
                    f"status_history inner join property on property.id = status_history.property_id where status_id " \
                    f"!= 1 and status_id != 2 group by property_id order by property_id desc"

            print(query)
            cur.execute(query)
            property = cur.fetchall()
            print(property)

            if property is None or property == []:
                print('No se encontraron items')

            for i in property:

                property_id = i[1]
                status_id = i[2]
                address = i[5]
                city = i[6]
                price = i[7]
                description = i[8]
                year = i[9]
                update_date = i[10].strftime('%d-%m-%Y %H:%M:%S')

                iObj = {

                    'property_id': property_id,
                    'address': address,
                    'city': city,
                    'price': price,
                    'description': description,
                    'year': year,
                    'status_id': status_id,
                    'update_date': update_date,
                }
                propertyarray.append(iObj)
            else:
                print('Se obtuvieron los items registrados')

            output['Property'] = propertyarray

        else:

            query = f"select * ,MAX(update_date) update_date  from " \
                    f"status_history inner join property on property.id = status_history.property_id where status_id " \
                    f"!= 1 and status_id != 2 "

            if date:
                query = query+f" and year ={date}"

            if city:
                query = query+f" and city ='{city}'"

            if state:
                query = query+f" and status_id ={state}"

            query = query+f" group by property_id order by property_id desc"
            print(query)
            cur.execute(query)
            property = cur.fetchall()
            print(property)

            if property is None or property == []:
                print('No se encontraron items')

            for i in property:

                property_id = i[1]
                status_id = i[2]
                address = i[5]
                city = i[6]
                price = i[7]
                description = i[8]
                year = i[9]
                update_date = i[10].strftime('%Y-%m-%d %H:%M:%S')

                iObj = {

                    'property_id': property_id,
                    'address': address,
                    'city': city,
                    'price': price,
                    'description': description,
                    'year': year,
                    'status_id': status_id,
                    'update_date': update_date,
                }
                propertyarray.append(iObj)
            else:
                print('Se obtuvieron los items registrados')

            output['Property'] = propertyarray

    except Exception as e:
        print(e)
        print('Ocurrio un error al obtener los items')
        output['message'] = 'Ocurrio un error al obtener los items '
        return jsonify(output), 500

    output['message'] = 'Se obtuvieron correctamente los items'
    output['response'] = True
    con.commit()
    cur.close()
    con.close()
    print('Ejecucion correcta')
    return jsonify(output), 200


if __name__ == '__main__':
    app.run()