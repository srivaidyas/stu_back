from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Allow all origins
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
    vowels_present = db.Column(db.String(3), nullable=False)  # New column for vowels presence

    def serialize(self):
        return {
            "id": self.id,
            "raw_data": self.raw_data,
            "encrypted_data": self.encrypted_data,
            "shift_value": self.shift_value,
            "unique_name": self.unique_name,
            "encrypted_id": self.encrypted_id,
            "vowels_present": self.vowels_present
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

def create_matrix_from_string(text, width):
    """Create a 2D matrix from a string with the given width."""
    return [list(text[i:i + width]) for i in range(0, len(text), width)]

def matrix_to_string(matrix):
    """Convert a 2D matrix back to a string."""
    return ''.join(''.join(row) for row in matrix)

def swap_matrix_elements(matrix):
    """Perform a 2D swap of elements in the matrix."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    for i in range(rows):
        for j in range(cols // 2):
            # Swap elements in each row
            matrix[i][j], matrix[i][cols - j - 1] = matrix[i][cols - j - 1], matrix[i][j]
    return matrix

def reverse_string_by_swapping_2d(text, width=5):
    """Reverse the string by converting it to a 2D matrix and swapping elements."""
    matrix = create_matrix_from_string(text, width)
    swapped_matrix = swap_matrix_elements(matrix)
    return matrix_to_string(swapped_matrix)

def sort_string_alphabetically(text):
    return ''.join(sorted(text))

def replace_vowels_with_special_characters(text):
    vowels_to_special_chars = {'a': '@', 'e': '#', 'i': '$', 'o': '%', 'u': '&',
                               'A': '@', 'E': '#', 'I': '$', 'O': '%', 'U': '&'}
    return ''.join(vowels_to_special_chars.get(char, char) for char in text)

def generate_unique_name():
    return random.choice(military_alphabet)

def generate_encrypted_id(unique_name, record_id, shift_value):
    return f"{unique_name}{record_id}-{shift_value}"

def check_vowels_presence(text):
    vowels = "aeiouAEIOU"
    return any(char in vowels for char in text)

class RecordListResource(Resource):
    def get(self):
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
            encrypted_data = reverse_string_by_swapping_2d(encrypted_data)
            encrypted_data = sort_string_alphabetically(encrypted_data)
            final_encrypted_data = replace_vowels_with_special_characters(encrypted_data)
            unique_name = generate_unique_name()
            vowels_present = "Yes" if check_vowels_presence(encrypted_data) else "No"

            new_record = Record(
                raw_data=raw_data, 
                encrypted_data=final_encrypted_data, 
                shift_value=shift_value,
                unique_name=unique_name,
                encrypted_id="",  # Placeholder, will be updated after the record is added
                vowels_present=vowels_present
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
        encrypted_data = reverse_string_by_swapping_2d(encrypted_data)
        encrypted_data = sort_string_alphabetically(encrypted_data)
        final_encrypted_data = replace_vowels_with_special_characters(encrypted_data)
        vowels_present = "Yes" if check_vowels_presence(encrypted_data) else "No"

        record.encrypted_data = final_encrypted_data
        record.shift_value = shift_value
        record.unique_name = generate_unique_name()
        record.encrypted_id = generate_encrypted_id(record.unique_name, record_id, shift_value)
        record.vowels_present = vowels_present

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
