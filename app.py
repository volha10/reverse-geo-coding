from flask import Flask
from flask_restx import Api, Resource

app = Flask(__name__)
api = Api(
    app=app,
    description="The service is calculate distance between several "
    "locations ( points ) giving human-readable addresses "
    "for each point.",
)
api_ns = api.namespace(
    "api",
)


@api_ns.route("/getList/<int:task_id>")
class JobResult(Resource):
    def get(self, task_id):
        pass


@api_ns.route("/calculateDistances/")
class CreateJob(Resource):
    def post(self):
        pass


if __name__ == "__main__":
    app.run(debug=True)
