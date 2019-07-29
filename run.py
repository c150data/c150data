from app import app
import logging

if __name__ == "__main__":
    app.run(host="localhost", ssl_context='adhoc', debug=True)