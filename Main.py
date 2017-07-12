from __future__ import print_function
from __future__ import print_function

import json
import Attendance
import time
import Export
import Admin
import Github
import github
import ids

NO_CACHE = 0
SHORT_CACHE = 2*60*60
MEDIUM_CACHE = 24*60*60
LONG_CACHE = 30*24*60*60


def main(event, context):
    print(event, context)

    if is_auto_manage_event(event):
        manage_attendance()
        response = {"status": "OK"}
        cache_length = NO_CACHE
    elif event is None or "resource" not in event:
        response = {"message": "No resource specified", "status": "ERROR"}
        cache_length = NO_CACHE
    elif event["resource"] == "/sign-in":
        response = sign_in(event, context)
        cache_length = NO_CACHE
    elif event["resource"] == "/post-announcement":
        response = sign_in(event, context)
        cache_length = NO_CACHE
    elif event["resource"] == "/github-sign-up":
        response = github_sign_up(event, context)
        cache_length = NO_CACHE
    else:
        response = {"status": "ERROR"}
        cache_length = NO_CACHE

    print("RETURNING", response)

    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {"Cache-Control": "public,max-age=" + str(cache_length) + ",only-if-cached,max-stale"},
        "body": json.dumps(response)
    }


def is_auto_manage_event(event):
    if "detail-type" in event and event["detail-type"] == "Scheduled Event":
        if ids.aws_cloudwatch_id in event['resources'][0]:
            return True
    return False


def sign_in(event, context):
    params = event["queryStringParameters"]
    response_code = Attendance.sign_in(uid=params["uid"], name=params["name"], email=params["email"])

    return {"status": "OK", "response_code": response_code}


def github_sign_up(event, context):
    params = event["queryStringParameters"]

    try:
        response_code = Github.add_username_to_members(params["username"])
        return {"message": "You have been added to the Github organization. Welcome to ACM!", "status": "OK",
                "github_response": response_code}
    except github.GithubException as e:
        return {"message": "Oh no! Something went wrong.", "status": "ERROR", "github_response": str(e)}


def manage_attendance():
    day_of_week = time.strftime("%A").lower()
    meeting_key = time.strftime("%B_%d").lower()

    print(day_of_week, meeting_key)

    if day_of_week == "friday":
        print("friday")
        Admin.set_current_meeting(meeting_key)
        Admin.enable_attendance()
    else:
        print("otherday")
        if Admin.is_attendance_enabled():
            Export.export_attendance()
        Admin.disable_attendance()