#!/usr/bin/env python3
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_file, Response
from pymongo import MongoClient
import json
import io
import csv
import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
try:
    from openpyxl import Workbook
except Exception:
    Workbook = None

client = MongoClient("mongodb://localhost:27017")
db = client['rental_db']

app = Flask(__name__)

INDEX_TEMPLATE = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>MongoDB Dashboard - rental_db</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body{padding:20px;background:#f7fafc}
    .card-hover:hover{box-shadow:0 6px 18px rgba(0,0,0,.08)}
    pre.json{background:#0b1420;color:#c8f8ff;padding:12px;border-radius:6px;overflow:auto}
    .small-muted{font-size:.9rem;color:#6c757d}
  </style>
</head>
<body>
  <div class="container">
    <div class="d-flex align-items-center mb-4">
      <h1 class="me-auto">MongoDB Dashboard</h1>
      <div class="small-muted">Database: <strong>rental_db</strong></div>
    </div>

    <div class="row g-3">
      <div class="col-lg-6">
        <div class="card p-3 card-hover">
          <h5>Collections</h5>
          <div class="list-group">
            {% for c,count in collections %}
              <a href="{{ url_for('view_collection', name=c) }}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                {{ c }}
                <span class="badge bg-secondary rounded-pill">{{ count }}</span>
              </a>
            {% endfor %}
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card p-3 card-hover">
          <h5>Insert Document</h5>
          <form id="insertForm">
            <div class="mb-2">
              <label class="form-label">Collection</label>
              <select id="collectionSelect" class="form-select">
                {% for c,count in collections %}
                  <option value="{{ c }}">{{ c }} ({{ count }})</option>
                {% endfor %}
              </select>
            </div>

            <div class="mb-2">
              <label class="form-label">Mode</label>
              <div class="btn-group" role="group">
                <button type="button" id="jsonModeBtn" class="btn btn-outline-primary active">JSON</button>
                <button type="button" id="formModeBtn" class="btn btn-outline-primary">Form</button>
              </div>
            </div>

            <div id="jsonBox" class="mb-2">
              <label class="form-label">JSON</label>
              <textarea id="jsonInput" class="form-control" rows="6">{"example":"value"}</textarea>
              <div class="mt-2 d-flex gap-2 align-items-center">
                <input id="jsonFileInput" type="file" accept=".json" class="form-control form-control-sm" style="max-width:300px">
                <button id="loadFileBtn" type="button" class="btn btn-sm btn-outline-secondary">Load file</button>
              </div>
            </div>

            <div id="formBox" class="mb-2" style="display:none">
              <label class="form-label">Fields</label>
              <div id="fieldsContainer"></div>
              <button id="addFieldBtn" type="button" class="btn btn-sm btn-outline-secondary mt-2">Add Field</button>
            </div>

            <div class="mt-3 d-flex gap-2">
              <button id="insertBtn" type="button" class="btn btn-success">Insert</button>
              <a id="viewColBtn" class="btn btn-outline-secondary" href="">View Collection</a>
            </div>

            <div id="insertResult" class="mt-3"></div>
          </form>
        </div>
      </div>
    </div>

    <div class="mt-4 small-muted">Tips: Pilih mode "Form" untuk melihat field yang terdeteksi dari dokumen pada koleksi. Anda dapat menambah field custom.</div>

  </div>

  <script>
    const collections = {{ collections_names|tojson }};
    function setViewLink(){
      const sel = document.getElementById('collectionSelect');
      document.getElementById('viewColBtn').href = '/collection/' + encodeURIComponent(sel.value);
    }
    document.getElementById('collectionSelect').addEventListener('change', () => {
      setViewLink();
      if(document.getElementById('formModeBtn').classList.contains('active')){
        loadSchema();
      }
    });
    document.getElementById('jsonModeBtn').addEventListener('click', () => {
      document.getElementById('jsonBox').style.display='block';
      document.getElementById('formBox').style.display='none';
      document.getElementById('jsonModeBtn').classList.add('active');
      document.getElementById('formModeBtn').classList.remove('active');
    });
    document.getElementById('formModeBtn').addEventListener('click', () => {
      document.getElementById('jsonBox').style.display='none';
      document.getElementById('formBox').style.display='block';
      document.getElementById('formModeBtn').classList.add('active');
      document.getElementById('jsonModeBtn').classList.remove('active');
      loadSchema();
    });

    async function loadSchema(){
      const col = document.getElementById('collectionSelect').value;
      const res = await fetch('/schema/' + encodeURIComponent(col));
      const fields = await res.json();
      buildFields(fields.map(f=>f.name));
    }

    function buildFields(fieldNames){
      const container = document.getElementById('fieldsContainer');
      container.innerHTML='';
      if(!fieldNames || fieldNames.length===0){
        addFieldRow('', '');
      } else {
        fieldNames.forEach(name => addFieldRow(name, ''));
      }
    }

    function addFieldRow(key='', val=''){
      const container = document.getElementById('fieldsContainer');
      const row = document.createElement('div');
      row.className='d-flex gap-2 mb-2';
      row.innerHTML = `
        <input class="form-control form-control-sm field-key" placeholder="field name" value="${key}">
        <input class="form-control form-control-sm field-val" placeholder="value" value="${val}">
        <button type="button" class="btn btn-sm btn-danger remove-field">✕</button>
      `;
      row.querySelector('.remove-field').addEventListener('click', ()=>row.remove());
      container.appendChild(row);
    }

    document.getElementById('addFieldBtn').addEventListener('click', ()=>addFieldRow());

    function parseValue(v){
      if(v === '') return null;
      if(v==='true') return true;
      if(v==='false') return false;
      if(!isNaN(v) && v.trim()!=='') return (v.indexOf('.')>=0)? parseFloat(v): parseInt(v);
      try {
        const parsed = JSON.parse(v);
        if(typeof parsed === 'object') return parsed;
      } catch(e){}
      return v;
    }

    document.getElementById('loadFileBtn').addEventListener('click', ()=>{
      const f = document.getElementById('jsonFileInput').files[0];
      if(!f) return alert('Pilih file .json terlebih dahulu');
      const r = new FileReader();
      r.onload = () => { document.getElementById('jsonInput').value = r.result; };
      r.readAsText(f);
    });

    async function doInsert(){
      const col = document.getElementById('collectionSelect').value;
      let doc;
      if(document.getElementById('jsonBox').style.display!=='none'){
        try {
          doc = JSON.parse(document.getElementById('jsonInput').value);
        } catch(e){
          showResult('error', 'Invalid JSON: ' + e.message);
          return;
        }
      } else {
        doc = {};
        const keys = document.querySelectorAll('#fieldsContainer .field-key');
        const vals = document.querySelectorAll('#fieldsContainer .field-val');
        for(let i=0;i<keys.length;i++){
          const k = keys[i].value.trim();
          if(!k) continue;
          doc[k] = parseValue(vals[i].value);
        }
      }
      const res = await fetch('/insert', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({collection:col, doc:doc})
      });
      if(res.ok){
        const j = await res.json();
        if(j.inserted_ids) showResult('ok', 'Inserted: ' + j.inserted_ids.join(', '));
        else showResult('ok', 'Inserted: ' + j.inserted_id);
      } else {
        const text = await res.text();
        showResult('error', text);
      }
    }

    function showResult(kind, text){
      const box = document.getElementById('insertResult');
      box.innerHTML = '';
      const el = document.createElement('div');
      el.className = (kind==='ok') ? 'alert alert-success' : 'alert alert-danger';
      el.textContent = text;
      box.appendChild(el);
      setTimeout(()=>box.innerHTML='', 5000);
    }

    document.getElementById('insertBtn').addEventListener('click', doInsert);

    setViewLink();
  </script>

</body>
</html>
'''

COL_TEMPLATE = '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Collection: {{ name }} - MongoDB Dashboard</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style> body{padding:20px;background:#f7fafc} pre.json{background:#0b1420;color:#c8f8ff;padding:12px;border-radius:6px;}</style>
</head>
<body>
  <div class="container">
    <div class="mb-3 d-flex gap-3 align-items-center">
      <a href="{{ url_for('index') }}" class="btn btn-link">&larr; Back</a>
      <h1 class="d-inline-block ms-2">Collection: {{ name }}</h1>
      <span class="badge bg-secondary">{{ count }}</span>
      <div class="ms-auto d-flex gap-2">
        <input id="searchInput" class="form-control form-control-sm" style="min-width:220px" placeholder="Search..." value="{{ q or '' }}">
        <button id="searchBtn" class="btn btn-sm btn-outline-primary">Search</button>
        <a id="exportCsvBtn" class="btn btn-sm btn-outline-secondary" href="/export/{{ name }}?format=csv{% if q %}&q={{ q }}{% endif %}">Export CSV</a>
        <a id="exportXlsBtn" class="btn btn-sm btn-outline-secondary" href="/export/{{ name }}?format=xlsx{% if q %}&q={{ q }}{% endif %}">Export XLSX</a>
      </div>
    </div>

    <div class="row g-3">
      <div class="col-lg-8">
        <div class="card p-3">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h5 class="mb-0">Documents (showing up to 100)</h5>
            <div class="btn-group" role="group">
              <button id="viewJsonBtn" class="btn btn-outline-secondary active">JSON</button>
              <button id="viewMinimalBtn" class="btn btn-outline-secondary">Minimal</button>
            </div>
          </div>

          <div id="jsonView"><pre class="json">{{ docs }}</pre></div>

          <div id="minimalView" style="display:none">
            <div id="cardsContainer" class="row g-3"></div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card p-3">
          <h5>Insert</h5>
          <div>
            <label class="form-label">Mode</label>
            <div class="btn-group mb-2" role="group">
              <button id="jsonMode" class="btn btn-outline-primary active">JSON</button>
              <button id="formMode" class="btn btn-outline-primary">Form</button>
            </div>
          </div>

          <div id="jsonBox">
            <textarea id="jsonInput" class="form-control mb-2" rows="6">{"example":"value"}</textarea>
            <div class="mt-2 d-flex gap-2 align-items-center">
              <input id="jsonFileInputCol" type="file" accept=".json" class="form-control form-control-sm" style="max-width:260px">
              <button id="loadFileBtnCol" type="button" class="btn btn-sm btn-outline-secondary">Load file</button>
            </div>
          </div>

          <div id="formBox" style="display:none">
            <div id="fieldsContainer"></div>
            <button id="addFieldBtn" class="btn btn-sm btn-outline-secondary mt-2">Add Field</button>
          </div>

          <button id="insertBtn" class="btn btn-success mt-3">Insert</button>
          <div id="insertResult" class="mt-3"></div>
        </div>
      </div>
    </div>
  </div>

<script>
  const docsForJs = {{ docs_for_js|tojson }};
  const displayFields = {{ display_fields|tojson }};
  const colName = {{ name|tojson }};

  function escapeHtml(s){
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
  }

  function renderMinimal(){
    const container = document.getElementById('cardsContainer');
    container.innerHTML='';
    if(!docsForJs || docsForJs.length===0){
      container.innerHTML = '<div class="text-muted">No documents</div>';
      return;
    }
    docsForJs.forEach(doc => {
      const col = document.createElement('div');
      col.className = 'col-md-6';
      const card = document.createElement('div');
      card.className = 'card p-3';
      const header = document.createElement('div');
      header.className = 'd-flex justify-content-between align-items-start';
      header.innerHTML = `<div><small class="text-muted">_id: ${escapeHtml(String(doc._id))}</small></div>`;
      const delBtn = document.createElement('button');
      delBtn.className = 'btn btn-sm btn-outline-danger';
      delBtn.textContent = 'Delete';
      delBtn.addEventListener('click', async ()=>{
        if(!confirm('Hapus dokumen ' + doc._id + '?')) return;
        const res = await fetch('/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({collection:colName, id:doc._id})});
        if(res.ok){
          col.remove();
        } else {
          const txt = await res.text();
          alert('Error: ' + txt);
        }
      });
      header.appendChild(delBtn);

      const body = document.createElement('div');
      body.className = 'mt-2';
      const keys = displayFields && displayFields.length? displayFields : Object.keys(doc).filter(k=>k!=='_id').slice(0,3);
      keys.forEach(k=>{
        let v = doc[k];
        if(typeof v === 'object') v = JSON.stringify(v);
        body.innerHTML += `<div><strong>${escapeHtml(k)}:</strong> ${escapeHtml(String(v ?? ''))}</div>`;
      });

      card.appendChild(header);
      card.appendChild(body);
      col.appendChild(card);
      container.appendChild(col);
    });
  }

  document.getElementById('viewJsonBtn').addEventListener('click', ()=>{
    document.getElementById('jsonView').style.display='block';
    document.getElementById('minimalView').style.display='none';
    document.getElementById('viewJsonBtn').classList.add('active');
    document.getElementById('viewMinimalBtn').classList.remove('active');
  });
  document.getElementById('viewMinimalBtn').addEventListener('click', ()=>{
    document.getElementById('jsonView').style.display='none';
    document.getElementById('minimalView').style.display='block';
    document.getElementById('viewMinimalBtn').classList.add('active');
    document.getElementById('viewJsonBtn').classList.remove('active');
    renderMinimal();
  });

  function addFieldRow(container, key='', val=''){
    const row = document.createElement('div');
    row.className='d-flex gap-2 mb-2';
    row.innerHTML = `
      <input class="form-control form-control-sm field-key" placeholder="field name" value="${key}">
      <input class="form-control form-control-sm field-val" placeholder="value" value="${val}">
      <button type="button" class="btn btn-sm btn-danger remove-field">✕</button>
    `;
    row.querySelector('.remove-field').addEventListener('click', ()=>row.remove());
    container.appendChild(row);
  }

  function buildFields(fieldNames){
    const container = document.getElementById('fieldsContainer');
    container.innerHTML='';
    if(!fieldNames || fieldNames.length===0){
      addFieldRow(container,'','');
    } else {
      fieldNames.forEach(name => addFieldRow(container,name,''));
    }
  }

  document.getElementById('jsonMode').addEventListener('click', ()=>{
    document.getElementById('jsonBox').style.display='block';
    document.getElementById('formBox').style.display='none';
    document.getElementById('jsonMode').classList.add('active');
    document.getElementById('formMode').classList.remove('active');
  });

  document.getElementById('formMode').addEventListener('click', async ()=>{
    document.getElementById('jsonBox').style.display='none';
    document.getElementById('formBox').style.display='block';
    document.getElementById('formMode').classList.add('active');
    document.getElementById('jsonMode').classList.remove('active');
    const res = await fetch('/schema/' + encodeURIComponent(colName));
    const fields = await res.json();
    buildFields(fields.map(f=>f.name));
  });

  document.getElementById('addFieldBtn').addEventListener('click', ()=> addFieldRow(document.getElementById('fieldsContainer')));

  document.getElementById('loadFileBtnCol').addEventListener('click', ()=>{
    const f = document.getElementById('jsonFileInputCol').files[0];
    if(!f) return alert('Pilih file .json terlebih dahulu');
    const r = new FileReader();
    r.onload = () => { document.getElementById('jsonInput').value = r.result; };
    r.readAsText(f);
  });

  document.getElementById('searchBtn').addEventListener('click', ()=>{
    const q = document.getElementById('searchInput').value.trim();
    const params = new URLSearchParams();
    if(q) params.set('q', q);
    window.location = '/collection/' + encodeURIComponent(colName) + '?' + params.toString();
  });

  function parseValue(v){
    if(v === '') return null;
    if(v==='true') return true;
    if(v==='false') return false;
    if(!isNaN(v) && v.trim()!=='') return (v.indexOf('.')>=0)? parseFloat(v): parseInt(v);
    try {
      const parsed = JSON.parse(v);
      if(typeof parsed === 'object') return parsed;
    } catch(e){}
    return v;
  }

  async function doInsert(){
    const col = colName;
    let doc;
    if(document.getElementById('jsonBox').style.display!=='none'){
      try {
        doc = JSON.parse(document.getElementById('jsonInput').value);
      } catch(e){
        showResult('error', 'Invalid JSON: ' + e.message);
        return;
      }
    } else {
      doc = {};
      const keys = document.querySelectorAll('#fieldsContainer .field-key');
      const vals = document.querySelectorAll('#fieldsContainer .field-val');
      for(let i=0;i<keys.length;i++){
        const k = keys[i].value.trim();
        if(!k) continue;
        doc[k] = parseValue(vals[i].value);
      }
    }
    const res = await fetch('/insert', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({collection:col, doc:doc})
    });
    if(res.ok){
      const j = await res.json();
      showResult('ok', 'Inserted: ' + j.inserted_id);
      // update local docs and re-render minimal view
      docsForJs.unshift(Object.assign({_id: j.inserted_id}, doc));
    } else {
      const text = await res.text();
      showResult('error', text);
    }
  }

  function showResult(kind, text){
    const box = document.getElementById('insertResult');
    box.innerHTML='';
    const el = document.createElement('div');
    el.className = (kind==='ok') ? 'alert alert-success' : 'alert alert-danger';
    el.textContent = text;
    box.appendChild(el);
    setTimeout(()=>box.innerHTML='', 5000);
  }

  document.getElementById('insertBtn').addEventListener('click', doInsert);

</script>

</body>
</html>
'''

def guess_type(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'boolean'
    if isinstance(v, (int, float)):
        return 'number'
    if isinstance(v, str):
        return 'string'
    if isinstance(v, list):
        return 'array'
    if isinstance(v, dict):
        return 'object'
    if isinstance(v, datetime.datetime):
        return 'date'
    return 'string'


@app.route('/')
def index():
    cols = db.list_collection_names()
    collections = []
    for c in cols:
        try:
            count = db[c].count_documents({})
        except Exception:
            count = 0
        collections.append((c, count))
    names = [c for c, _ in collections]
    return render_template_string(INDEX_TEMPLATE, collections=collections, collections_names=names)


@app.route('/collection/<name>')
def view_collection(name):
  q = request.args.get('q')
  # sample string keys to search over
  sample_docs = list(db[name].find().limit(50))
  keys = set()
  for d in sample_docs:
    for k, v in d.items():
      if k == '_id':
        continue
      if isinstance(v, str):
        keys.add(k)
  keys = [k for k in keys]
  if q:
    # if we have string keys, build regex OR query, otherwise try _id lookup
    if keys:
      or_clause = [{k: {'$regex': q, '$options': 'i'}} for k in keys]
      query = {'$or': or_clause}
      docs_cursor = list(db[name].find(query).limit(100))
    else:
      try:
        docs_cursor = list(db[name].find({'_id': ObjectId(q)}).limit(100))
      except Exception:
        docs_cursor = []
  else:
    docs_cursor = list(db[name].find().limit(100))
  docs_json = dumps(docs_cursor, indent=2)
  docs_for_js = []
  for doc in docs_cursor:
    doc2 = {}
    for k, v in doc.items():
      if k == '_id':
        doc2[k] = str(v)
      else:
        try:
          doc2[k] = v
        except Exception:
          doc2[k] = str(v)
    docs_for_js.append(doc2)
  # choose a few fields to show in minimal view
  display_fields = []
  if docs_for_js:
    first = docs_for_js[0]
    for k in first.keys():
      if k == '_id':
        continue
      display_fields.append(k)
      if len(display_fields) >= 3:
        break
  # Ensure cars minimal view shows plate_number and status when available
  if name == 'cars':
    preferred = []
    for f in ('plate_number', 'status'):
      if any(f in d for d in docs_for_js):
        preferred.append(f)
    if preferred:
      # put preferred fields first
      display_fields = preferred + [f for f in display_fields if f not in preferred]
  try:
    count = db[name].count_documents({})
  except Exception:
    count = len(docs_cursor)
  return render_template_string(COL_TEMPLATE, name=name, docs=docs_json, count=count, docs_for_js=docs_for_js, display_fields=display_fields, q=q)


@app.route('/delete', methods=['POST'])
def delete_doc():
  payload = None
  if request.is_json:
    payload = request.get_json()
  else:
    try:
      payload = json.loads(request.data or b'{}')
    except Exception:
      payload = None
  if not payload:
    return "Invalid payload", 400
  col = payload.get('collection')
  id_str = payload.get('id')
  if not col or not id_str:
    return "collection or id missing", 400
  # try delete by ObjectId first
  try:
    oid = ObjectId(id_str)
    res = db[col].delete_one({'_id': oid})
  except Exception:
    res = db[col].delete_one({'_id': id_str})
  if res.deleted_count:
    return jsonify({'status': 'ok', 'deleted': id_str})
  return "Not found", 404


@app.route('/schema/<name>')
def get_schema(name):
    docs = list(db[name].find().limit(200))
    field_types = {}
    for doc in docs:
        for k, v in doc.items():
            if k == '_id':
                continue
            t = guess_type(v)
            if k not in field_types:
                field_types[k] = t
    fields = [{'name': k, 'type': field_types[k]} for k in field_types]
    return jsonify(fields)


@app.route('/insert', methods=['POST'])
def insert():
    if request.is_json:
        payload = request.get_json()
        col = payload.get('collection')
        data = payload.get('doc')
    else:
        col = request.form.get('collection')
        doc_text = request.form.get('doc')
        if not doc_text:
            return "No document provided", 400
        try:
            data = json.loads(doc_text)
        except Exception as e:
            return f"Invalid JSON: {e}", 400
    if not col:
        return "No collection specified", 400

    # support array insert
    if isinstance(data, list):
        res = db[col].insert_many(data)
        if request.is_json:
            return jsonify({'status': 'ok', 'inserted_ids': [str(i) for i in res.inserted_ids]})
        return redirect(url_for('view_collection', name=col))
    else:
        result = db[col].insert_one(data)
        if request.is_json:
            return jsonify({'status': 'ok', 'inserted_id': str(result.inserted_id)})
        return redirect(url_for('view_collection', name=col))


@app.route('/export/<name>')
def export_collection(name):
  fmt = request.args.get('format', 'csv')
  q = request.args.get('q')
  # build optional query from q param (same logic as view_collection)
  sample_docs = list(db[name].find().limit(20))
  keys = set()
  for d in sample_docs:
    keys.update(d.keys())
  keys = [k for k in keys if k != '_id']
  if q and keys:
    or_clause = [{k: {'$regex': q, '$options': 'i'}} for k in keys]
    query = {'$or': or_clause}
    docs = list(db[name].find(query))
  else:
    docs = list(db[name].find())

  # prepare rows
  # gather all keys
  all_keys = set()
  for d in docs:
    all_keys.update(d.keys())
  # ensure _id first
  all_keys = ['_id'] + [k for k in all_keys if k != '_id']

  if fmt in ('xlsx','xls') and Workbook is not None:
    wb = Workbook()
    ws = wb.active
    ws.append(all_keys)
    for d in docs:
      row = []
      for k in all_keys:
        v = d.get(k, '')
        if k == '_id':
          v = str(v)
        if isinstance(v, (dict, list)):
          v = json.dumps(v)
        row.append(v if v is not None else '')
      ws.append(row)
    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return send_file(bio, as_attachment=True, download_name=f'{name}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

  # default CSV
  si = io.StringIO()
  writer = csv.writer(si)
  writer.writerow(all_keys)
  for d in docs:
    row = []
    for k in all_keys:
      v = d.get(k, '')
      if k == '_id':
        v = str(v)
      if isinstance(v, (dict, list)):
        v = json.dumps(v)
      row.append(v)
    writer.writerow(row)
  output = si.getvalue()
  return (output, 200, {'Content-Type': 'text/csv', 'Content-Disposition': f'attachment; filename="{name}.csv"'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
