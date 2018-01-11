import json, time, os
from glob import glob
from flask import Flask, render_template, request


"""
This is a simple web application to visualize the progress of trained
models for efpm.

Simply run python api.py from your terminal to start the server on the port
9000.
"""

app = Flask(__name__)
subscriptions = []


@app.route('/health/', methods=['GET'])
def health():
    return '200 OK'


@app.route('/', methods=['GET'])
def home():
    id = request.args.get('id')
    files = sorted([y for x in os.walk("./data") for y in glob(os.path.join(x[0], '*.json'))], reverse=True)
    index_of_ids = [i for i in range(len(files)) if str(id) in files[i] ]
    index_of_id = index_of_ids[0] if len(index_of_ids) > 0 else 0
    models = list(map(lambda filename: json.load(open(filename)), files))
    return render_template('base.html', models=models, active_model=models[index_of_id])



class ServerSentEvent(object):
    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)


@app.route("/publish/model/", methods=["POST"])
def publish_model():
    payload = request.form.get('data')
    data = json.loads(payload)

    key = str(time.time())
    app.current_model = key

    with open("data/model-" + key + ".json", "w") as f:
        json.dump(data, f, indent=4)

    return "OK"

@app.route("/publish/train/begin/", methods=["POST"])
def publish_train_begin():
    return "OK"

@app.route("/publish/train/end/", methods=["POST"])
def publish_train_end():
    return "OK"

@app.route("/publish/epoch/end/", methods=['POST'])
def publish_epoch_end():
    payload = request.form.get('data')
    data = json.loads(payload)
    key = app.current_model
    filename = "data/model-"+key+".json"
    with open(filename,"r") as f:
        model = json.load(f)

    model["id"] = key
    with open(filename, "w") as f:
        if model["training"].get("history"):
            model["training"].get("history").append(data)
        else:
            model["training"]["history"] = [data]
        json.dump(model, f, indent=4)
    return "OK"


def to_pretty_json(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['tojson_pretty'] = to_pretty_json

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = True
    app.run(port=9000,extra_files=['./templates/base.html'])