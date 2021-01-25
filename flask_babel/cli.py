import os
import click


def register_cli(app):
    translate_dir = os.path.join(app.root_path, "translations")
    cfg = "babel.cfg"

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if not os.path.exists(cfg):
            with open(cfg, "w+") as f:
                f.write(
                    "[python: **.py]"
                )
        if os.system('pybabel extract -F -k _l -o messages.pot .'.format(cfg)):
            raise RuntimeError('extract command failed')

        if os.system(
                'pybabel init -i messages.pot -d {} -l '.format(translate_dir) + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F -k _l -o messages.pot .'.format(cfg)):
            raise RuntimeError('extract command failed')

        if os.system('pybabel update -i messages.pot -d {}'.format(translate_dir)):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d {}'.format(translate_dir)):
            raise RuntimeError('compile command failed')
