# -*- coding: utf-8 -*-
from __future__ import with_statement

import flask

import flask_babel as babel
from flask_babel import gettext, lazy_gettext, lazy_ngettext, ngettext
from flask_babel._compat import text_type


def test_basics():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale='de_DE')

    with app.test_request_context():
        assert gettext(u'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
        assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 3) == \
            u'3 Äpfel'
        assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 1) == \
            u'1 Apfel'


def test_template_basics():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale='de_DE')

    t = lambda x: flask.render_template_string('{{ %s }}' % x)

    with app.test_request_context():
        assert t("gettext('Hello %(name)s!', name='Peter')") == \
            u'Hallo Peter!'
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == \
            u'3 Äpfel'
        assert t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == \
            u'1 Apfel'
        assert flask.render_template_string('''
            {% trans %}Hello {{ name }}!{% endtrans %}
        ''', name='Peter').strip() == 'Hallo Peter!'
        assert flask.render_template_string('''
            {% trans num=3 %}{{ num }} Apple
            {%- pluralize %}{{ num }} Apples{% endtrans %}
        ''', name='Peter').strip() == u'3 Äpfel'


def test_lazy_gettext():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale='de_DE')
    yes = lazy_gettext(u'Yes')
    with app.test_request_context():
        assert text_type(yes) == 'Ja'
        assert yes.__html__() == 'Ja'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
    with app.test_request_context():
        assert text_type(yes) == 'Yes'
        assert yes.__html__() == 'Yes'


def test_lazy_ngettext():
    app = flask.Flask(__name__)
    babel.Babel(app, default_locale='de_DE')
    one_apple = lazy_ngettext(u'%(num)s Apple', u'%(num)s Apples', 1)
    with app.test_request_context():
        assert text_type(one_apple) == '1 Apfel'
        assert one_apple.__html__() == '1 Apfel'
    two_apples = lazy_ngettext(u'%(num)s Apple', u'%(num)s Apples', 2)
    with app.test_request_context():
        assert text_type(two_apples) == u'2 Äpfel'
        assert two_apples.__html__() == u'2 Äpfel'


def test_list_translations():
    app = flask.Flask(__name__)
    b = babel.Babel(app, default_locale='de_DE')
    translations = b.list_translations()
    assert len(translations) == 1
    assert str(translations[0]) == 'de'


def test_no_formatting():
    """
    Ensure we don't format strings unless a variable is passed.
    """
    app = flask.Flask(__name__)
    babel.Babel(app)

    with app.test_request_context():
        assert gettext(u'Test %s') == u'Test %s'
        assert gettext(u'Test %(name)s', name=u'test') == u'Test test'
        assert gettext(u'Test %s') % 'test' == u'Test test'
