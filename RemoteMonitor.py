import requests
import warnings
import json
import os
from keras import callbacks
from keras_diagram import ascii


class RemoteMonitor(callbacks.Callback):
    """Callback used to stream events to a server.

    Requires the `requests` library.

    Events:

        Model Params
        Train Start:
        Train End
        Epoch End
        Epoch Start

    Epoch end events are sent to `root + '/publish/epoch/end/'` by default. Calls are
    HTTP POST, with a `data` argument which is a JSON-encoded dictionary of event data.

    # Arguments
        root: String; root url of the target server.
        path: String; path relative to `root` to which the events will be sent.
        field: String; JSON field under which the data will be stored.
        headers: Dictionary; optional custom HTTP headers.
    """

    def __init__(self,
                 root='http://localhost:9000',
                 path='/publish/',
                 field='data',
                 headers=None):
        super(RemoteMonitor, self).__init__()

        self.root = root
        self.path = path
        self.field = field
        self.headers = headers

        if requests is None:
            raise ImportError('RemoteMonitor requires '
                              'the `requests` library.')

    def send(self, data, path):

        try:
            requests.post(self.root + self.path + path,
                          {self.field: json.dumps(data)},
                          headers=self.headers)

        except requests.exceptions.RequestException:
            warnings.warn('Warning: could not reach RemoteMonitor '
                          'root server at ' + str(self.root))


    def on_epoch_end(self, epoch, logs=None):

        logs = logs or {}
        send = {}
        send['epoch'] = epoch
        for k, v in logs.items():
            send[k] = v

        self.send(send, "epoch/end/")


    def on_train_begin(self, logs=None):
        self.send(logs or {}, "train/begin/")


    def on_train_end(self, logs=None):
        self.send(logs or {}, "train/end/")


    def set_model(self, model):

        with open('tmp_report.txt', 'w') as fh:
            model.summary(print_fn=lambda x: fh.write(x + '\n'))
        with open('tmp_report.txt', 'r') as f:
            summary = f.read()
        os.remove('tmp_report.txt')

        self.send({"architecture":json.loads(model.to_json()),
                   "training": {
                       "optimizer":{**model.optimizer.get_config(), **{"name":model.optimizer.__class__.__name__.lower()}}
                   },
                   "ascii": ascii(model),
                   "summary": summary},
                  "model/")
