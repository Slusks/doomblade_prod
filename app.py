from flask import Flask, render_template, request, jsonify
import json

import plotly.graph_objs as go
import plotly.io as pio
import os

#import firebase_admin
#from firebase_admin import credentials, firestore

# Initialize Firebase Admin with service account key JSON file
#cred = credentials.Certificate('path/to/your/firebase-service-account.json')
#firebase_admin.initialize_app(cred)

# Initialize Firestore
#db = firestore.client()

#to run: flask run
app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials, db

# Initialize the Firebase app
# Load Firebase credentials from environment variables
firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
if firebase_creds_json:
    cred_dict = json.loads(firebase_creds_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://doomblade-b08ea-default-rtdb.firebaseio.com/'
    })


# Load data from Firebase
def fetch_data_from_firebase(path):
    ref = db.reference(path)
    return ref.get()

# Get data for 'home' and 'EDH'
data = fetch_data_from_firebase('home')
EDH_data = fetch_data_from_firebase('EDH')

# Now 'data' and 'EDH_data' contain the same structure as before
print(data)
print(EDH_data)

    
@app.route('/')
def index():
    formats = [list(d.keys())[0] for d in data]  # Extract formats from the data
    formats = ["standard"] + [item for item in formats if item !="standard"]
    return render_template('index.html', formats=formats)

@app.route('/plot', methods=['POST'])
def plot():
    print("/plot run")
    selected_format = request.form['format']
    
    # Find the selected data
    selected_data = next((item[selected_format] for item in data if selected_format in item), None)
    if not selected_data:
        return jsonify({'error': 'Data not found for the selected format.'})

    # Extract X and Y data
    x_data = selected_data[0]
    y_data = selected_data[1]

    # Create a histogram using Plotly

    fig = go.Figure(data=[go.Bar(x=y_data, y=x_data,
                             orientation='h',
                             marker_color="black",
                      hovertemplate='%{label}: %{value:,.0f}<extra></extra>' )])
    fig.update_layout(title=f'What dies to Doomblade in {selected_format}?', 
                      xaxis_title='Number of Creatures that Die to Spell', 
                      yaxis_title='Card Names', 
                      xaxis=dict(tickformat=',d'))
    
    # Convert the plot to JSON format
    graph_json = pio.to_json(fig)

    return jsonify(graph_json)

@app.route("/commander", methods=["GET"])
def commander():
    # Load data from EDH_plotly_formatted_data.json instead of plotly_formatted_data.json
    data=EDH_data

    
    # Assuming the data has the same structure as the original plot function
    commander_data = data[0]['commander']
    print("commander_data", commander_data)
    card_names = commander_data[0]  # List of card names
    card_values = commander_data[1]  # Corresponding list of values

    # Normalize the values so that they sum up to 250
    total_value = sum(card_values)

    normalized_values = [round((value / 250) * 100,2) for value in card_values]

    mtg_colors = ["hsl(54, 37%, 84%)", 
                  "hsl(220, 70%, 50%)",  
                  "hsl(0, 0%, 10%)", 
                  "hsl(0, 70%, 40%)", 
                  "hsl(120, 70%, 40%)"]

       # Generate the colors by repeating the mtg_colors pattern
    wedge_colors = [mtg_colors[i % len(mtg_colors)] for i in range(len(card_names))]


    # Create the pie chart trace
    trace = go.Pie(labels=card_names, 
                   values=normalized_values,
                   marker = dict(colors=wedge_colors,
                   line=dict(color='black', width=2)))

    # Define the layout of the pie chart
    layout = go.Layout(
        title='Percentag of the top 250 Creatures Targetable in Commander',
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    # Combine the trace and layout into a figure
    fig = go.Figure(data=[trace], layout=layout)

    edh_graph = pio.to_json(fig)
    # Return the JSON data to be rendered by the client
    return render_template('commander.html', graph_json=edh_graph)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
