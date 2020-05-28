import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.user = "postgres"
        self.pwd = 'postgres'
        self.host = 'localhost'
        self.port = '5432'
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}:{}/{}".format(
            self.user,
            self.pwd,
            self.host,
            self.port,
            self.database_name
        )

        # new question
        self.new_question = {
            'id': 24,
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 2,
            'category': 1,
        }

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_retrieve_categories(self):
        """GET categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)

    def test_retrieve_questions(self):
        """
        Test retrieve questions
        """
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        # Questions
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 10)

        # Total questions
        self.assertEqual(data['total_questions'], 19)

        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
        self.assertIsInstance(data['categories'], dict)
        self.assertEqual(data['current_category'], None)

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        '''
        Test requesting questions beyond valid page
        '''
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_question(self):
        """
        CREATE question
        """
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'], 24)

    def test_delete_question(self):
        """
        DELETE question
        """
        res = self.client().delete('/questions/24')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 24)

    def test_404_send_not_valid_id_for_delete_question(self):
        """
        Test send not valid id for delete a question
        """
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        """
        Search questions with results
        """
        res = self.client().post(
            '/search',
            json={'searchTerm': 'Taj Mahal'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['current_category'], None)

    def test_search_questions_without_results(self):
        """
        Search questions without results
        """
        res = self.client().post(
            '/search',
            json={'searchTerm': 'aaaaa'}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_by_category(self):
        """
        Get questions by category
        """
        res = self.client().get('/categories/1/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertIsInstance(data['questions'], list)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)

    def test_404_send_category_without_questions(self):
        """
        Get category without questions
        """
        res = self.client().get('/categories/1000/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_quizzes_without_category_and_without_previous_questions(self):
        """
        Test quizzes without category or previous questions
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '0',
                'type': 'All'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def test_quizzes_with_category_and_without_previous_questions(self):
        """
        Test quizzes without previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def test_quizzes_with_category_and_with_some_previous_questions(self):
        """
        Test quizzes with some previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIsInstance(data['question'], dict)

    def test_quizzes_with_category_and_with_all_the_previous_questions(self):
        """
        Test quizzes with all the previous questions
        for the requested category
        """
        res = self.client().post('/quizzes', json={
            'previous_questions': [13, 14, 15],
            'quiz_category': {
                'id': '3',
                'type': 'Geography'
            }
        })
        data = json.loads(res.data)

        # Status code
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
