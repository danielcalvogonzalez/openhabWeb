from flask_bootstrap import Bootstrap

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',404)

bootstrap = Bootstrap(app)

