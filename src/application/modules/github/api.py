import json
import datetime
import flask
from flask import request, Response

from google.appengine.ext import ndb
from github import Github

from application import app
from models import IssueSnapshot, GithubSnapshot
import tasks

def all():
    org = requests.args.get("org")
    if not org or len(org) == 0:
        return flask.jsonify({
                "type": "Error",
                "body": "Bad org name"
            })
    qry = GithubSnapshot.query(GithubSnapshot.github_org_name == org).order(-GithubSnapshot.requested_time)
    results = qry.fetch()

    result = {}
    requested_time = datetime.datetime.now()
    result["currentSnapshot"] = tasks.take_snapshot(org, requested_time, save=False)
    result["snapshots"] = [r.as_dict() for r in results]

    return Response(json.dumps(result), mimetype="text/json")

def snapshots():
    qry = GithubSnapshot.query().order(-GithubSnapshot.requested_time)
    results = qry.fetch()

    return Response(json.dumps([r.as_dict() for r in results]), mimetype="text/json")

def take_snapshot():
    org = request.args.get("org")
    if not org or len(org) == 0:
        return flask.jsonify({
                "type": "Error",
                "body": "Bad org name"
            })
    requested_time = datetime.datetime.now()

    result = tasks.take_snapshot(org, requested_time)
    return Response(json.dumps(result.as_dict()), mimetype="text/json")