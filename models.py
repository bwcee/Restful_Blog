from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine, Integer, Table, Column, ForeignKey, Boolean
from migrate.versioning.schema import Table, Column


db = SQLAlchemy()

## CONFIGURE TABLE
# reduced lengths below date:250->80, author:250->100, img_url:250->400
# not sure if it will affect posts.db file which is alr created
# nope, think once the file is created, the table config parameters are ignored
# hmmm mebbe cos there is no db.create_all() at the end
# the class is solely to provide sqlalchemy w info abt how e table is structured?


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100))
    img_url = db.Column(db.String(400), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user_records.id"))
    author_new = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post")


class Users(db.Model):
    __tablename__ = "user_records"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    posts = relationship("BlogPost", back_populates="author_new")
    comments = relationship("Comments", back_populates="user")

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user_records.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_post.id"))
    user = relationship("Users", back_populates="comments")
    post = relationship("BlogPost", back_populates="comments")

# line below only used in initial creation of tables
# db.create_all()


##Create user_id column in blog_post table so can create relationship between BlogPost and Users
##Altho it seems sqlalchemy-migrate which I used here is obsolete. recommended package to use now is actually Alembic
##Deleting a column is not recommend tho. So end up w unused author column
# db_engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
# db_meta = MetaData(bind=db_engine)
#
# table = Table('blog_post', db_meta)
# col = Column('user_id', Integer)
# col.create(table)

##Alembic method to create admin column in Users is more involved
