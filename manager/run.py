from manager import app
from manager import db

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)

