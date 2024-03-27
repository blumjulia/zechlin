import os
from flask import Flask

def create_app(test_config=None) -> Flask:
    """
    Erstellung und Konfiguration der Flask-Applikation

    :param test_config: Optionale Konfiguration zum Konfigurieren der Applikation
    :return: Flask Applikation
    """

    # Initiieren einer neuen Instanz von Flask
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # Wenn keine Testkonfiguration vorhanden, dann Standard-Konfigurationsdatei verwenden
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Bei Angabe einer Testdatei: Testdatei laden
        app.config.from_mapping(test_config)

    # Deaktiviert das Sortieren von JSON Keys, dadurch kann eine eigene Sortierung angewendet werden
    app.json.sort_keys = False

    app.config.from_mapping(
        SECRET_KEY='zechlin_session_key',
    )

    # Erstellt den Instanz-Ordner
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Funktionen um Interaktionen mit der MariaDB Datenbank durchzuführen
    from . import datenbank

    from . import auth
    app.register_blueprint(auth.bp)

    # Hauptseiten der Webseite
    # /
    # /pid/<pid>
    from . import index
    app.register_blueprint(index.bp)
    app.add_url_rule('/', endpoint='index')

    # Suchalgorithmen sowie Ergebnis-Seiten
    # /ergebnis/schnellsuche
    # /ergebnis/werksuche
    # /ergebnis/nutzungssuche
    from . import suche
    app.register_blueprint(suche.bp)
    app.add_url_rule('/', endpoint='suche')

    # Werk-bezogene Seiten
    # /werk/<id>
    # /werk/verzeichnis
    from . import werk
    app.register_blueprint(werk.bp)
    app.add_url_rule('/', endpoint='werk')

    # Nutzung-bezogene Seiten
    # /nutzung/<id>
    # /nutzung/verzeichnis
    from . import nutzung
    app.register_blueprint(nutzung.bp)
    app.add_url_rule('/', endpoint='nutzung')

    # Seiten für weitere Entitäten neben Werk/Nutzung (Gattung, Untergattung, usw)
    # /gattung/<id>
    # /untergattung/<id>
    # /detailgattung/<id>
    # /ort/<id>
    from . import objekt
    app.register_blueprint(objekt.bp)
    app.add_url_rule('/', endpoint='objekt')

    # Datenauswertung in Form von Visualisierungen/Diagrammen
    # /auswertung/nutzung/karte
    from . import auswertung
    app.register_blueprint(auswertung.bp)
    app.add_url_rule('/', endpoint='auswertung')

    # Dokumentation des Projektes sowie der Datenbank
    # /dokumentation/datenbank
    # /dokumentation/werk
    # /dokumentation/gattung
    # /dokumentation/untergattung
    # /dokumentation/detailgattung
    # /dokumentation/verlag
    # /dokumentation/werkart
    # /dokumentation/ausgabe
    # /dokumentation/rism
    # /dokumentation/rism-kategorie
    # /dokumentation/ort
    # /dokumentation/nutzung
    # /dokumentation/nutzung-quelle
    from . import dokumentation
    app.register_blueprint(dokumentation.bp)

    # Export der Daten
    # /export/json-ld/werk/<id>
    # /export/json-ld/nutzung/<id>
    # /export/json-ld/ort/<id>
    from . import export
    app.register_blueprint(export.bp)
    app.add_url_rule('/', endpoint='export')

    return app


# Initiieren der Applikation zechlin
if __name__ == '__main__':
    zechlin = create_app()
    zechlin.run()
