from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Define an empty DataFrame
df = pd.DataFrame(columns=['Name', 'Age', 'City'])

# Define a POST endpoint to add data to the DataFrame
@app.route('/api/add_data', methods=['POST'])
def add_data():
    # Get the data from the request body
    data = request.json

    # Add the data to the DataFrame
    global df
    df = df.append(data, ignore_index=True)

    # Return a success message
    response = {
        'message': 'Data added successfully'
    }
    return jsonify(response)

# Define a GET endpoint to retrieve all data from the DataFrame
@app.route('/api/get_data', methods=['GET'])
def get_data():
    # Return the data as a JSON object
    data = df.to_dict('records')
    return jsonify(data)

if __name__ == '__main__':
    port=8001
    app.run(debug=True, port=port)

