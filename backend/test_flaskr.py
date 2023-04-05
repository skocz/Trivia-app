import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import db, setup_db, Question, Category
# from dotenv import load_dotenv

# load_dotenv()

# database_name_test = os.getenv('database_name')
# database_path_test = os.getenv('database_path')

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    def setUp(self):
        # """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia_test"
        # self.database_path = "postgresql://joannas@localhost:5432/trivia_test"
        # setup_db(self.app, self.database_path)
       
        # with self.app.app_context():
            # self.db = SQLAlchemy()
            # self.db.init_app(self.app)
            # create all tables
            # db.create_all()
       
        self.new_question = {
            'question': 'What is the capital of Australia?',
            'answer': 'Canberra',
            'category': 3,
            'difficulty': 2
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_categories_success(self):
    # Test for successful operation
        res = self.client().get('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_post_categories_error(self):
        # Test for error when requesting with invalid method
        res = self.client().post('/api/v1.0/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed.')

    def test_404_get_questions_beyond_valid_page(self):
        # Test for error when no questions are found
        res = self.client().get('/api/v1.0/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')

    def test_get_questions_by_page_success(self):
        # Test for successful retrieval of questions by page
        res = self.client().get('/api/v1.0/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)
    
    # deletion of a question
    def test_delete_question_success(self):
        # Test for successful deletion of a question
        # question = Question(question='What is the capital of Canada?', answer='Ottawa', category=1, difficulty=1)
        # question.insert()

        res = self.client().delete('/api/v1.0/questions/5')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 5)
        self.assertEqual(question, None)

    def test_delete_question_failure(self):
        # Test for failure when trying to delete a non-existent question
        res = self.client().delete('/api/v1.0/questions/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')

    # questions by category
    def test_get_questions_by_category_success(self):
        # Test for successful retrieval of questions by category
        res = self.client().get('/api/v1.0/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_get_questions_by_category_failure(self):
        # Test for error when category doesn't exist
        res = self.client().get('/api/v1.0/categories/999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found.')

    #  creation of a new question
    def test_create_question_success(self):
    #     # Test for successful creation of a new question
        res = self.client().post('/api/v1.0/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']) > 0)
    
    # search of questions
    def test_search_questions_success(self):
        # Test for successful search of questions
        search_term = 'title'
        res = self.client().post('/api/v1.0/questions/search', json={'searchTerm': search_term})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 2)
        self.assertEqual(data['current_category'], None)

    def test_search_questions_missing_search_term_failure(self):
        # Test for failure when search term is missing
        res = self.client().post('/api/v1.0/questions/search', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity.')

    def test_play_quiz_success(self):
        # Create a quiz category
        # "answer": "Maya Angelou",
        # "category": 4,
        # "difficulty": 2,
        # "id": 5,
        # "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        # },

        # Play a quiz with the quiz category
        res = self.client().post('/api/v1.0/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'id': 9}
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    # def test_play_quiz_failure(self):
        # Play a quiz with no questions
        # res = self.client().post('/api/v1.0/quizzes', json={
        #     'previous_questions': []
        # })
        # data = json.loads(res.data)
        
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(data['success'], True)
        # self.assertFalse(data['question'])
        
        # Play a quiz with an invalid quiz category
        # res = self.client().post('/api/v1.0/quizzes', json={
        #     'previous_questions': [],
        #     'quiz_category': {'id': 1000, 'type': 'Invalid Category'}
        # })
        # data = json.loads(res.data)
        
        # self.assertEqual(res.status_code, 404)
        # self.assertEqual(data['success'], False)
        # self.assertEqual(data['message'], 'Not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()