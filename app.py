from flask import Flask, request, render_template, send_from_directory, url_for, redirect
from mercury_parser import ParserAPI
from urlparse import urljoin
import validators
import urllib
import os
import re
from config import MERCURY_API_KEY, DO_NOT_REDIRECT, FALLBACK_REDIRECT_URL

# initialization
app = Flask(__name__)
app.config.update(DEBUG=True)


# functions
def get_remote_data(url):
    ''' fetch website data '''

    mercury = ParserAPI(api_key=MERCURY_API_KEY)
    return mercury.parse(url)


def build_url(page_url, page_theme, page_links):
    if any(x in page_url for x in DO_NOT_REDIRECT):
        link = page_url
    else:
        link = urljoin(request.url_root,
                       url_for('main',
                               theme=page_theme,
                               links=page_links,
                               url=page_url))
    result = 'href="{0}"'
    return result.format(link)


def change_links_to_readable(content, page_theme, page_links):
    ''' update outgoing links to pass through this site '''

    return re.sub('href="(\S+)"',
                  lambda m: build_url(m.group(1), page_theme, page_links),
                  content)


# controllers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico')


@app.route("/")
def main():
    # variables
    page_url = ""

    # parse query string parameters
    paramTheme = request.args.get('theme')
    page_theme = 'dark' if paramTheme and paramTheme.lower() == 'dark' else ''

    paramLinks = request.args.get('links')
    page_links = 'original' if paramLinks and paramLinks.lower() == 'original' else ''

    paramUrl = request.args.get('url')

    if paramUrl:
        url = urllib.unquote(paramUrl).strip()

        if validators.url(url):
            # get page content
            try:
                data = get_remote_data(url)
                if data.url:
                    page_title = data.title
                    page_content = data.content if page_links == 'original' \
                        else change_links_to_readable(data.content,
                                                      page_theme, page_links)
                    page_url = data.url
                else:
                    # parser is unavailable
                    return redirect(FALLBACK_REDIRECT_URL + url)
            except:
                return redirect(FALLBACK_REDIRECT_URL + url)

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
                           theme=page_theme,
                           links=page_links)


# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
