import datetime
import os

import pandas as pd
from flask import request

from app import app, db
from model import ETLRun, ETLUserResults, ETLUser, etl_run_schema, Compound, etl_user_results_schema


def etl(run_label: str = '', data_dir: str = 'data/') -> ETLRun:
    # Load CSV files
    compounds_data: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'compounds.csv'), sep=',\t', engine='python')
    user_data: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'users.csv'), sep=',\t', engine='python')
    experiments: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'user_experiments.csv'), sep=',\t', engine='python')

    # upload user data as is - no transformation to make later retrieval more useful
    for i, row_series in user_data.iterrows():
        user = ETLUser(
            **row_series.to_dict()
        )
        found_users = ETLUser.query.filter_by(user_id=user.user_id).first()
        if not found_users:
            db.session.add(user)
            db.session.commit()

    for i, row_series in compounds_data.iterrows():
        compound = Compound(
            **row_series.to_dict()
        )
        found_compounds = Compound.query.filter_by(compound_id=compound.compound_id).first()
        if not found_compounds:
            db.session.add(compound)
            db.session.commit()


    # calculate avg experiments per user
    '''
    assuming that we only care about the average ~among users who actually performed at least one experiment~.
    justification: 
        if used within a single organization, it is likely that the same user.csv 
        would be used over and over again, only needing to be updated when a new
        team member is added. therefore we likely dont care about the average experiments
        across the entire org.
    '''

    # Calculate experiments by each person

    grouped_experiments = experiments.groupby('user_id', as_index=False).agg(
        {
            'experiment_run_time': lambda x: sum(x) / x.count(),
            'experiment_id': lambda x: x.nunique(),
            'experiment_compound_ids': lambda x: max(
                list(''.join(x).replace(';', '')), key=list(''.join(x).replace(';', '')).count
            )
        }
    ).rename(
        columns={
            'experiment_run_time': 'avg_experiment_runtime',
            'experiment_id': 'total_experiments',
            'experiment_compound_ids': 'most_common_compound'
        }
    )

    # Upload processed data into a database
    new_run = ETLRun(
        label=run_label,
        time_stamp=datetime.datetime.now(),
    )
    db.session.add(new_run)
    db.session.commit()

    for i, row_series in grouped_experiments.iterrows():
        user_results_as_dict = row_series.to_dict().copy()
        user_results_as_dict.update(
            {
                "run_id": new_run.id
            }
        )
        new_etl_user_results = ETLUserResults(
            **user_results_as_dict
        )
        db.session.add(new_etl_user_results)
        db.session.commit()

    return new_run


# Your API that can be called to trigger your ETL process
@app.route('/trigger_etl', methods=['POST'])
def trigger_etl():
    run_label = request.json.get('label')
    # Trigger your ETL process here
    new_run = etl(run_label=run_label)
    return etl_run_schema.dump(new_run)


@app.route('/etl_results/<etl_id>', methods=['GET'])
def etl_results(etl_id):
    run_object = ETLRun.query.filter_by(id=etl_id).first()
    if run_object:
        results_objects = ETLUserResults.query.filter_by(run_id=run_object.id).all()
        return etl_user_results_schema.dump(results_objects, many=True)
    else:
        return "Could not find the ETL results you are looking for."


@app.route('/results_by_user/<user_id>', methods=['GET'])
def results(user_id):
    results_objects = ETLUserResults.query.filter_by(user_id=user_id).all()
    if results_objects:
        return etl_user_results_schema.dump(results_objects, many=True)
    else:
        return "Could not find the ETL results you are looking for."
