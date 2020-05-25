from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


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
        Endpoint for handle GET requests for all available categories.
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

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

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

    return app
