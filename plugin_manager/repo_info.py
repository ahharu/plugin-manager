# -*- coding: utf-8 -*-
#from fabric.api import local, env
from fabric.api import *
from fabric.operations import run, put
from fabric.colors import blue, cyan, green, red, white, yellow, magenta
from fabric.decorators import task
from StringIO import StringIO
from datetime import date, datetime
from xml.etree import ElementTree as ET
import random
import time
from fabric.contrib.console import confirm
from fabtools import service
import os
from git import *

from jenkinsapi.jenkins import Jenkins

now = datetime.today()


def getLatestJobWithInfo(job):
    lgb = job.get_last_good_build()
    vernumber = lgb.get_number()
    if(lgb._data["changeSet"]["kind"] == "svn"):
        return lgb
    while (len(lgb._data["changeSet"]["items"]) == 0 or not lgb.is_good()):
        vernumber = vernumber - 1
        lgb = job.get_build(vernumber)
    return lgb


class RepoInfo():

    def getSCMInfroFromLatestGoodBuild(self, url, jobName):
        J = Jenkins(url)
        job = J[jobName]
        lgb = getLatestJobWithInfo(job)

        repotype = lgb._data["changeSet"]["kind"]
        if repotype not in ["svn", "git"]:
            raise(NotImplementedError)
        rev = lgb.get_revision()
        if repotype == "svn":
            repourl = lgb._data["changeSet"]["revisions"][0]["module"]
            repourl = repourl.replace("devext01", "devext")
            # ok, lets find svn info
            with hide('running', 'stdout'):
                response = local("svn log --verbose -r %s %s \
                                  --non-interactive --no-auth-cache \
                                  --username alruiz --password 6Ym*ep64?mI8" % (
                                 rev, repourl), capture=True)
            return response
        elif repotype == "git":
            actions = ""
            info = lgb._data["changeSet"]["items"][0]
            for x in info["paths"]:
                actions += x["editType"] + "  " + x["file"] + "\n"
            response = ("Git Hash: " + info["id"] + "\n" + "Author: " +
                        info["author"]["fullName"] +
                        "\n" + "Time:  " + time.strftime('%d-%m-%Y %H:%M:%S ',
                                                         time.gmtime(
                                                             info["timestamp"])) +
                        " \n**Actions** \n") + actions
            return response
        else:

            raise(NotImplementedError)
        return rev
