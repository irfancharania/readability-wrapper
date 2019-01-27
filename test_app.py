import app

''' Run 'pytest' to run all '''

def test_strip_email_campaign():
    given = 'https://dotnetthoughts.net/background-tasks-in-asp-net-core/?utm_campaign=ASP.NET%20Weekly&utm_medium=email&utm_source=Revue%20newsletter'
    expected = 'https://dotnetthoughts.net/background-tasks-in-asp-net-core'

    result = app.clean_input_url(given)

    assert result == expected


def test_ignore_post_id():
    given = 'https://cocowest.ca/?p=39181'
    expected = 'https://cocowest.ca/?p=39181'

    result = app.clean_input_url(given)

    assert result == expected


def test_ignore_post_id_with_file():
    given = 'https://queue.acm.org/detail.cfm?id=3184136'
    expected = 'https://queue.acm.org/detail.cfm?id=3184136'

    result = app.clean_input_url(given)

    assert result == expected


def test_strip_referral_redirect():
    given = 'http://www.amazon.ca/gp/redirect.html?ie=UTF8&location=https%3A%2F%2Fwww.amazon.ca%2FSTEINS-GATE-ELITE-Limited-Nintendo%2Fdp%2FB07BKKNRC9%2F&tag=redflagdealsc-20&linkCode=ur2&camp=15121&creative=330641'
    expected = 'https://www.amazon.ca/STEINS-GATE-ELITE-Limited-Nintendo/dp/B07BKKNRC9/'

    result = app.strip_redirects(given)

    assert result == expected


def test_http_in_link():
    given = 'https://www.newmediacampaigns.com/blog/browser-rest-http-accept-headers'
    expected = 'https://www.newmediacampaigns.com/blog/browser-rest-http-accept-headers'

    result = app.strip_redirects(given)

    assert result == expected


def test_build_link_ignore_google_link():
    given = 'https://goo.gl/maps/Pzw6XhTeLz62'
    expected = 'https://goo.gl/maps/Pzw6XhTeLz62'

    result = app.build_link_url(given)

    assert result == expected


def test_img_link():
    given = 'https://west.cocowest1.ca/2019/01/crackers2.jpg%20407w,%20https://west.cocowest1.ca/2019/01/crackers2-250x300.jpg%20250w'
    expected = 'https://west.cocowest1.ca/2019/01/crackers2.jpg'

    result = app.build_img_url(given)

    assert result == expected
