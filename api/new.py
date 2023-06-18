import json
from flask import Flask, Response, stream_with_context
import time
app = Flask(__name__)

@app.route('/json_stream')
def json_stream():
    def generate_json():
        data = [{"id": i, "value": f"Item {i + 1}"} for i in range(10)]
        for item in data:
            yield json.dumps(item) + "\n"

    return Response(stream_with_context(generate_json()), content_type='application/json')

if __name__ == '__main__':
    app.run(debug=True)
