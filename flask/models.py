import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DefaultApplication(db.Model):
    __tablename__ = 'default_application'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    audit_status = db.Column(db.SmallInteger, nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    #upload_user = db.Column(db.String(50), nullable=False)
    uploaduser_id = db.Column(db.Integer, nullable=False)
    application_time = db.Column(db.DateTime, nullable=False)
    audit_data = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.Text, nullable=False)
    default_status = db.Column(db.SmallInteger, nullable=False)

    # Define relationship to Customer
    customer = db.relationship('Customer', backref=db.backref('default_applications', lazy=True))

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.SmallInteger, nullable=False)
    industry_classification = db.Column(db.String(50), nullable=False)
    region_classification = db.Column(db.String(50), nullable=False)
    credit_rating = db.Column(db.String(50), nullable=True)
    group = db.Column(db.String(50), nullable=True)
    external_rating = db.Column(db.String(50), nullable=False)

class DefaultRebirth(db.Model):
    __tablename__ = 'default_rebirth'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    default_id = db.Column(db.Integer, db.ForeignKey('default_application.id'), nullable=False)
    audit_status = db.Column(db.SmallInteger, nullable=False)
    remarks = db.Column(db.Text, nullable=False)

    # Define relationships to Customer and DefaultApplication
    customer = db.relationship('Customer', backref=db.backref('default_rebirths', lazy=True))
    default_application = db.relationship('DefaultApplication', backref=db.backref('default_rebirths', lazy=True))
