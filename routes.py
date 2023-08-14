import datetime
import os

import pandas as pd
from uuid import UUID

from app import app, db
from model import ETLRun, ETLUserResults, ETLUser, etl_run_schema, Compound, etl_user_results_schema


def upload_new_compounds(compound_table: pd.DataFrame):
    # upload compound data
    for i, row_series in compound_table.iterrows():
        compound = Compound(
            **row_series.to_dict()
        )
        found_compounds = Compound.query.filter_by(compound_id=compound.compound_id).first()
        if not found_compounds:
            db.session.add(compound)
            db.session.commit()


def upload_new_users(user_table: pd.DataFrame):
    # upload user data as is - no transformation but storing new users will make later retrieval more useful
    for i, row_series in user_table.iterrows():
        user = ETLUser(
            **row_series.to_dict()
        )
        found_users = ETLUser.query.filter_by(user_id=user.user_id).first()
        # not worrying about updating existing users with new data
        if not found_users:
            db.session.add(user)
            db.session.commit()


def upload_new_etl_user_results(grouped_experiments: pd.DataFrame, new_run: ETLRun):
    for i, row_series in grouped_experiments.iterrows():
        user_results_as_dict = row_series.to_dict()
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


def etl(data_dir: str = 'data/') -> ETLRun:
    # Load CSV files
    compounds_data: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'compounds.csv'), sep=',\t', engine='python')
    user_data: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'users.csv'), sep=',\t', engine='python')
    experiments: pd.DataFrame = pd.read_csv(os.path.join(data_dir, 'user_experiments.csv'), sep=',\t', engine='python')

    # upload new users and compounds - not strictly necessary but nice to have
    # when returning the results schema later
    upload_new_users(user_data)
    upload_new_compounds(compounds_data)

    # summarize data for storage
    '''
    I found the wording in the challenge README to be a little ambiguous and thus wasn't sure whether
     to make each of calculations on a per user basis so I went forward with my best guess based 
     on the wording of the prompt.
      
      1. Total experiments completed in the etl run across all users.
        - how big was the dataset we just analyzed?
      2. For each user, the average experiment runtime. 
        - what kinds of experiments/how much work did XXX do compared to XXX?
      3. Most common compound used across all experiments.
        - characterize the dataset as a whole
      
    '''
    # calculation per user
    grouped_experiments = experiments.groupby('user_id', as_index=False).agg(
        {
            'experiment_run_time': lambda x: sum(x) / x.count()
        }
    ).rename(
        columns={
            'experiment_run_time': 'avg_experiment_runtime'
        }
    )

    # calculations in aggregate
    all_compounds_used = ';'.join(experiments['experiment_compound_ids'])
    most_common_compound_id = max(
        list(''.join(all_compounds_used).replace(';', '')),
        key=list(''.join(all_compounds_used).replace(';', '')).count
    )
    total_experiments = experiments['experiment_id'].nunique()

    # Upload processed data into the database
    new_run = ETLRun(
        time_stamp=datetime.datetime.now(),
        most_common_compound_id=most_common_compound_id,
        total_experiments=total_experiments
    )
    db.session.add(new_run)
    db.session.commit()

    # etl_user_results table will hold the user specific data, currently just
    # the avg runtime for each used in the dataset which was just loaded
    upload_new_etl_user_results(
        grouped_experiments=grouped_experiments,
        new_run=new_run
    )

    return new_run


# API
@app.route('/trigger_etl', methods=['POST'])
def trigger_etl():
    # Trigger the ETL process
    new_run = etl()
    return etl_run_schema.dump(new_run)


@app.route('/etl_results/<etl_id>', methods=['GET'])
def etl_results(etl_id):
    """
    :param etl_id: an ID
    :return: Return a rich representation of the etl run object, including nested compound and user objects.
    """
    try:
        UUID(etl_id, version=4)
    except ValueError:
        return "Not a valid UUID - try again!"
    run_object = ETLRun.query.filter_by(id=etl_id).first()
    if run_object:
        results_objects = ETLUserResults.query.filter_by(run_id=run_object.id).all()
        return etl_user_results_schema.dump(results_objects, many=True)
    else:
        return "Could not find the ETL results you are looking for."


@app.route('/results_by_user/<user_id>', methods=['GET'])
def results(user_id):
    """
    :param user_id: user ID to grab data for
    :return: Get all past results tied to the specified user
    """
    results_objects = ETLUserResults.query.filter_by(user_id=user_id).all()
    if results_objects:
        return etl_user_results_schema.dump(results_objects, many=True)
    else:
        return "Could not find the ETL results you are looking for."
