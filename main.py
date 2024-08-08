from api import ApiData
from database import Database
from reporting import Report

if __name__ == "__main__":

    # Extraction and Transformation layer

    api = ApiData()
    print(api.USERS_JSON[0])
    print(api.COMMENTS_JSON[0])
    print(api.POSTS_JSON[0])

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


