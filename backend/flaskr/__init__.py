from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

CATEGORY_ALL = '0'
QUESTIONS_PER_PAGE = 10


def get_ids_from_questions(questions, previous_ids):
    '''
    First create a formatted list of the current questions
    And then compare both list and return a list of ids
    '''
    questions_formatted = [q.format() for q in questions]
    current_ids = [q.get('id') for q in questions_formatted]

    ids = list(set(current_ids).difference(previous_ids))

    return ids


def create_app(test_config=None):
    '''
    Create and configure the app
    '''
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        '''
        CORS Headers
        '''
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'
        )
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET,PUT,POST, DELETE, OPTIONS'
        )

        return response

    @app.route('/categories', methods=['GET'])
    def retrieve_categories():
        '''
        Fetches a dictionary of categories in which the keys are the ids and
        the value is the corresponding string of the category.
        '''
        try:
            categories = Category.query.order_by(Category.id).all()

            return jsonify({
              'success': True,
              'categories': {
                category.id: category.type for category in categories
              }
            })
        except Exception:
            abort(422)

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        '''
        Endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        '''
        try:
            # page
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            # questions
            questions = Question.query.order_by(Question.id).all()
            questions_formatted = [
              question.format() for question in questions
            ]
            questions_paginated = questions_formatted[start:end]

            # categories
            categories = Category.query.order_by(Category.id).all()
            categories_formatted = {
              category.id: category.type for category in categories
            }

            if len(questions_paginated) == 0:
                abort(404)
            else:
                return jsonify({
                  'success': True,
                  'questions': questions_paginated,
                  'total_questions': len(Question.query.all()),
                  'categories': categories_formatted,
                  'current_category': None,
                })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        Endpoint to DELETE question using a question ID.

        TEST: When you click the trash icon next to a question,
        the question will be removed.
        This removal will persist in the database and when
        you refresh the page.
        '''
        try:
            question = Question.query \
              .filter(Question.id == question_id) \
              .one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
              'success': True,
            })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

    @app.route('/questions', methods=['POST'])
    def create_or_search_question():
        '''
        Endpoint to create a new question
        and get questions based on a search term
        '''

        # Get raw data
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                # Search the term
                questions = Question.query \
                  .order_by(Question.id) \
                  .filter(Question.question.ilike('%{}%'.format(search)))

                questions_formatted = [
                  question.format() for question in questions
                ]

                return jsonify({
                  'success': True,
                  'questions': questions_formatted,
                  'total_questions': len(questions.all()),
                  'current_category': None,
                })
            else:
                # Create question
                question = Question(
                  question=question,
                  answer=answer,
                  difficulty=difficulty,
                  category=category
                )

                # Update db
                question.insert()

                return jsonify({
                  'success': True,
                  'created': question.id,
                })
        except Exception:
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        '''
        Create a GET endpoint to get questions based on category.
        '''
        try:
            # page
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            # questions
            questions = Question.query \
                .order_by(Question.id) \
                .filter(Question.category == category_id) \
                .all()

            questions_formatted = [
              question.format() for question in questions
            ]

            questions_paginated = questions_formatted[start:end]

            if len(questions_paginated) == 0:
                abort(404)
            else:
                return jsonify({
                  'success': True,
                  'questions': questions_paginated,
                  'total_questions': len(questions),
                  'current_category': category_id
                })
        except Exception as e:
            if '404' in str(e):
                abort(404)
            else:
                abort(422)

    @app.route('/quizzes', methods=['POST'])
    def retrieve_quizzes():
        '''
        Endpoint to get questions to play the quiz.
        '''
        try:
            # Get raw data
            questions = None
            body = request.get_json()
            quiz_category = body.get('quiz_category', None)
            previous_ids = body.get('previous_questions', None)
            category_id = quiz_category.get('id')

            # Check category
            if category_id == CATEGORY_ALL:
                # Get all the questions
                questions = Question.query.all()
            else:
                # Get the questions by the requested category
                questions = Question.query \
                    .filter(Question.category == category_id) \
                    .all()

            # Get the list of ids
            ids = get_ids_from_questions(questions, previous_ids)

            if len(ids) == 0:
                # If the list is empty return no question
                return jsonify({
                  'success': True,
                  'question': None
                })
            else:
                # Choice a random id
                random_id = random.choice(ids)

                # Get the question
                question = Question.query.get(random_id)

                return jsonify({
                  'success': True,
                  'question': question.format()
                })

        except Exception:
            abort(422)

    '''
    Handlers for all expected errors
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        print(error)
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
