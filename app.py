from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgresql@localhost:5432/todoapp'
db=SQLAlchemy(app)

migrate=Migrate(app,db)

class Todo(db.Model):
    __tablename__='todos'
    id=db.Column(db.Integer,primary_key=True)
    description=db.Column(db.String(),nullable=False)
    completed=db.Column(db.Boolean, nullable=False, default=False)
    list_id=db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__='todolists'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(),nullable=False)
    todos=db.relationship('Todo',backref='list',lazy=True)

#db.create_all()
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))


@app.route('/todos/<todo_id>/set-completed',methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed=request.get_json()['completed']
        todo=Todo.query.get(todo_id)
        todo.completed=completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/create', methods=['POST'])
def create_todo():
  description = request.get_json()['description']
  todo = Todo(description=description)
  db.session.add(todo)
  db.session.commit()
  return jsonify({
      'description':todo.description
  })
  
@app.route('/list/<list_id>')
def get_list_todos():
    return render_template('index.html', data=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))