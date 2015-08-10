# Run pairwise institution distance for each geotiff pixel on EMR
import argparse
import logging
import time
import sys

from boto import s3, emr

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

SCRIPT_RUNNER='s3://elasticmapreduce/libs/script-runner/script-runner.jar'
COPY='/home/hadoop/lib/emr-s3distcp-1.0.jar'
HADOOP='/home/hadoop/bin/hadoop'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jar', dest='jar', required=True)
    parser.add_argument('--raster_csv', dest='raster_csv', required=True)
    parser.add_argument('--institution_csv', dest='institution_csv', required=True)
    parser.add_argument('--output_s3_bucket', dest='bucket', required=True)
    parser.add_argument('--output_s3_prefix', dest='prefix', required=True)
    parser.add_argument('--output_file', dest='output_file', required=True)
    return parser.parse_args()


def upload_inputs(jar, raster_csv, institution_csv, bucket, prefix):
    logger.info("Uploading inputs to s3..")
    s3_conn = s3.connect_to_region('us-west-2')
    bucket = s3_conn.get_bucket(bucket)
    logger.info("Uploading " + raster_csv + " to " + prefix + '/raster_data.csv')
    raster_csv_key = bucket.new_key(prefix + '/raster_data.csv')
    raster_csv_key.set_contents_from_filename(raster_csv)
    logger.info("Uploading " + institution_csv + " to " + prefix + '/institution_data.csv')
    institution_csv_key = bucket.new_key(prefix + '/institution_data.csv')
    institution_csv_key.set_contents_from_filename(institution_csv)
    logger.info("Uploading " + jar + " to " + prefix + '/jar.jar')
    jar_key = bucket.new_key(prefix + '/jar.jar')
    jar_key.set_contents_from_filename(jar)


def collect_output(bucket, prefix, output_file):
    s3_conn = s3.connect_to_region('us-west-2')
    bucket = s3_conn.get_bucket(bucket)

    keys = bucket.list(prefix=prefix + '/output')
    with open(output_file, 'w') as of:
        for k in keys:
            k.get_contents_to_file(of)


def run_emr(bucket, prefix):
    conn = emr.connect_to_region('us-west-2')
    steps = [
        emr.JarStep('makedir', jar=SCRIPT_RUNNER,
                    step_args=[HADOOP, 'fs', '-mkdir', '-p', '/data/']),
        emr.JarStep('download_to_client', jar=SCRIPT_RUNNER,
                    step_args=[HADOOP, 'fs', '-get',
                               's3://' + bucket + '/' + prefix + '/institution_data.csv',
                               '/home/hadoop/institution_data.csv']),
        emr.JarStep('download_to_hdfs', jar=SCRIPT_RUNNER,
                    step_args=[HADOOP, 'fs', '-cp',
                               's3://' + bucket + '/' + prefix + '/raster_data.csv',
                               '/data/raster_data.csv']),
        emr.JarStep('download_jar_to_client', jar=SCRIPT_RUNNER,
                    step_args=[HADOOP, 'fs', '-get',
                               's3://' + bucket + '/' + prefix + '/jar.jar',
                               '/home/hadoop/jar.jar']),
        emr.JarStep('run_spark', jar=SCRIPT_RUNNER,
                    step_args=['/home/hadoop/spark/bin/spark-submit',
                               '--files',
                               '/home/hadoop/institution_data.csv',
                               '--master',
                               'yarn-cluster',
                               '--class',
                               'com.pairwise.PairwiseDistance',
                               '--num-executors',
                               '10',
                               '/home/hadoop/jar.jar',
                               '/home/hadoop/institution_data.csv',
                               '/data/raster_data.csv',
                               '/data/output',
                               '10']),
        emr.JarStep('get_output', jar=COPY,
                    step_args=['--src',
                               '/data/output',
                               '--dest',
                               's3://' + bucket + '/' + prefix + '/output'])]
    bootstrap_actions = [
        emr.BootstrapAction('install-spark',
                            path='file:///usr/share/aws/emr/install-spark/install-spark',
                            bootstrap_action_args=['-x'])]

    jid = conn.run_jobflow('pairwise_distance', log_uri='s3://' + bucket + '/' + prefix + '/logs',
                     master_instance_type='m3.xlarge',
                     slave_instance_type='m3.xlarge',
                     num_instances=5,
                     enable_debugging=True,
                     ami_version='3.8',
                     visible_to_all_users=True,
                     steps=steps,
                     bootstrap_actions=bootstrap_actions)

    logger.info("Running jobflow: " + jid)
    while True:
        time.sleep(15)
        state = conn.describe_cluster(jid).status.state
        logger.info("Jobflow " + jid + ": " + state)
        if state == 'TERMINATED':
            break
        elif state == 'TERMINATED_WITH_ERRORS':
            sys.exit(1)

def main():
    args = get_args()
    upload_inputs(args.jar, args.raster_csv, args.institution_csv, args.bucket, args.prefix)
    run_emr(args.bucket, args.prefix)
    collect_output(args.bucket, args.prefix, args.output_file)

if __name__ == '__main__':
    main()
