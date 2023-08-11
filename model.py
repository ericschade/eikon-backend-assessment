import uuid

from sqlalchemy.dialects.postgresql import UUID

from app import db

import marshmallow_sqlalchemy as m_sqla


class ETLRun(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = db.Column(db.String)
    time_stamp = db.Column(db.TIMESTAMP)


class ETLUser(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    signup_date = db.Column(db.DATE)


class Compound(db.Model):
    compound_id = db.Column(db.Integer, primary_key=True)
    compound_name = db.Column(db.String)
    compound_structure = db.Column(db.String)


class ETLUserResults(db.Model):
    results_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey(ETLUser.user_id))
    run_id = db.Column(UUID(as_uuid=True), db.ForeignKey(ETLRun.id))
    total_experiments = db.Column(db.Integer)
    avg_experiment_runtime = db.Column(db.Float)
    most_common_compound = db.Column(db.Integer, db.ForeignKey(Compound.compound_id))


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


class ETLRunSchema(m_sqla.SQLAlchemyAutoSchema):

    class Meta:
        model = ETLRun


etl_user_results_schema = ETLUserResultsSchema()
etl_run_schema = ETLRunSchema()
user_schema = ETLUserSchema()