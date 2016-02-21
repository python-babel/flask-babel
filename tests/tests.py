# -*- coding: utf-8 -*-
from __future__ import with_statement

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from decimal import Decimal
import flask
from datetime import datetime
from flask_icu import *
# from flask_babel import gettext, ngettext, lazy_gettext
from flask_icu._compat import text_type


class DateFormattingTestCase(unittest.TestCase):

    def test_basics(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
            assert format_date(d) == 'Apr 12, 2010'
            assert format_time(d) == '1:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            assert format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
            assert format_date(d) == 'Apr 12, 2010'
            assert format_time(d) == '3:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'de_DE'
            assert format_datetime(d, 'long') == \
                '12. April 2010 15:46:00 MESZ'

    def test_basics_with_none_for_defaults(self):
        app = flask.Flask(__name__)
        icu = ICU(app, None, None)
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'


    def test_init_app(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        icu.init_app(app)
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
            assert format_date(d) == 'Apr 12, 2010'
            assert format_time(d) == '1:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            assert format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'
            assert format_date(d) == 'Apr 12, 2010'
            assert format_time(d) == '3:46:00 PM'

        with app.test_request_context():
            app.config['ICU_DEFAULT_LOCALE'] = 'de_DE'
            assert format_datetime(d, 'long') == \
                '12. April 2010 15:46:00 MESZ'

    def test_custom_formats(self):
        app = flask.Flask(__name__)
        app.config.update(
            ICU_DEFAULT_LOCALE='en_US',
            ICU_DEFAULT_TIMEZONE='Pacific/Johnston'
        )
        icu = ICU(app)
        icu.date_formats['datetime'] = 'long'
        icu.date_formats['datetime.long'] = 'MMMM d, yyyy h:mm:ss a'
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert format_datetime(d) == 'April 12, 2010 3:46:00 AM'

    def test_custom_locale_selector(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        d = datetime(2010, 4, 12, 13, 46)

        the_timezone = 'UTC'
        the_locale = 'en_US'

        @icu.localeselector
        def select_locale():
            return the_locale
        @icu.timezoneselector
        def select_timezone():
            return the_timezone

        with app.test_request_context():
            assert format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'

        the_locale = 'de_DE'
        the_timezone = 'Europe/Vienna'

        with app.test_request_context():
            assert format_datetime(d) == '12.04.2010 15:46:00'

    def test_refreshing(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        d = datetime(2010, 4, 12, 13, 46)

        with app.test_request_context():
            assert format_datetime(d) == 'Apr 12, 2010, 1:46:00 PM'
            app.config['ICU_DEFAULT_TIMEZONE'] = 'Europe/Vienna'
            icu_refresh()
            assert format_datetime(d) == 'Apr 12, 2010, 3:46:00 PM'


class NumberFormattingTestCase(unittest.TestCase):

    def test_basics(self):
        app = flask.Flask(__name__)
        icu = ICU(app)
        n = 1099

        with app.test_request_context():
            assert format_number(n) == u'1,099'
#             assert babel.format_decimal(Decimal('1010.99')) == u'1,010.99'
#             assert babel.format_currency(n, 'USD') == '$1,099.00'
#             assert babel.format_percent(0.19) == '19%'
#             assert babel.format_scientific(10000) == u'1E4'
#
#
# class GettextTestCase(unittest.TestCase):
#
#     def test_basics(self):
#         app = flask.Flask(__name__)
#         b = babel.Babel(app, default_locale='de_DE')
#
#         with app.test_request_context():
#             assert gettext(u'Hello %(name)s!', name='Peter') == 'Hallo Peter!'
#             assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 3) == u'3 Äpfel'
#             assert ngettext(u'%(num)s Apple', u'%(num)s Apples', 1) == u'1 Apfel'
#
#     def test_template_basics(self):
#         app = flask.Flask(__name__)
#         b = babel.Babel(app, default_locale='de_DE')
#
#         t = lambda x: flask.render_template_string('{{ %s }}' % x)
#
#         with app.test_request_context():
#             assert t("gettext('Hello %(name)s!', name='Peter')") == 'Hallo Peter!'
#             assert t("ngettext('%(num)s Apple', '%(num)s Apples', 3)") == u'3 Äpfel'
#             assert t("ngettext('%(num)s Apple', '%(num)s Apples', 1)") == u'1 Apfel'
#             assert flask.render_template_string('''
#                 {% trans %}Hello {{ name }}!{% endtrans %}
#             ''', name='Peter').strip() == 'Hallo Peter!'
#             assert flask.render_template_string('''
#                 {% trans num=3 %}{{ num }} Apple
#                 {%- pluralize %}{{ num }} Apples{% endtrans %}
#             ''', name='Peter').strip() == u'3 Äpfel'
#
#     def test_lazy_gettext(self):
#         app = flask.Flask(__name__)
#         b = babel.Babel(app, default_locale='de_DE')
#         yes = lazy_gettext(u'Yes')
#         with app.test_request_context():
#             assert text_type(yes) == 'Ja'
#         app.config['BABEL_DEFAULT_LOCALE'] = 'en_US'
#         with app.test_request_context():
#             assert text_type(yes) == 'Yes'
#
#     def test_list_translations(self):
#         app = flask.Flask(__name__)
#         b = babel.Babel(app, default_locale='de_DE')
#         translations = b.list_translations()
#         assert len(translations) == 1
#         assert str(translations[0]) == 'de'


if __name__ == '__main__':
    unittest.main()
