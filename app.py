import datetime
import os

from celery import Celery
from flask import Flask
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage

import utils

UPLOAD_FOLDER = "./uploaded-files"
ALLOWED_EXTENSIONS = {"csv"}


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reverse_geo_coding.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CELERY_broker_url"] = "redis://localhost:6379/0"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

celery_app = Celery(
    app.name,
    broker=app.config["CELERY_broker_url"],
    task_ignore_result=True
)
celery_app.conf.update(app.config)


api = Api(
    app=app,
    description="The service is calculate distance between several "
    "locations ( points ) giving human-readable addresses "
    "for each point.",
)
api_ns = api.namespace(
    "api",
)


upload_parser = api.parser()
upload_parser.add_argument("file", location="files", type=FileStorage, required=True)


class Tasks(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    status = db.Column(db.String(10))


@celery_app.task
def find_addresses_and_distances(**kwargs):
    with app.app_context():
        file_path = kwargs["file_path"]
        current_task_id = find_addresses_and_distances.request.id

        new_task = Tasks(id=current_task_id, status="running")
        db.session.add(new_task)
        db.session.commit()

        points = utils.read_csv(file_path)

        utils.find_addresses(points)
        utils.calculate_distances(points)

        new_task.status = "done"
        db.session.add(new_task)
        db.session.commit()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_filename():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    filename = f"geo-points-{formatted_datetime}.txt"

    return filename


@api_ns.route("/calculateDistances/")
@api.expect(upload_parser)
class CreateJob(Resource):
    def post(self):
        args = upload_parser.parse_args()
        uploaded_file = args["file"]

        if uploaded_file and allowed_file(uploaded_file.filename):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], generate_filename())

            uploaded_file.save(file_path)

            result = find_addresses_and_distances.apply_async(
                kwargs={"file_path": file_path}
            )

            return {"task_id": result.id, "status": "running"}, 200
        return {"message": "Invalid file format. Please upload a CSV file."}, 400


@api_ns.route("/getResult/<uuid:task_id>")
class JobResult(Resource):
    def get(self, task_id):
        response = {"task_id": str(task_id), "status": None,  "data": []}

        result = Tasks.query.get_or_404(str(task_id))

        if result.status == "done":
            response["status"] = "done"
            response["data"] = {
                "points": [
                    {"name": "A", "address": "Some address..."},
                    {"name": "B", "address": "Some address..."},
                    {"name": "C", "address": "Some address..."},
                ],
                "links": [
                    {"name": "AB", "distance": 350.6},
                    {"name": "BC", "distance": 125.8},
                    {"name": "AC", "distance": 1024.9},
                ],
            }  # TODO
            return response

        response["status"] = result.status
        return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
