from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import pymongo

app = Flask(__name__)

# Define an empty DataFrame
df = pd.DataFrame(columns=['Topic','Content', 'Title', 'Num_Links'])

# Define a POST endpoint to add wiki topic to the DataFrame
@app.route('/api/add_topic', methods=['POST'])
def add_topic():
    
    # retreive content from request then retrieve html content from wikipedia page.
    content = request.json
    url='https://en.wikipedia.org/wiki/' + content['topic']
    response = requests.get(url)
    print(response.status_code)
    
    # create keys and values list for response_dict
    keys = ['Topic','Content', 'Title', 'Num_Links']
    values=[]
    topic_list=[]
    para_list=[]
    title_list=[]
    links_list=[]
    
    # Add topic to topic list then values list
    topic_list.append(str(content['topic']))
    values.append(topic_list)
    
    # Add content to paragraph list then values list
    para_list.append(str(response.content[0:100]))
    values.append(para_list)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the page title then add to title list.
    title = soup.find('title').text
    title_list.append(title)
    values.append(title_list)
    
    # Find all the hyperlinks on the page then add to links list.
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    links_list.append(len(links))
    values.append(links_list)
    #print(keys)
    #print(values)
    
    # create response_dict from keys adn values lists.
    response_dict = dict(zip(keys,values))
    
    # Convert the response_dict to the DataFrame
    global df
    response_df=pd.DataFrame(response_dict)
    df=pd.concat([df,response_df], ignore_index=True)
    df.set_index('Topic')
    print(df)
    
    #print(response_dict)
    return jsonify(response_dict)

# Define a DELETE endpoint to delete data from the DataFrame
@app.route('/api/del_topic', methods=['DELETE'])
def del_topic():
    
    # retrieve content from request to extract topic to delete from the DataFrame.
    content = request.json
    global df
    print(df)
    df.drop(df[df['Topic'] == content['topic']].index, inplace=True)
    print(df)
    response = df.to_json(orient=('columns'))
    return jsonify(response)

# Define an PUT endpoint to update data in the DataFrame
@app.route('/api/update_topic', methods=['PUT'])
def update_topic():
    
    # retrieve content from request to extract topic to update the topic in the DataFrame.
    content = request.json
    global df
    print(df)

    if content['title'] != "":
        df.loc[df['Topic'] == content['topic'], 'Title'] = content['title']
    if content['content'] != "":
        df.loc[df['Topic'] == content['topic'], 'Content'] = content['content']
    if content['num_links'] != "":
        df.loc[df['Topic'] == content['topic'], 'Num_Links'] = content['num_links']
    print(df)
    response = df.to_json(orient=('columns'))
    return jsonify(response)

# Define an PUT endpoint to save the topic data in the Mongodb (wiki)
@app.route('/api/save_topic', methods=['PUT'])
def save_topic():
    
    # Declare global df 
    global df
    #print(df)
    
    #Connecting to MongoDB
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        if client:
            print("Connected to MongoDB server")
            client.server_info() # ping the server to verify the connection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB server: {e}")
    
    # drop wiki database first if exist.    
    client.drop_database('wiki')
    print(client.list_database_names())
    
    # Initiate Wiki DB and collection
    db = client['wiki']
    wiki_collection = db['wiki_data']
    
    # Insert data into collection from the DataFrame
    df_topics = df.to_dict(orient='records')
    wiki_collection.insert_many(df_topics)

    # check if collection created and data inserted
    print(client.list_database_names())
    print(db.list_collection_names())
    print('Number of records:', wiki_collection.count_documents({}))
    
    # Close the MongoDB connection
    client.close()
    
    # Return a success message
    response = {
        'message': 'Records Inserted to DB'
    }
    return jsonify(response)

# Define GET endpoint to retrieve all the topic data from the Mongodb (wiki)
@app.route('/api/get_topic', methods=['GET'])
def get_topic():
    
    # Connecting to MongoDB
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        if client:
            print("Connected to MongoDB server")
            client.server_info() # ping the server to verify the connection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to MongoDB server: {e}")
    
    # Initiate Wiki DB and collection
    db = client['wiki']
    wiki_collection = db['wiki_data']
    
    # Retrieve all topic data and store in wiki_df DataFrame
    wiki_data = wiki_collection.find({})
    wiki_df = pd.DataFrame(list(wiki_data))
    #print(wiki_df)
    
    # Convert wiki_df to dict and store it in response
    response = wiki_df.to_dict(orient='records')
    print(response)
    
    # Close the MongoDB connection
    client.close()
    
    # return response (using json.dumps to fix object_id is not serializable)
    return jsonify(json.dumps(response, default=str))
    

if __name__ == '__main__':
    port=8001
    app.run(debug=True, port=port)
    
    
