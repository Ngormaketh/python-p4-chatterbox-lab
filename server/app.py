from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

# GET /messages
@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    message_dicts = [message.to_dict() for message in messages]
    return make_response(jsonify(message_dicts), 200)

# POST /messages
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    try:
        new_message = Message(
            body=data.get('body'),
            username=data.get('username')
        )
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

# PATCH /messages/<int:id>
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()

    if 'body' in data:
        message.body = data['body']
    if 'username' in data:
        message.username = data['username']

    message.updated_at = datetime.utcnow()  # Ensure updated_at changes
    db.session.commit()

    return make_response(jsonify(message.to_dict()), 200)

# DELETE /messages/<int:id>
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555)
