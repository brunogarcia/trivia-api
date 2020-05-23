import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


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

    """
    TODO
    Write at least one test for each test
    for successful operation and for expected errors.
    """

    def test_retrieve_categories(self):
        """GET categories """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

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
        self.assertEqual(len(data['questions']), 10)

        # Total questions
        self.assertEqual(data['total_questions'], 19)

        # Categories
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
