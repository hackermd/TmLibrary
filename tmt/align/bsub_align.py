#!/usr/bin/env python
import os
import glob
from time import time
from datetime import datetime
import argparse
import yaml
import tmt
from tmt.cluster import Cluster


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Submit jobs for shift calculation.')

    parser.add_argument('experiment_dir', default=os.getcwd(),
                        help='experiment directory')

    parser.add_argument('-c', '--config', dest='config',
                        help='use custom yaml configuration file \
                        (defaults to "tmt" config file)')

    args = parser.parse_args()

    experiment_dir = args.experiment_dir

    if args.config:
        # Overwrite default "tmt" configuration
        print '. Using configuration file "%s"' % args.config
        args.config = tmt.util.load_config(args.config)
        print '. Checking configuration file'
        tmt.util.check_config(args.config)
    else:
        args.config = tmt.config

    joblist_filenames = glob.glob(os.path.join(experiment_dir, 'align*.jobs'))
    if len(joblist_filenames) == 1:
        joblist_filename = joblist_filenames[0]
    elif len(joblist_filenames) > 1:
        raise OSError('There must not be more than one joblist file.')
    else:
        raise OSError('Joblist file does not exist.')

    with open(joblist_filename, 'r') as joblist_file:
        joblist = yaml.load(joblist_file.read())

    for job_id in range(1, len(joblist)+1):

        ts = datetime.fromtimestamp(time()).strftime('%Y-%m-%d_%H-%M-%S')
        lsf = os.path.join(experiment_dir, 'lsf',
                           'align_%.5d_%s.lsf' % (job_id, ts))

        command = ['align', 'run', '--job', str(job_id), experiment_dir]

        print '. submitting job #%d' % job_id

        job = Cluster(lsf)
        job.submit(command)
