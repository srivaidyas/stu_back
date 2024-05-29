from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Allow all origins across all site, errors persists with cors so we ended up allwoing permission for al origins in order to combat said probelms and error, which seemed to have worked
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db' #creates a databse named records.db which stores the data in the backend for the api to access.
db = SQLAlchemy(app) #SQAlcehmy used in the code
api = Api(app) # API intergreation in the code

military_alphabet = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", #a list of the military alphabet from A-Z which is later used for the encrypted id name. The words are used in order to create a more prfessional look to the program
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",  # this is an example of a list being used in the program from which later parts are accessseed.
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", 
    "X-ray", "Yankee", "Zulu"
]

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True) # create a coloumn in the backend database for the id of the raw and encrypted data
    raw_data = db.Column(db.String(512), nullable=False) # creates a backend coloumn to store the raw data sent by the user
    encrypted_data = db.Column(db.String(512), nullable=False) # creates a couloumn which stores the encrypted data in the backend
    shift_value = db.Column(db.Integer, nullable=False)  # creates a couloumn that stores the value for the ceaser cipher shift value, usually an interger value
    unique_name = db.Column(db.String(64), nullable=False) # stores the military alphabet randomly adssigned to the id and the raw data
    encrypted_id = db.Column(db.String(128), nullable=False) # stores the encrypted id which is a mix of the id, shift value and the unquie name to form what will later be known as the secret key for decryption
    vowels_present = db.Column(db.String(3), nullable=False)  # New column for vowels presence, Y/N for the vowels present in the in string with is used to sort and subsitute values.

    def serialize(self):
        return {
            "id": self.id, # id ofr hte data sent by the user
            "raw_data": self.raw_data, # raw data string sent from the frontend by the user
            "encrypted_data": self.encrypted_data, # encrypted data string containeing the encrypted data
            "shift_value": self.shift_value, # shift value containing the shift integer for the ceaser cipher
            "unique_name": self.unique_name, # unqiue name from the miltary alphabet assigned to each id value
            "encrypted_id": self.encrypted_id, # encrypted id which is a mix of all the other values
            "vowels_present": self.vowels_present # check for vowels which returns yes if positive and no if negetive
        }

#Algorithm basics: 4 layer encryption
    # first layer deals with the ceaser cipher which randomly selects a number from 1-25 to shift the letters of the string
    # second layer deals with shifting the first and last, the second and second last and so on and so forth using a 2-D Iteration
    # third layer sorts the existing encrypted string alphbetically from A-Z
    # fourth layer searches the encrypted string for vowels and interchanges them with special characters

# Summary for Requirments
    # lists: In the provided backend, we use list comprehension to serialize multiple Record objects efficiently. The line [record.serialize() for record in records] quickly converts all records into a list of dictionaries. 
    # Sorting and Searching: Sorting occurs with the alphbetical sort whereas searching occurs with the vowel search and substirute for special characters
    # 2-D Iteration occurs with the matrix of first and last substitution
    # Big O Time Complexity: Big(O) complexity helps evaluate the performance of algorithms, particularly in sorting and searching operations. Sorting operation of SQAlchemy which include those of oder_by and filter help reduce the time it takes to compare and sort large databases
    # Depolyment: Handled by the Ryan


def caesar_cipher_encrypt(text, shift): # This function encrypts text using a Caesar cipher with a given shift value. It iterates over each character, adjusting its ASCII value based on the shift. 
    encrypted_text = [] #Non-alphabetic characters are appended unchanged. This simple encryption demonstrates basic iteration and character manipulation.
    for char in text: #Iterates over each character in the input text.
        if char.isalpha(): # Checks if the character is an alphabet letter.
            shift_base = 65 if char.isupper() else 97 #
            encrypted_text.append(chr((ord(char) - shift_base + shift) % 26 + shift_base)) #Encrypts the character by shifting its ASCII value.
        else:
            encrypted_text.append(char)
    return ''.join(encrypted_text) # Joins the list of encrypted characters into a single string and returns it.

 #GPT code for 2-d iteration

#2-D Iteration Description: 
# The function performs the 2 d iteration over a matrix, swapping elememts wihing each row. The outerlook iterated over the rows, and teh ineer loop iterates over the coloumns
# Function create a 2-D matirix and swaps elemts in each row using teh swap matrix elements
# the 2 d iteration is used to swap the letters in teh frist and last and the second and second last and so on in a more comprehensive way

#in lay man's terms
# the string of words Hello World! is converted into a matrix for 2-D iteration
    # [H, E, L, L, O], 
    # [W, O, R, L, D]
# then on each the first and last and second and last and so on are swapped
    # [O, L, L, E, H]
    # [D, L, R, O, W]
# lastly then two different strings are then concentated together to form a single string
    # [OLLEH-DLROW]

def create_matrix_from_string(text, width): #This function uses list comprehension to create a 2D matrix from a string, splitting it into chunks of the specified width
    """Create a 2D matrix from a string with the given width.""" # Creates a list of lists where in each row represents a matrix of the inputted text from teh user
    return [list(text[i:i + width]) for i in range(0, len(text), width)]  # Specifies the length and the width

def matrix_to_string(matrix): # This function concatenates rows and then joins the resulting strings to form a single string. It uses nested list comprehensions to process the 2D matrix efficiently.
    """Convert a 2D matrix back to a string.""" # Converts the matrix back into a string
    return ''.join(''.join(row) for row in matrix) # joins the rows of teh matrix into one single string of letters

def swap_matrix_elements(matrix): # This function demonstrates 2D iteration by swapping elements within each row of a matrix. 
    #It iterates over the rows and columns, performing swaps to reverse the order of elements within each row.
    """Perform a 2D swap of elements in the matrix."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0 # This function iterates over each row of the matrix and within each row, it iterates up to half the width of the matrix.
    for i in range(rows): # For each iteration, it swaps the elements symmetrically across the row. For instance, in the matrix
        for j in range(cols // 2):
            # Swap elements in each row
            matrix[i][j], matrix[i][cols - j - 1] = matrix[i][cols - j - 1], matrix[i][j]
    return matrix

def reverse_string_by_swapping_2d(text, width=5): # This function combines creating a matrix, swapping elements, and converting the matrix back to a string. It showcases the practical application of 2D iteration in string manipulation.
    """Reverse the string by converting it to a 2D matrix and swapping elements."""
    matrix = create_matrix_from_string(text, width) # Concantation of the string of letters into one single string of a word.
    swapped_matrix = swap_matrix_elements(matrix) # The final result is the reversed string obtained after swapping elements in the matrix and converting it back to a string.
    return matrix_to_string(swapped_matrix) # returns the result to the matrix

def sort_string_alphabetically(text): #This function sorts the characters of a string in alphabetical order using Python's built-in sorted function. It demonstrates simple sorting, leveraging efficient built-in algorithms.
    return ''.join(sorted(text))

def replace_vowels_with_special_characters(text): # This function replaces vowels in a string with corresponding special characters. It uses a dictionary for mappings and a list comprehension for efficient processing.
    vowels_to_special_chars = {'a': '@', 'e': '#', 'i': '$', 'o': '%', 'u': '&', # The searching portion of the algorithm 
                               'A': '@', 'E': '#', 'I': '$', 'O': '%', 'U': '&'}
    return ''.join(vowels_to_special_chars.get(char, char) for char in text)

def generate_unique_name(): # This function randomly selects a name from the military_alphabet list, ensuring uniqueness in record naming.
    return random.choice(military_alphabet)

def generate_encrypted_id(unique_name, record_id, shift_value): # This function generates a unique encrypted ID by combining a unique name, record ID, and shift value. It demonstrates string formatting for creating unique identifiers.
    return f"{unique_name}{record_id}-{shift_value}"

def check_vowels_presence(text): # This function checks if a string contains any vowels, using a generator expression for efficient iteration. It returns True if any vowel is found, otherwise False.
    vowels = "aeiouAEIOU" # this acts are teh searching segment of the algorithm which searches the encrypted string for the presence of any vowels, and if there are any vowels present then the vowel is interchanged into a special character
    return any(char in vowels for char in text)

class RecordListResource(Resource):
    # Method to handle GET requests for the RecordListResource endpoint
    def get(self):
        # Retrieve the record with the greatest ID from the database
        greatest_id_record = Record.query.order_by(Record.id.desc()).first()
        if greatest_id_record:  # Check if a record was found
            return jsonify(greatest_id_record.serialize())  # Return the serialized record
        else:
            return jsonify({"message": "No records found"}), 404  # Return a message indicating no records were found

    # Method to handle POST requests for the RecordListResource endpoint
    def post(self):
        try:
            data = request.get_json()  # Get the JSON data from the request
            raw_data = data['raw_data']  # Extract the raw data from the JSON
            shift_value = random.randint(1, 25)  # Generate a random shift value
            encrypted_data = caesar_cipher_encrypt(raw_data, shift_value)  # Encrypt the raw data
            encrypted_data = reverse_string_by_swapping_2d(encrypted_data)  # Reverse the encrypted data
            encrypted_data = sort_string_alphabetically(encrypted_data)  # Sort the encrypted data alphabetically
            final_encrypted_data = replace_vowels_with_special_characters(encrypted_data)  # Replace vowels with special characters
            unique_name = generate_unique_name()  # Generate a unique name
            vowels_present = "Yes" if check_vowels_presence(encrypted_data) else "No"  # Check if vowels are present

            # Create a new Record object with the processed data
            new_record = Record(
                raw_data=raw_data,
                encrypted_data=final_encrypted_data,
                shift_value=shift_value,
                unique_name=unique_name,
                encrypted_id="",  # Placeholder for encrypted ID
                vowels_present=vowels_present
            )

            db.session.add(new_record)  # Add the new record to the database session
            db.session.flush()  # Get the new record's ID
            new_record.encrypted_id = generate_encrypted_id(unique_name, new_record.id, shift_value)  # Generate encrypted ID
            db.session.commit()  # Commit changes to the database

            return jsonify(new_record.serialize()), 201  # Return the serialized new record with status code 201 (Created)
        except Exception as e:  # Handle any exceptions that may occur
            error_message = f"An error occurred: {str(e)}"  # Generate an error message
            return jsonify({"error": error_message}), 500  # Return the error message with status code 500 (Internal Server Error)


class RecordResource(Resource):
    # Method to handle GET requests for individual records by ID
    def get(self, record_id):
        record = Record.query.get_or_404(record_id)  # Retrieve the record with the given ID or return a 404 error if not found
        return jsonify(record.serialize())  # Return the serialized record

    # Method to handle DELETE requests for individual records by ID
    def delete(self, record_id):
        record = Record.query.get_or_404(record_id)  # Retrieve the record with the given ID or return a 404 error if not found
        db.session.delete(record)  # Delete the record from the database
        db.session.commit()  # Commit changes to the database
        return '', 204  # Return an empty response with status code 204 (No Content)

    # Method to handle PUT requests for updating individual records by ID
    def put(self, record_id):
        data = request.get_json()  # Get the JSON data from the request
        record = Record.query.get_or_404(record_id)  # Retrieve the record with the given ID or return a 404 error if not found

        # Update record attributes with data from the request, if provided
        record.raw_data = data.get('raw_data', record.raw_data)  # Update raw data if provided
        shift_value = random.randint(1, 25)  # Generate a random shift value
        encrypted_data = caesar_cipher_encrypt(record.raw_data, shift_value)  # Encrypt the updated raw data
        encrypted_data = reverse_string_by_swapping_2d(encrypted_data)  # Reverse the encrypted data
        encrypted_data = sort_string_alphabetically(encrypted_data)  # Sort the encrypted data alphabetically
        final_encrypted_data = replace_vowels_with_special_characters(encrypted_data)  # Replace vowels with special characters
        vowels_present = "Yes" if check_vowels_presence(encrypted_data) else "No"  # Check if vowels are present

        # Update record attributes with processed data
        record.encrypted_data = final_encrypted_data
        record.shift_value = shift_value
        record.unique_name = generate_unique_name()
        record.encrypted_id = generate_encrypted_id(record.unique_name, record_id, shift_value)
        record.vowels_present = vowels_present

        db.session.commit()  # Commit changes to the database
        return jsonify(record.serialize())  # Return the serialized updated record


class RecordByEncryptedIdResource(Resource):
    # Method to handle GET requests for individual records by encrypted ID
    def get(self, encrypted_id):
        record = Record.query.filter_by(encrypted_id=encrypted_id).first()  # Retrieve the record with the given encrypted ID
        if record:  # Check if a record was found
            return jsonify(record.serialize())  # Return the serialized record
        else:
            return jsonify({"message": "Record not found"}), 404  # Return a message indicating the record was not found


api.add_resource(RecordListResource, '/encrypted_data') # endpoint for the encrypted database
api.add_resource(RecordResource, '/encrypted_data/<int:record_id>') # endpoint for induvial id search among the databse all in all
api.add_resource(RecordByEncryptedIdResource, '/encrypted_id/encrypted/<string:encrypted_id>')  # New endpoint for encrypted ID with can be searched for the decryter algorithm

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8085, debug=True)

# Notes: Entire encryption process for Ryan 
    
    # 1. Encrypt using Ceaser Cipher
        # Shift Value equals 5
        # New string equals WDFS
    
    #2. Encrypt using 2-D Iteration
        # Create Matrix
            # [W, D, F, S]
        # Substritute the first and last and so on
            # [S, F, D, W]
    
    #3. Sorting the encrypted data alphabetically
        # [S, F, D, W] to [D, F, S, W]
    
    #4. Check for vowels
        # Negetive no vowels, thus return false for vowels present
    
    #5 Create encrypted_id
        #India6-5
    
    #6 Display Final result
        # encrypted_id = India6-5
        # Encrpted_data = dfsw
