
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields
import mysql.connector
from mysql.connector import Error



app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    age = fields.Int(required=True)
    start_date = fields.Date(required=True)


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)



def get_db_connection():
    db_name = 'gym_db'
    user = 'root'
    password = 'Bedswamp25!'
    host = 'localhost'

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        print('Connection successful!')
        return conn
    except Error as e:
        print(f'Error{e}')


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    new_member = (member_data['first_name'],member_data['last_name'],member_data['age'], member_data['start_date'])
    query = 'INSERT INTO Members(first_name, last_name, age, start_date) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, new_member)
    conn.commit()
    return jsonify({'message': 'New member added successfully'}), 200



@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'Error': 'Database connection failed!'}), 500
    try:

        cursor = conn.cursor()
        query = 'SELECT * FROM Members WHERE id = %s'  
        cursor.execute(query, (id, ))
        member = cursor.fetchone()
        if member:
            return member_schema.jsonify(members)
        else:
            return jsonify({'message': 'Member not Found!'}), 404
    except Error as e:
        return jsonify({'Error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    new_member = (member_data['first_name'],member_data['last_name'],member_data['age'], member_data['start_date'],id)
    query = 'UPDATE Members SET first_name=%s,last_name=%s,age=%s,start_date=%s WHERE id = %s'
    cursor.execute(query, new_member)
    conn.commit()
    return jsonify({'message': 'New member added successfully'}), 200



@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'DELETE FROM Members WHERE id = %s'
        cursor.execute(query, (id,))
        conn.commit()
        return jsonify({'message': 'Member deleted successfully'}), 200

    except ValidationError as e:
        return jsonify(e.messages), 400
    


if __name__ == '__main__':
    app.run(debug=True)