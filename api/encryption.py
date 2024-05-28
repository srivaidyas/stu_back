from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app, resources={r"/encrypted_data": {"origins": "*"}})  # Allow all origins for /encrypted_data endpoint
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
db = SQLAlchemy(app)
api = Api(app)

military_alphabet = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", 
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", 
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", 
    "X-ray", "Yankee", "Zulu"
]

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_data = db.Column(db.String(512), nullable=False)
    encrypted_data = db.Column(db.String(512), nullable=False)
    shift_value = db.Column(db.Integer, nullable=False)
    unique_name = db.Column(db.String(64), nullable=False)
    encrypted_id = db.Column(db.String(128), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "raw_data": self.raw_data,
            "encrypted_data": self.encrypted_data,
            "shift_value": self.shift_value,
            "unique_name": self.unique_name,
            "encrypted_id": self.encrypted_id
        }

def caesar_cipher_encrypt(text, shift):
    encrypted_text = []
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            encrypted_text.append(chr((ord(char) - shift_base + shift) % 26 + shift_base))
        else:
            encrypted_text.append(char)
    return ''.join(encrypted_text)

def reverse_string_by_swapping(text):
    text_list = list(text)
    n = len(text_list)
    for i in range(n // 2):
        text_list[i], text_list[n - i - 1] = text_list[n - i - 1], text_list[i]
    return ''.join(text_list)

def generate_unique_name():
    return random.choice(military_alphabet)

def generate_encrypted_id(unique_name, record_id, shift_value):
    return f"{unique_name}{record_id}-{shift_value}"

class RecordListResource(Resource):
    def get(self):
        # Fetch the record with the greatest ID
        greatest_id_record = Record.query.order_by(Record.id.desc()).first()
        if greatest_id_record:
            return jsonify(greatest_id_record.serialize())
        else:
            return jsonify({"message": "No records found"}), 404
    
    def post(self):
        try:
            data = request.get_json()
            raw_data = data['raw_data']
            shift_value = random.randint(1, 25)
            encrypted_data = caesar_cipher_encrypt(raw_data, shift_value)
            final_encrypted_data = reverse_string_by_swapping(encrypted_data)
            unique_name = generate_unique_name()

            new_record = Record(
                raw_data=raw_data, 
                encrypted_data=final_encrypted_data, 
                shift_value=shift_value,
                unique_name=unique_name,
                encrypted_id=""  # Placeholder, will be updated after the record is added
            )
            db.session.add(new_record)
            db.session.flush()  # Get the new record's ID
            new_record.encrypted_id = generate_encrypted_id(unique_name, new_record.id, shift_value)
            db.session.commit()

            return jsonify(new_record.serialize()), 201
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return jsonify({"error": error_message}), 500

class RecordResource(Resource):
    def get(self, record_id):
        record = Record.query.get_or_404(record_id)
        return jsonify(record.serialize())
    
    def delete(self, record_id):
        record = Record.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204

    def put(self, record_id):
        data = request.get_json()
        record = Record.query.get_or_404(record_id)
        
        record.raw_data = data.get('raw_data', record.raw_data)
        shift_value = random.randint(1, 25)
        encrypted_data = caesar_cipher_encrypt(record.raw_data, shift_value)
        final_encrypted_data = reverse_string_by_swapping(encrypted_data)
        
        record.encrypted_data = final_encrypted_data
        record.shift_value = shift_value
        record.unique_name = generate_unique_name()
        record.encrypted_id = generate_encrypted_id(record.unique_name, record_id, shift_value)
        
        db.session.commit()
        return jsonify(record.serialize())

class RecordByEncryptedIdResource(Resource):
    def get(self, encrypted_id):
        record = Record.query.filter_by(encrypted_id=encrypted_id).first()
        if record:
            return jsonify(record.serialize())
        else:
            return jsonify({"message": "Record not found"}), 404

api.add_resource(RecordListResource, '/encrypted_data')
api.add_resource(RecordResource, '/encrypted_data/<int:record_id>')
api.add_resource(RecordByEncryptedIdResource, '/encrypted_id/encrypted/<string:encrypted_id>')  # New endpoint for encrypted ID

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8085, debug=True)

