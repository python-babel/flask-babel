import flask
import pytest
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo

import flask_babel as babel


@pytest.mark.parametrize("same_domain", [False, True])
@pytest.mark.parametrize("reverse_requests", [False, True])
def test_shared_babel_keeps_application_catalogs_separate(
    tmp_path, mocker, same_domain, reverse_requests
):
    extension = babel.Babel()
    apps = []
    for index in range(2):
        domain = "messages" if same_domain else "domain%d" % index
        directory = tmp_path / str(index) / "de" / "LC_MESSAGES"
        directory.mkdir(parents=True)
        catalog = Catalog(locale="de")
        catalog.add("Hello", "App %d" % index)
        catalog.add(("one item", "many items"), ("one %d" % index, "many %d" % index))
        with (directory / (domain + ".mo")).open("wb") as output:
            write_mo(output, catalog)
        app = flask.Flask(__name__)
        extension.init_app(
            app,
            default_locale="de",
            default_domain=domain,
            default_translation_directories=str(tmp_path / str(index)),
        )

        @app.route("/")
        def index_page():
            return (
                flask.render_template_string("{{ _('Hello') }}")
                + " / "
                + babel.ngettext("one item", "many items", 2)
            )

        apps.append(app)

    load = mocker.patch(
        "babel.support.Translations.load", wraps=babel.support.Translations.load
    )
    order = [1, 0] if reverse_requests else [0, 1]
    domains = {}
    for index in order + order:
        assert apps[index].test_client().get("/").get_data(
            as_text=True
        ) == "App %d / many %d" % (index, index)
        with apps[index].app_context():
            current = extension.domain_instance
            if index in domains:
                assert current is domains[index]
            domains[index] = current
    assert domains[0] is not domains[1]
    assert load.call_count == 2

    with apps[0].app_context():
        assert babel.gettext("Hello") == "App 0"
        with apps[1].app_context():
            assert babel.gettext("Hello") == "App 1"
        assert babel.gettext("Hello") == "App 0"


def test_reinitializing_app_does_not_reuse_previous_domain():
    app = flask.Flask(__name__)
    extension = babel.Babel(app, default_domain="first")
    with app.app_context():
        original = extension.domain_instance
        assert original.domain == ["first"]
    extension.init_app(app, default_domain="second")
    with app.app_context():
        assert extension.domain_instance is not original
        assert extension.domain_instance.domain == ["second"]
        custom = babel.Domain(domain="custom")
        custom.as_default()
        assert babel.get_domain() is custom
    with app.app_context():
        assert babel.get_domain() is extension.domain_instance
