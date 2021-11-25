import json

from crontab import CronTab
from croniter import croniter
from datetime import datetime

import os
import signal
import sys

import logging

dir_name, f_name = os.path.split(__file__)


def startLogging():
    logging.basicConfig(filename=dir_name + '/myapp.log',
                        level=logging.DEBUG,
                        format="[%(asctime)s]:%(levelname)s: %(message)s")


def getConfigInform():
    try:
        logging.info("Try for read json config file")
        logging.debug("Path to the json config file: " +
                      dir_name + "/settings.json")
        this_config = {}
        try:
            file = open(dir_name + "/settings.json")
            this_config = json.loads(file.read())
            logging.info("json config file read successfully")
            return this_config
        except IOError as e:
            logging.error(e)

            logging.debug("Config file: " + str(this_config))
    except Exception as e:
        logging.error(e)


def getCrontabList(tab_file_name):
    """Crontab file parser"""
    logging.info("Try to read crontab file")
    try:
        cron = CronTab(tabfile=tab_file_name)

        jobs_list = []

        datetime_to_start_cron = datetime.now().timestamp()

        for job in cron:
            job_time_in_croniter = croniter(str(job.slices), datetime_to_start_cron, is_prev=True)

            jobs_list.append([job_time_in_croniter, job.command])

        logging.info("Crontab read successfully")
        return jobs_list
    except Exception as exc:
        logging.error("Error:{}".format(e))
        sys.exit(1)


def runCommand(command):
    return_value = 3
    try:
        return_value = os.system(command)
        logging.info("Successfully executed command: '{}'".format(command))
    except Exception as e:
        logging.error("Error:{}, CommandToExecute: '{}'".format(e, command))
    finally:
        sys.exit(return_value)


def process(jobs_list):
    if len(jobs_list) == 0:
        logging.info("Nothing to execute. Check if there is any commands and their spelling is right. End of program")
        sys.exit(0)
    logging.info("Trying run commands")
    while True:
        time_now = datetime.now().timestamp()
        for job in range(len(jobs_list)):
            if jobs_list[job][0].get_current() <= time_now:
                jobs_list[job][0].get_next()
                pid = os.fork()

                if pid > 0:
                    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
                    continue
                else:
                    runCommand(jobs_list[job][1])


if __name__ == "__main__":
    startLogging()
    logging.info("Start of program")
    config = getConfigInform()
    jobs_list = getCrontabList(config["CRONTAB_PATH"])
    process(jobs_list)
