import logging

from flask import request, jsonify;

from conduit import app;

logger = logging.getLogger(__name__)

@app.route('/test', methods=['GET'])
# @app.route('/square', methods=['POST'])
def test_api():
    # data = request.get_json();
    # logging.info("data sent for evaluation {}".format(data))
    # inputValue = data.get("input");
    # result = inputValue * inputValue
    # logging.info("My result :{}".format(result))
    # return jsonify(result);
    return "hello world"
