import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    if post is None:
     app.logger.error(f'Article with id {post_id} Not found')
    else:
     app.logger.info(f'Article {post["title"]} Retrieved!')
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info(f'Index page retrieved with post count of {len(posts)}')
    return render_template('index.html', posts=posts)

 # Define the healthz endpoint
@app.route('/healthz')
def healthcheck():
    health_response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Health check endpoint invoked ')
    return health_response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post = connection.execute('SELECT count(*) FROM posts').fetchone()
    connection.close()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": 1, "post_count": post[0]}}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics endpoint invoked ')
    return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error(f'A non-existing article with id {post_id} is accessed and a 404 page is returned')
      return render_template('404.html'), 404
    else:
      app.logger.info(f'post {post_id} and {post["title"]} retrieved')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The "About Us" page is retrieved')
    return render_template('about.html')



# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            app.logger.error('Creation of article is failed due to missing title ')
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'A new article is created, with title {title} and content {content} Successfully created ')
            return redirect(url_for('index'))

    app.logger.info('Creation endpoint retrieved for GET')
    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   ## stream logs to a file
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
