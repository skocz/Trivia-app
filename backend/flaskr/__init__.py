import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random
import math
from models import db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  # app.app_context().push()
  # with app.app_context():
  setup_db(app)

  CORS(app)

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response
  
  @app.route('/api/v1.0/categories', methods=['GET'])
  def get_categories():
    with app.app_context():
      categories = Category.query.all()
      formatted_categories = {category.id: category.type for category in categories}
    return jsonify({
      'success': True,
      'categories': formatted_categories
    })
  
  @app.route('/api/v1.0/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    categories = Category.query.all()
    formatted_categories = {category.id: category.type for category in categories}
    
    total_questions = len(questions)
    if total_questions == 0:
      abort(404, description='No questions found.')
    
    if (page > math.ceil(total_questions/10)) or (page < 1):
      abort(404, description='Invalid page number.')

    return jsonify({
      'success': True,
      'questions': formatted_questions[start:end],
      'total_questions': len(questions),
      'categories': formatted_categories,
      'current_category': None
    })
  
  @app.route('/api/v1.0/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
      })
    except:
      db.session.rollback()
      abort(404)
    finally:
      db.session.close()
  
  @app.route('/api/v1.0/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    category = Category.query.filter(Category.id == category_id).one_or_none()
    if category is None:
      abort(404)

    questions = Question.query.filter(Question.category == category_id).all()
    formatted_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': category.format()
    })

  @app.route('/api/v1.0/questions', methods=['POST'])
  def create_question():
    data = request.get_json()

    # check for missing fields
    if not data.get('question') or not data.get('answer') or not data.get('category') or not data.get('difficulty'):
      abort(400, 'Missing required fields')

    question = data.get('question')
    answer = data.get('answer')
    category = data.get('category')
    difficulty = data.get('difficulty')

    try:
      new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id,
        'questions': [question.format() for question in Question.query.all()]
      })
    except:
      db.session.rollback()
      abort(422)
    finally:
      db.session.close()
    
  @app.route('/api/v1.0/questions/search', methods=['POST'])
  def search_questions():
    data = request.get_json()

    search_term = data.get('searchTerm')

    if search_term:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      if len(questions) == 0:
        abort(404)

      return jsonify({
          'success': True,
          'questions': [question.format() for question in questions],
          'total_questions': len(questions),
          'current_category': None
      })
    else:
      abort(422)

  @app.route('/api/v1.0/quizzes', methods=['POST'])
  def play_quiz():
    data = request.get_json()

    previous_questions = data.get('previous_questions', [])
    quiz_category = data.get('quiz_category', None)
    
    if quiz_category:
      category_id = quiz_category['id']
      if category_id == 0:
        questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category == category_id, ~Question.id.in_(previous_questions)).all()
    else:
      questions = Question.query.filter(~Question.id.in_(previous_questions)).all()

    if len(questions) > 0:
      question = random.choice(questions).format()
      return jsonify({
        'success': True,
        'question': question
      })
    else:
      return jsonify({
        'success': True,
        'question': None
      })
    
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource not found."
    }), 404
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed."
    }), 405
  
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable entity."
    }), 422
  
  return app

# python -c 'import os; print(os.urandom(16))'
# # b'_5#y2L"F4Q8z\n\xec]/'

# def create_app(test_config=None):
#   # create and configure the app
#   app = Flask(__name__)
#   setup_db(app)
#   CORS(app)

#   # Set Access-Control-Allow headers for all routes
#   @app.after_request
#   def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE OPTION')
#     return response
  


  # app.config.from_mapping(
  #   SECRET_KEY='dev', 
  #   DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
  # )
  # if test_config is None:
  # # load the instance config, if it exists, when not testing
  #   app.config.from_pyfile('config.py', silent=True)
  # else:
  #   # load the test config if passed in
  #   app.config.from_mapping(test_config)

  # try:
  #   os.makedirs(app.instance_path)
  # except OSError:
  #   pass

  # @app.route('/')
  # def read():
  #   return jsonify({'messages': 'hi'})
  # return app
    

  
