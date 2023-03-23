import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import  db, setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

# Set Access-Control-Allow headers for all routes
  @app.after_request
  def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE OPTION')
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
    if len(formatted_questions) == 0:
      abort(404)

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
      abort(422)
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
      "message": "Resource not found"
    }), 404

  return app
