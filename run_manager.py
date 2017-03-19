from manager import app
from manager import monitor_pool


import threading


if __name__ == '__main__':

    monitor_process = threading.Thread(target=monitor_pool.background_monitor)
    monitor_process.start()
    app.run(host='0.0.0.0', threaded=True)
