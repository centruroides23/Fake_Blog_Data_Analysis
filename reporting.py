from database import Database
from sqlalchemy import func
import pandas as pd
import plotly.graph_objects as go


class Report:
    def __init__(self):
        self.db = Database("social_media.db")
        self.models = self.db.models
        self.session = self.db.session
        self.Users, self.Posts, self.Comments = self.db.models
        self.activity_report_data = self.fetch_post_comment_counts()
        self.time_report_data = self.fetch_comment_post_times()

    def fetch_post_comment_counts(self):
        # Query the database to get count of posts and comments per user
        result = self.session.query(
            self.Users.id.label('user_id'),
            func.concat(self.Users.first_name, " ", self.Users.last_name).label("full_name"),
            func.count(self.Posts.id.distinct()).label('post_count'),
            func.count(self.Comments.id).label('comment_count')
        ).outerjoin(self.Posts, self.Users.id == self.Posts.author_id) \
            .outerjoin(self.Comments, self.Users.id == self.Comments.author_id) \
            .group_by(self.Users.id) \
            .order_by(func.count(self.Posts.id.distinct()).desc(), func.count(self.Comments.id).desc()) \
            .limit(20) \
            .all()

        # Close the session
        self.db.close()

        # Create dataframe with query result
        columns = ["user_id", "full_name", "post_count", "comment_count"]
        data = pd.DataFrame(result, columns=columns)
        return data

    def fetch_comment_post_dates(self):
        post_counts = self.session.query(
            func.strftime('%Y-%m-%d', self.Posts.created_at).label('date'),
            func.count(self.Posts.id).label('count')
        ).group_by('date').order_by('hour').all()

        # Query to count comments per hour
        comment_counts = self.session.query(
            func.strftime('%Y-%m-%d', self.Comments.created_at).label('date'),
            func.count(self.Comments.id).label('count')
        ).group_by('date').order_by('hour').all()

        results = {
            'posts': post_counts,
            'comments': comment_counts
        }

        return results

    def fetch_comment_post_times(self):
        post_counts = self.session.query(
            func.strftime('%H', self.Posts.created_at).label('hour'),
            func.count(self.Posts.id).label('count')
        ).group_by('hour').order_by('hour').all()

        # Query to count comments per hour
        comment_counts = self.session.query(
            func.strftime('%H', self.Comments.created_at).label('hour'),
            func.count(self.Comments.id).label('count')
        ).group_by('hour').order_by('hour').all()

        results = {
            'posts': post_counts,
            'comments': comment_counts
        }

        return results

    def generate_user_activity_report(self):
        # Generate a Seaborn Barchart
        fig = go.Figure(data=[
            go.Bar(name="Post Count", x=self.activity_report_data["full_name"],
                   y=self.activity_report_data["post_count"]),
            go.Bar(name="Comment Count", x=self.activity_report_data["full_name"],
                   y=self.activity_report_data["comment_count"])
        ])

        fig.update_layout(barmode="stack",
                          title="Bar Chart of Post and Comment Count per User",
                          xaxis_title="Users",
                          yaxis_title="Count")
        fig.show()

    def generate_activity_statistics(self):
        fig = go.Figure()
        fig.add_trace(go.Box(name="Comment Count", y=self.activity_report_data["comment_count"]))
        fig.add_trace(go.Box(name="Post Count", y=self.activity_report_data["post_count"]))

        fig.update_layout(
            title="Box Plot of Post and Comment Count",
            xaxis_title="Frequency",
            yaxis_title="Categories"
        )

        fig.show()

    def generate_time_report(self):
        posts_data = self.time_report_data["posts"]
        comments_data = self.time_report_data["comments"]

        # Create dataframe with comment and posts times
        columns_posts = ["time", "post_count"]
        columns_comments = ["time", "comment_count"]
        time_posts = pd.DataFrame(posts_data, columns=columns_posts)
        time_comments = pd.DataFrame(comments_data, columns=columns_comments)

        fig = go.Figure(data=[
            go.Bar(name="Post Count",
                   x=time_posts["time"],
                   y=time_posts["post_count"],
                   marker_color='rgb(26, 118, 255)'),

            go.Bar(name="Comment Count",
                   x=time_comments["time"],
                   y=time_comments["comment_count"],
                   marker_color='rgb(55, 83, 109)')
        ])

        fig.update_layout(barmode="group",
                          title="Bar Chart of Post and Comment Count per Hour",
                          xaxis_title="Hour of the Day",
                          xaxis={"categoryorder": "total descending"},
                          yaxis_title="Frequency")
        fig.show()
