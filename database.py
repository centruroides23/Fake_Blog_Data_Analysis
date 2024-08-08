import os.path
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Mapped, mapped_column
import csv
import numpy as np
import datetime as datetime
from faker import Faker


def random_integer(min_val, max_val, mean, std_dev):
    # Generate a random value from a normal distribution
    value = np.random.normal(loc=mean, scale=std_dev)
    clamped_value = max(min_val, min(max_val, round(value)))

    return clamped_value


Base = declarative_base()


# def define_tables(self):
class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    birthday: Mapped[str] = mapped_column(String(10))
    city: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(50))
    state_code: Mapped[str] = mapped_column(String(3))

    # Relationships
    posts = relationship('Posts', back_populates='author')
    comments = relationship("Comments", back_populates="author")


class Posts(Base):
    __tablename__ = 'posts'
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    likes: Mapped[int] = mapped_column(Integer)
    dislike: Mapped[int] = mapped_column(Integer)
    views: Mapped[int] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Relationship
    author = relationship('Users', back_populates='posts')
    comments = relationship("Comments", back_populates="posts")


class Comments(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    body: Mapped[str] = mapped_column(String(250), nullable=False)
    likes: Mapped[int] = mapped_column(Integer)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Relationship
    author = relationship("Users", back_populates="comments")
    posts = relationship("Posts", back_populates="comments")


class Database:
    def __init__(self, db_filename):
        self.engine = create_engine(f'sqlite:///{db_filename}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Assign classes to instance variables for later use
        self.Users = Users
        self.Posts = Posts
        self.Comments = Comments

    def add_data(self, data, source):

        # Instantiate Faker
        fake = Faker()

        # Creating new users
        if source == "users":
            Users = self.Users
            for entry in data:
                new_user = Users(
                    first_name=entry["firstName"],
                    last_name=entry["lastName"],
                    email=entry["email"],
                    birthday=entry["birthDate"],
                    city=entry["city"],
                    state=entry["state"],
                    state_code=entry["stateCode"]
                )

                self.session.add(new_user)
                self.session.commit()

        if source == "posts":
            Posts = self.Posts
            for entry in data:
                new_post = Posts(
                    created_at=fake.date_time_this_decade(),
                    title=entry["title"],
                    likes=entry["likes"],
                    dislike=entry["dislikes"],
                    views=entry["views"],
                    # author_id=entry["id"] TRY FOR DISTINCT VALUES
                    author_id=random_integer(0, 150, 75, 2)
                )

                self.session.add(new_post)
                self.session.commit()

        if source == "comments":
            Comments = self.Comments
            for entry in data:
                new_comment = Comments(
                    created_at=fake.date_time_this_decade(),
                    body=entry["body"],
                    likes=entry["likes"],
                    post_id=entry["postId"],
                    author_id=entry["id"]
                )

                self.session.add(new_comment)
                self.session.commit()

    def export_to_csv(self):
        users_data = self.session.query(self.Users).all()
        posts_data = self.session.query(self.Posts).all()
        comments_data = self.session.query(self.Comments).all()

        output_directory = "data/"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        csv_files = {
            "users.csv": users_data,
            "posts.csv": posts_data,
            "comments.csv": comments_data
        }

        for file_name, data in csv_files.items():
            filepath = os.path.join(output_directory, file_name)

            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Write headers
                if data:
                    headers = data[0].__table__.columns.keys()
                    writer.writerow(headers)

                    # Write rows
                    for row in data:
                        writer.writerow([getattr(row, column) for column in headers])

    def close(self):
        self.session.close()

    @property
    def models(self):
        return Users, Posts, Comments
