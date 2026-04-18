#!/usr/bin/env python3
from flask import Flask, render_template_string, request, redirect, url_for
from pymongo import MongoClient
import json
from bson.json_util import dumps

client = MongoClient("mongodb://localhost:27017")
db = client['rental_db']

app = Flask(__name__)

INDEX_TEMPLATE = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>MongoDB GUI - rental_db</title>
  <style>body{font-family:Arial,Helvetica,sans-serif;} pre{background:#f6f8fa;padding:8px;border-radius:4px;}</style>
</head>
<body>
  <h1>MongoDB GUI — `rental_db`</h1>
  <h2>Collections</h2>
  <ul>
    {% for c in collections %}
      <li><a href="{{ url_for('view_collection', name=c) }}">{{ c }}</a></li>
    {% endfor %}
  </ul>

  <h2>Quick Insert</h2>
  <form method="post" action="{{ url_for('insert') }}">
    <label>Collection: <input name="collection" value="cars"></label>
    <br>
    <label>JSON document:</label>
    <br>
    <textarea name="doc" rows="4" cols="80">{"example":"value"}</textarea>
    <br>
    <button type="submit">Insert</button>
  </form>

  <p>Click a collection to view documents.</p>
</body>
</html>
'''

COL_TEMPLATE = '''
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Collection: {{ name }}</title></head>
<body>
  <a href="{{ url_for('index') }}">&larr; Back</a>
  <h1>Collection: {{ name }}</h1>
  <h2>Documents (showing up to 100)</h2>
  <pre>{{ docs }}</pre>
  <h3>Insert another document</h3>
  <form method="post" action="{{ url_for('insert') }}">
    <input type="hidden" name="collection" value="{{ name }}">
    <textarea name="doc" rows="4" cols="80">{"example":"value"}</textarea>
    <br>
    <button type="submit">Insert</button>
  </form>
</body>
</html>
'''

@app.route('/')
def index():
    collections = db.list_collection_names()
    return render_template_string(INDEX_TEMPLATE, collections=collections)

@app.route('/collection/<name>')
def view_collection(name):
    docs = list(db[name].find().limit(100))
    docs_json = dumps(docs, indent=2)
    return render_template_string(COL_TEMPLATE, name=name, docs=docs_json)

@app.route('/insert', methods=['POST'])
def insert():
    col = request.form.get('collection')
    doc = request.form.get('doc')
    try:
        data = json.loads(doc)
    except Exception as e:
        return f"Invalid JSON: {e}", 400
    db[col].insert_one(data)
    return redirect(url_for('view_collection', name=col))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
