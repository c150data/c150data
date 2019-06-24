from app import app

if __name__ == "__main__":
    app.run(host="localhost", ssl_context='adhoc', debug=True) # TODO fix SSL

