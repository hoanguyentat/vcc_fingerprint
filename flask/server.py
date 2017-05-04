from flask_failsafe import failsafe

def create_app():
    from uniquemachine_app import app
    return app

if __name__ == "__main__":
    create_app().run(threaded=True, host = '0.0.0.0')

