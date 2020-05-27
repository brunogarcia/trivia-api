#!/bin/bash

# Setting the `FLASK_ENV` variable to `development`
# will detect file changes and restart the server automatically
export FLASK_APP=flaskr &&

# Setting the `FLASK_APP` variable to `flaskr` 
# directs flask to use the `flaskr` directory
# and the `__init__.py` file to find the application
export FLASK_ENV=development  &&

# Run the flask app
flask run