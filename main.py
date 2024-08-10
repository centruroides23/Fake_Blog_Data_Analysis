import api
from api import ApiData
from validation import DataValidation
from database import Database
from reporting import Report

if __name__ == "__main__":

    # Extraction layer
    api = ApiData()

    # Validation Layer
    validation = DataValidation()
    for record in api.USERS_JSON:
        validation.perform_validation(data=record, schema="users")

    for record in api.POSTS_JSON:
        validation.perform_validation(data=record, schema="posts")

    for record in api.COMMENTS_JSON:
        validation.perform_validation(data=record, schema="comments")

    # Load and Query Layer
    db = Database('social_media.db')
    db.add_data(api.USERS_JSON, source="users")
    db.add_data(api.COMMENTS_JSON, source="comments")
    db.add_data(api.POSTS_JSON, source="posts")
    db.export_to_csv()
    db.close()

    # Reporting Layer
    report = Report()
    report.generate_user_activity_report()
    report.generate_activity_statistics()
    report.generate_time_report()


