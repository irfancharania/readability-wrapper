from flask import Flask, request, render_template, send_from_directory, url_for, redirect
from mercury_parser import ParserAPI
from urllib.parse import urljoin
import validators
import urllib.request
import urllib.parse
import urllib.error
import os
import sys
import re
import bleach
from bs4 import BeautifulSoup
from config import AMP_PREFIX, MERCURY_API_KEY, DO_NOT_REDIRECT, FALLBACK_REDIRECT_URL

# initialization
app = Flask(__name__)
app.config.update(DEBUG=False)


# functions
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_remote_data(url):
    ''' fetch website data '''

    mercury = ParserAPI(api_key=MERCURY_API_KEY)
    return mercury.parse(url)


def strip_invalid_html(content):
    ''' strips invalid tags/attributes '''

    allowed_tags = ['a', 'abbr', 'acronym', 'address', 'b', 'br',
                    'div', 'dl', 'dt', 'em', 'h1',
                    'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img',
                    'li', 'ol', 'p', 'pre', 'q', 's', 'small',
                    'strike', 'strong', 'span', 'sub', 'sup', 'table', 'tbody',
                    'td', 'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul'
                    ]

    allowed_attrs = {
        'a': ['href', 'target', 'title'],
        'img': ['src', 'srcset', 'alt', 'width', 'height'],
    }

    cleaned = bleach.clean(content,
                           tags=allowed_tags,
                           attributes=allowed_attrs,
                           strip=True)

    return cleaned


def clean_input_url(paramUrl):
    ''' strip junk from user submitted url before fetching '''

    return strip_tracking_suffix(
                urllib.parse.unquote(paramUrl)
                .strip().strip("/")
                .replace(' ', '%20')
                .replace(AMP_PREFIX, '')
                )


def strip_redirects(page_url):
    ''' strip out any redirects (adverts/analytics/etc) and get final link url '''

    t = page_url.replace('%3A', ':').replace('%2F', '/')
    i = t.lower().rfind('http')
    if (i > 0):
        # ignore urls that have "http" in slugs (blog title, etc)
        if (t[i-1] == '=' or t[i-1] != '-'):
            t = t[i:]
            j = t.find('&')
            if (j > 0):
                t = t[:j]
    return t


def build_link_url(request_base_url, page_url,
                   page_theme=None, page_links=None):

    # fix relative to absolute
    absolute = urljoin(request_base_url, page_url)
    # strip redirects
    u = strip_redirects(absolute)

    if any(x in page_url for x in DO_NOT_REDIRECT) or page_links == 'original':
        link = u
    else:
        params = {'url': u}
        # build optional parameter list
        if page_theme:
            params['theme'] = page_theme
        if page_links:
            params['links'] = page_links

        link = urljoin(request.url_root,
                       url_for('main', **params))

    return link


def build_img_url(request_base_url, img_url):
    '''
    take first image if srcset specified (Mercury screws it up)
    e.g. <img src="http://... .jpg%201024w,%20http://...
    '''

    t = img_url

    # account for munged srcset and
    # discount space in single image path
    if ',%20' in t:
        i = img_url.find('%20')
        if (i > 0):
            t = t[:i]

    # fix relative to absolute
    absolute = urljoin(request_base_url, t)

    return absolute


def remove_unnecessary_elements(soup):
    ''' removing unnecessary html and body tags '''
    soup.html.unwrap()
    soup.body.unwrap()

    return soup


def update_links(request_base_url, content, page_theme=None, page_links=None):
    ''' update image and outgoing links to pass through this site '''

    clean_html = strip_invalid_html(content)
    extract = BeautifulSoup(clean_html, 'lxml')
    soup = remove_unnecessary_elements(extract)

    for h in soup.findAll('a', href=True):
        h['href'] = build_link_url(request_base_url, h['href'],
                                   page_theme, page_links)

    ''' removing srcset=True filter to catch lxml screwups '''
    for i in soup.findAll('img', src=True):
        i['src'] = build_img_url(request_base_url, i['src'])

    return soup.prettify(formatter="html").strip()


def get_lead_image(data):
    ''' show lead image if not repeated in content '''

    if data.lead_image_url:
        filename = data.lead_image_url[data.lead_image_url.rfind('/')+1:]

        if filename not in data.content:
            return data.lead_image_url

    return None


def strip_tracking_suffix(url):
    ''' remove advert/campaign tracking url parameters '''

    pattern = r'\/\?_?.*&\w*=.*'
    match = re.search(pattern, url)

    if match:
        return url[:match.start()]
    else:
        return url


def base_url(url, with_path=False):
    parsed = urllib.parse.urlparse(url)
    path = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
    parsed = parsed._replace(path=path)
    parsed = parsed._replace(params='')
    parsed = parsed._replace(query='')
    parsed = parsed._replace(fragment='')
    return parsed.geturl()


# controllers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'ico/favicon.ico')


@app.route("/")
def main():
    # variables
    host_url = request.url_root
    page_url = ""
    page_title = ""
    page_content = ""
    lead_img_url = ""
    date_published = ""
    page_theme = ""
    page_links = ""

    # parse query string parameters
    paramTheme = request.args.get('theme')
    if paramTheme and paramTheme.lower() == 'dark':
        page_theme = 'dark'

    paramLinks = request.args.get('links')
    if paramLinks and paramLinks.lower() == 'original':
        page_links = 'original'

    paramUrl = request.args.get('url')

    if paramUrl:
        url = clean_input_url(paramUrl)

        if validators.url(url):
            # get page content
            try:
                data = get_remote_data(url)

                if data.url:
                    request_base_url = base_url(url)
                    page_title = data.title
                    lead_img_url = get_lead_image(data)
                    page_content = update_links(request_base_url,
                                                data.content,
                                                page_theme,
                                                page_links)
                    page_url = url
                    date_published = data.date_published
                else:
                    eprint("Parser unavailable: ", url, data)
                    return redirect(FALLBACK_REDIRECT_URL + url)
            except:
                eprint("Unexpected Error: ", sys.exc_info()[0])
                return redirect(FALLBACK_REDIRECT_URL + url)
                # raise

        else:
            page_title = 'Invalid URL'
            page_content = 'Check URL and try again.'

    else:
        page_title = 'Enter URL to get started'
        page_content = 'No content provided'

    return render_template('index.html',
                           title=page_title,
                           lead_img_url=lead_img_url,
                           content=page_content,
                           url=page_url,
                           theme=page_theme,
                           links=page_links,
                           host=host_url,
                           date_published=date_published)


# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
