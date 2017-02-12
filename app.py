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


def strip_redirects(page_url):
    ''' strip out any redirects (adverts/analytics/etc) and get final link url '''

    t = page_url.lower().replace('%3a', ':').replace('%2f', '/')
    i = t.rfind('http')
    if (i > 0):
        t = t[i:]
        j = t.find('&')
        if (j > 0):
            t = t[:j]
    return t


def build_link_url(page_url, page_theme, page_links):
    u = strip_redirects(page_url)

    if any(x in page_url for x in DO_NOT_REDIRECT) or \
       page_links == 'original':
        link = u
    else:
        params = {'url': u}
        # build optional parameter list
        if page_theme: params['theme'] = page_theme
        if page_links: params['links'] = page_links

        link = urljoin(request.url_root,
                       url_for('main', **params))

    return 'href="{0}"'.format(link)


def build_img_url(img_url):
    '''
    take first image if srcset specified (Mercury screws it up)
    e.g. <img src="http://... .jpg%201024w,%20http://...
    '''

    t = img_url
    i = img_url.find(',')
    if (i > 0):
        t = t[:i]
        j = t.rfind('%')
        if (j > 0):
            t = t[:j]

    return 'img src="{0}"'.format(t)


def update_links(content, page_theme, page_links):
    ''' update image and outgoing links to pass through this site '''

    h = re.sub('href="(\S+)"',
                  lambda m: build_link_url(m.group(1), page_theme, page_links),
                  content)
    i = re.sub('img src="(\S+)"',
                  lambda m: build_img_url(m.group(1)),
                  h)
    return i


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
                    page_content = update_links(data.content,
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
