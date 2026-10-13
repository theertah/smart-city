
from flask import Flask, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from database.db import db, init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    init_db(app)

    # Import routes
    from routes.traffic import bp as traffic_bp
    from routes.environment import bp as environment_bp
    from routes.waste import bp as waste_bp
    from routes.complaints import bp as complaints_bp
    from routes.predictions import bp as predictions_bp
    from routes.assistant import bp as assistant_bp
    from routes.weather import bp as weather_bp

    # Register routes
    blueprints = (
        traffic_bp,
        environment_bp,
        waste_bp,
        complaints_bp,
        predictions_bp,
        assistant_bp,
        weather_bp,
    )

    for bp in blueprints:
        app.register_blueprint(bp)

    # Main pages
    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/admin")
    def index():
        return render_template("index.html")

    @app.route("/citizen")
    def citizen():
        return render_template("citizen.html")

    # Start the city simulator
    _start_simulator(app)

    return app


def _start_simulator(app):
    from simulator.city_data import generate_tick

    # Generate initial data before starting the scheduler
    with app.app_context():
        for _ in range(15):
            try:
                generate_tick()
            except Exception:
                db.session.rollback()
                app.logger.exception("Initial simulator data generation failed")
                break
            finally:
                db.session.remove()

    def tick():
        with app.app_context():
            try:
                generate_tick()
            except Exception:
                db.session.rollback()
                app.logger.exception("City simulator tick failed")
            finally:
                db.session.remove()

    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        tick,
        trigger="interval",
        seconds=app.config["SIMULATOR_INTERVAL_SECONDS"],
        id="city_simulator",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    scheduler.start()


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        port=5000,
    )
