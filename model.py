import uuid

from sqlalchemy.dialects.postgresql import UUID

from app import db

import marshmallow_sqlalchemy as m_sqla
from marshmallow_sqlalchemy import fields


class Compound(db.Model):
    compound_id = db.Column(db.Integer, primary_key=True)
    compound_name = db.Column(db.String)
    compound_structure = db.Column(db.String)


class ETLRun(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    time_stamp = db.Column(db.TIMESTAMP)
    results = db.relationship('ETLUserResults', backref='ETLRun', cascade='all, delete')
    total_experiments = db.Column(db.Integer)
    most_common_compound_id = db.Column(db.Integer, db.ForeignKey(Compound.compound_id))
    most_common_compound = db.relationship('Compound', backref='Compound')


class ETLUser(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    signup_date = db.Column(db.DATE)


class ETLUserResults(db.Model):
    results_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey(ETLUser.user_id))
    user = db.relationship('ETLUser', backref='ETLUser')
    run_id = db.Column(UUID(as_uuid=True), db.ForeignKey(ETLRun.id))
    avg_experiment_runtime = db.Column(db.Float)


# Schema for pretty return to API calls
class ETLUserSchema(m_sqla.SQLAlchemyAutoSchema):

    class Meta:
        model = ETLUser


class CompoundSchema(m_sqla.SQLAlchemyAutoSchema):

    class Meta:
        model = Compound


class ETLUserResultsSchema(m_sqla.SQLAlchemyAutoSchema):

    class Meta:
        model = ETLUserResults

    user = fields.Nested(ETLUserSchema(), exclude=('email', 'signup_date', ))


class ETLRunSchema(m_sqla.SQLAlchemyAutoSchema):

    class Meta:
        model = ETLRun
        include_relationships = True

    results = fields.Nested(ETLUserResultsSchema(), many=True, exclude=('results_id',))
    most_common_compound = fields.Nested(CompoundSchema())


etl_user_results_schema = ETLUserResultsSchema()
etl_run_schema = ETLRunSchema()
user_schema = ETLUserSchema()