import os
from flask import Flask, request, render_template, send_from_directory
import validators
import urllib
from mercury_parser import ParserAPI
from config import MERCURY_API_KEY

# initialization
app = Flask(__name__)
app.config.update(DEBUG=True)


# functions
def get_remote_data(url):
    ''' fetch website data '''
    mercury = ParserAPI(api_key=MERCURY_API_KEY)
    return mercury.parse(url)


# controllers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico')


@app.route("/")
def main():
    # variables
    page_url = ""
    page_theme = ""

    # main
    paramTheme = request.args.get('theme')
    if paramTheme:
        page_theme = "dark" if paramTheme.lower() == "dark" else ""

    paramUrl = request.args.get('url')
    if paramUrl:
        url = urllib.unquote(paramUrl).strip()
        if validators.url(url):
            # get posts
            data = get_remote_data(url)
            page_title = data.title
            page_content = data.content
            page_url = data.url

        else:
            page_title = "Invalid URL"
            page_content = "Invalid URL. Try again."

    else:
        page_title = "Home"
        page_content = "Enter URL to get started"

    return render_template('index.html',
                           title=page_title,
                           content=page_content,
                           url=page_url,
                           theme=page_theme)


# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
