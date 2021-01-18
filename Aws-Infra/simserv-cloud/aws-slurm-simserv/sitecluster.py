#!/usr/bin/env python
# Copyright 1983-2020 Keysight Technologies
from __future__ import print_function
import argparse
import json
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
import tempfile


try:
    from subprocess import STDOUT, check_output, CalledProcessError
except ImportError:  # pragma: no cover
    # python 2.6 doesn't include check_output
    # monkey patch it in!
    import subprocess
    STDOUT = subprocess.STDOUT

    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:  # pragma: no cover
            raise ValueError('stdout argument not allowed, '
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd,
                                                output=output)
        return output
    subprocess.check_output = check_output

    # overwrite CalledProcessError due to `output`
    # keyword not being available (in 2.6)
    class CalledProcessError(Exception):

        def __init__(self, returncode, cmd, output=None):
            self.returncode = returncode
            self.cmd = cmd
            self.output = output

        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (
                self.cmd, self.returncode)
    subprocess.CalledProcessError = CalledProcessError


class SiteCluster(object):

    # SiteCluster version
    __version__ = ['core_1']

    def __init__(self, use_argv=True, ignore_user=True):
        '''
        Constructor
        '''
        if not use_argv:
            return

        self.ignore_user = ignore_user

        parser = argparse.ArgumentParser(
            description='site cluster',
            usage='''sitecluster <command> [<args>]

The supported sitecluster commands are:
    api                                 Returns the sitecluster api version, minimum version is 'core_1'.
    queues                              Returns a list with queues, one queue on each line.
    submit [<options>] -- <cmd> <args>     Submits a job to the site cluster.
        supported submit options:
            [--queue=<queue>]           Queue on which the job should run (Optional).
            [--nodes=<nodes>]           Number of nodes to be reserved for the job (Optional).
            [--threads=<threads>]       Number of threads per node requested for this job (Optional).
            [--memory=<memory>]         Maximum amount of physical memory used by the job (Optional).
            [--jobname=<jobname>]       Name of the job (Optional).
            [--email=<email>]           List of email addresses to notify, format user[@host][,user[@host],...] (Optional).
            [--attime=<attime>]         Time after which the job is eligible for execution, format [[[[CC]YY]MM]DD]hhmm[.SS] (Optional).
            [--endtime=<endtime>]       End time of the job, format [[[[CC]YY]MM]DD]hhmm[.SS] (Optional).
            [--after=<after>]           List of jobs to wait for, format ['j1'.j2] (Optional).
            [--startnode=<node>]        Number of node to run sub process directly (Optional).
            [--user=<username>]         Submit job as user with name <username> (only available if allowed by system)
            [--project=<projectname>]   add a project/account name on submit when available (Optional).
            [--group=<groupname>]       add a group name for submit when available (Optional).
            [--customargs=<customargs>] Custom submit arguments for the job. Repeated occurences append customargs content. (Optional)
    status  ['-e','--add-exit-status'] <JobId>            Returns the status of the job with identifier <JobId> on the cluster,
                                        supported states are 'PENDING', 'RUNNING', 'SUSPENDED', 'COMPLETED' and UNKNOWNID.
                                        Optional options -e and --exit adds an optional exit status as provided by the cluster system
    kill <JobId> [<JobId> ...]          Kills the jobs with the specied <JobId>s.
    nodecount                           Returns the total number of nodes allocated to the job. Only usable within a job's environment.
    startnode <num> <cmd> <args>        Starts the command <cmd> with arguments <args> on node <num>.
    behavior                            Returns default behavior specifications.
''')
        parser.add_argument('command', choices=['api', 'queues', 'submit', 'status', 'kill', 'nodecount', 'startnode', 'behavior'],
                            help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def api(self):
        '''
        Prints the site cluster api version.
        '''
        for version in SiteCluster.__version__:
            print(version)

    def queues(self):
        '''
        Prints the available queues.
        '''
        queues = self.getQueues()
        for queue in queues:
            print(queue)

    def submit(self):
        '''
        Submits a job to the cluster.
        '''
        parser = argparse.ArgumentParser(description='submit', usage='%(prog)s submit [options] -- cmdargs')
        parser.add_argument('--queue', help='Queue on which the job should run (Optional).')
        parser.add_argument('--nodes', type=int, metavar='<n>', help='Number of nodes to be reserved for exclusive use by the job (Optional).')
        parser.add_argument('--threads', type=int, metavar='<n>', help='Number of threads per node requested for this job (Optional).')
        parser.add_argument('--memory', help='Maximum amount of physical memory used by the job (Optional).')
        parser.add_argument('--jobname', help='Name of the job (Optional).')
        parser.add_argument('--email', help='List of email addresses to notify, format user[@host][,user[@host],...] (Optional).')
        parser.add_argument('--attime', help='Time after which the job is eligible for execution, format [[[[CC]YY]MM]DD]hhmm[.SS] (Optional).')
        parser.add_argument('--endtime', help='End time of the job, format [[[[CC]YY]MM]DD]hhmm[.SS] (Optional).')
        parser.add_argument('--after', help="List of jobs to wait for, format ['j1'.j2] (Optional).")
        parser.add_argument('--project', help="Project/account setting for cluster system if available (Optional).")
        parser.add_argument('--group', help="Groupname setting for cluster system if available (Optional).")
        parser.add_argument('--customargs', action='append', help='Custom submit arguments for the job. (Optional).')
        parser.add_argument('--startnode', type=int, metavar='<n>', help='Number of node to run sub process within a job just as with startnode command. (Optional).')
        parser.add_argument('--user', help='Defines the user name under which the job is to run on the execution system if allowed by workload system (Optional).')
        parser.add_argument('cmdargs', nargs=argparse.REMAINDER)
        if not sys.argv[2:]:
            parser.print_help()
        args = parser.parse_args(sys.argv[2:])
        cmdargs = None
        if len(args.cmdargs) > 1 and args.cmdargs[0] == '--':
            cmdargs = args.cmdargs[1:]
        if not hasattr(self, 'submitJob'):
            parser.print_help()
        else:
            print(self.submitJob(args, cmdargs))

    def status(self):
        '''
        Returns the status of a job.
        '''
        parser = argparse.ArgumentParser(description='status', usage='%(prog)s status [options] jobId')
        parser.add_argument('-e', '--add-exit-status', dest='addStatus', action='store_true', help='Return the job exit status when available after COMPLETED')
        parser.add_argument('jobId')
        if not sys.argv[2:]:
            parser.print_help()
        args = parser.parse_args(sys.argv[2:])
        if not hasattr(self, 'getJobStatus'):
            parser.print_help()
        else:
            print(self.getJobStatus(args.jobId, args.addStatus))

    def kill(self):
        '''
        Kills a job.
        '''
        parser = argparse.ArgumentParser(description='kill', usage='%(prog)s kill jobId [jobId ...]')
        parser.add_argument('jobId', nargs='+', help='Kills the jobs with the specied <JobId>s')
        if not sys.argv[2:]:
            parser.print_help()
        args = parser.parse_args(sys.argv[2:])
        if not hasattr(self, 'killJob'):
            parser.print_help()
        else:
            print(self.killJob(args.jobId))

    def nodecount(self):
        print(self.getNodeCount())

    def startnode(self):
        self.startNode(sys.argv[2], sys.argv[3:])

    def behavior(self):
        behavior = {}

        ## qbehave mode:
        # behavior = {
        #     'alpha': {
        #         'command_argument_string': '',
        #         'allow_user_command_argument_string_suffix': True,
        #     },
        #     'beta': {
        #         'mapping': [
        #             {
        #                 'memory': [0,5],
        #                 'command_argument_string': '',
        #             },
        #             {
        #                 'memory': [5,50],
        #                 'command_argument_string': '',
        #             }
        #             # ...
        #         ],
        #         'allow_user_command_argument_string_suffix': True,
        #     },
        #     'omega': {
        #         'command_argument_string': '',
        #         'allow_user_command_argument_string_suffix': True,
        #     },
        # }

        print(json.dumps(behavior))

class PBSSiteCluster(SiteCluster):

    def __init__(self, use_argv=True, ignore_user=True):
        SiteCluster.__init__(self, use_argv=use_argv, ignore_user=ignore_user)

    def getQueues(self):
        cmd = ['qstat', '-Q']
        reAnsw = r'([a-zA-Z0-9_\.-]+)[ ]*([0-9]+).*'
        queueNames = []
        for s in [s.strip() for s in subprocess.check_output(cmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                queueNames.append(reMatch.group(1))
        return queueNames

    def submitJob(self, options, cmdargs):
        #  sub job start within job
        if options.startnode:
            self.startNode(options.startnode, cmdargs)
            return str(int(os.environ['PBS_JOBID']))

        submitCmd = ['qsub', '-V', '-W', 'umask=022']
        # destination  queue of the job
        if options.queue:
            submitCmd += ['-q', options.queue]
        # name of the job
        if options.jobname:
            submitCmd += ['-N', options.jobname]
        # resources
        resources = []
        if options.nodes:
            # number of nodes to be reserved for the job.
            resources += ['nodes=%d'% options.nodes]
        if options.threads:
            # the number of virtual processors/threads per node requested for this job
            resources += ['ppn=%d'% options.threads]
        if options.memory:
            # maximum amount of physical memory used by any single process of the job
            resources += ['pmem=%s'% options.memory]
        if resources:
            submitCmd += ['-l', ':'.join(resources)]
        # list of email addresses to notify
        if options.email:
            submitCmd += ['-M', options.email]
            # email is sent by default on following events:
            #   a - when the job is aborted by the batch system.
            #   b - when the job begins execution.
            #   e - when the job terminates.
            submitCmd += ['-m', 'abe']
        # time after which the job is eligible for execution
        if options.attime:
            submitCmd += ['-a', options.attime]
        # time when the job should be finished
        if options.endtime:
            submitCmd += ['-dl', options.endtime]
        # dependency between other jobs
        if options.after:
            afterJobs = eval(options.after)
            if afterJobs != []:
                submitCmd += ['-W', 'depend=after:%s' % ":".join(afterJobs)]
        # submit as specific user (typically only allowed for administrators)
        if not self.ignore_user and options.user:
            submitCmd += ['-u', options.user]
        # PBS has no project option using account option instead
        if options.project:
            submitCmd += ['-A', options.project]
        if options.group:
            submitCmd += ['-W', 'group_list=%s'% options.group]
        # custom arguments is an array need to decide how to process
        # TODO need to decide how to process arguments if duplicates are not allowed
        if options.customargs:
            customArgArray = []
            # just append when multiple customargs arguments existed
            for entry in options.customargs:
                customArgArray += shlex.split(entry, posix=False)
            submitCmd += customArgArray
        # the command to submit and its arguments
        submitCmd += cmdargs
        # perform the job submission
        res = ''
        reAnsw = r'(^\d+\.[\w\.\-]+).*'
        for s in [s for s in subprocess.check_output(submitCmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                res = str(reMatch.group(1))
        return res

    def getJobStatus(self, idOnCluster, addStatus=False):
        cmd = ['qstat', '-f', idOnCluster]
        try:
            # stderr=subprocess.STDOUT redirection is needed for getting the "Unknown Job Id" in err.output
            output = [s for s in subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()]
        except CalledProcessError as err:
            print(err.output, file=sys.stderr)
            # PBS error code PBSE_UNKJOBID = 15001; PBSE_UNKJOBID mod 256 = 153
            if err.returncode == 153 or "Unknown Job Id" in err.output:
                return "UNKNOWNID"
            raise

        reAnsw = r'\s+job_state\s+=\s+([BEHQRSTUWX])'
        rstate = ''
        for s in output:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                rstate = reMatch.group(1)
                break
        jobStatus = 'COMPLETED'
        if rstate == '':
            jobStatus = 'COMPLETED'
        elif rstate in 'QW':
            jobStatus = 'PENDING'
        elif rstate in 'BR':
            jobStatus = 'RUNNING'
        elif rstate in 'HTU':
            jobStatus = 'SUSPENDED'
        elif rstate == 'EX':
            jobStatus = 'COMPLETED'

        if addStatus and jobStatus == 'COMPLETED':
            exitStatus = '0'
            reAnsw = r'\s+exit_status\s+=\s+([0-9]+)'
            for s in output:
                reMatch = re.match(reAnsw, s)
                if reMatch:
                    exitStatus = reMatch.group(1)
                    break
            jobStatus += ' ' + exitStatus
        return jobStatus

    def killJob(self, idsOnCluster):
        try:
            output = subprocess.check_output(['qdel'] + [str(x) for x in idsOnCluster], stderr=subprocess.STDOUT, universal_newlines=True).splitlines()
        except CalledProcessError as e:
            output = e.output.splitlines()
        if output:
            for jobId in idsOnCluster:
                res = ''
                for l in output:
                    if str(jobId) in l:
                        res = l
                if not res:
                    continue
                reAnsw = r'Request invalid for state of job.*COMPLETE\s+{}'.format(jobId)
                reMatch = re.search(reAnsw, res)
                if reMatch:
                    continue
                reAnsw = r'nonexistent job id'
                reMatch = re.search(reAnsw, res)
                if reMatch:
                    continue
                return 1
        return 0

    def getNodeCount(self):
        return str(int(os.environ['PBS_NUM_NODES']))

    def startNode(self, num, cmdargs):
        subprocess.check_call(['pbsdsh', '-n', str(int(num))] + cmdargs)

class LSFSiteCluster(SiteCluster):

    def __init__(self, use_argv=True):
        SiteCluster.__init__(self, use_argv=use_argv)

    def getQueues(self):
        cmd = ['bqueues', '-w']
        reAnsw = r'([a-zA-Z0-9_-]+)[ ]*([0-9]+).*'
        queueNames = []
        for s in [s.strip() for s in subprocess.check_output(cmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                queueNames.append(reMatch.group(1))
        return queueNames

    def submitJob(self, options, cmdargs):
        #  sub job start within job
        if options.startnode:
            self.startNode(options.startnode, cmdargs)
            return str(int(os.environ['PBS_JOBID']))

        submitCmd = ['bsub']
        # destination  queue of the job
        if options.queue:
            submitCmd += ['-q', options.queue]
        # name of the job
        if options.jobname:
            submitCmd += ['-J', options.jobname]
        # resources
        if options.nodes:
            # number of hosts required to run the job
            submitCmd += ['-n', str(options.nodes)]
        if options.threads:
            ## limit of the number of concurrent threads to thread_limit for the whole job
            #  submitCmd += ['-T', str(options.threads)]
            pass
        if options.memory:
            # per-process physical memory limit for all of the processes belonging to a job
            # specified in KB
            submitCmd += ['-M', str(options.memory)]
        # list of email addresses to notify
        if options.email:
            submitCmd += ['-u', options.email]
            # email is sent by default on following events:
            #   -B - when the job is dispatched and begins execution..
            #   -N - when the job finishes.
            submitCmd += ['-B', '-N']
        # time after which the job is eligible for execution
        if options.attime:
            submitCmd += ['-b', options.attime]
        # time when the job should be finished
        if options.endtime:
            submitCmd += ['-t', options.endtime]
        # dependency between other jobs
        if options.after:
            afterJobs = eval(options.after)
            if afterJobs != []:
                submitCmd += ['-w', '\"ended(' + '|'.join(afterJobs) + ')\"']
        # project options for submit
        if options.project:
            submitCmd += ['-P', options.project]
        # group option for submit
        if options.group:
            submitCmd += ['-G', options.group]
        # custom arguments is an array 
        # TODO need to decide how to process arguments if duplicates are not allowed
        if options.customargs:
            customArgArray = []
            # just append when multiple customargs arguments existed
            for entry in options.customargs:
                customArgArray += shlex.split(entry, posix=False)
            submitCmd += customArgArray
        # the command to submit and its arguments
        if cmdargs and ' ' in cmdargs[0]:
            # LSF does not quote command correctly if containing spaces
            # execute as shell command with arguments instead
            submitCmd += ['/bin/bash']
        submitCmd += cmdargs
        # perform the job submission
        res = ''
        reAnsw = r'Job\s+<([0-9]+)>.*'
        for s in [s for s in subprocess.check_output(submitCmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                res = str(reMatch.group(1))
        return res

    def getJobStatus(self, idOnCluster, addStatus=False):
        cmd = ['bjobs', '-a', idOnCluster]
        reAnsw = r'\s*{}\s+\S+\s+(\w+)\s+.*'.format(idOnCluster)
        reAnswUnk = r'Job\s*<{}>\s*is not found'.format(idOnCluster)
        rstate = ''
        reMatchUnk = None
        for s in [s for s in subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                rstate = reMatch.group(1)
                break
            reMatchUnk = re.match(reAnswUnk, s)
            if reMatchUnk:
                break
        jobStatus = 'COMPLETED'
        if rstate == 'EXIT' or reMatchUnk:
            jobStatus = 'COMPLETED'
            exitStatus = 0
            cmdhist = ['bhist', '-la', idOnCluster]
            reAnsw = r'.*: Exited with exit code\s*(\d+).*'
            answSucces = 'Done successfully'
            answUnk = 'No matching job found'
            try:
                output = [s for s in subprocess.check_output(cmdhist, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()]
            except CalledProcessError as err:
                # LSF error code is always 255 so just look for string
                if answUnk in err.output:
                    return "UNKNOWNID"
                raise

            for s in output:
                if answSucces in s:
                    exitStatus = 0
                    break
                if answUnk in s:
                    jobStatus = 'UNKNOWNID'
                    break
                reMatch = re.match(reAnsw, s)
                if reMatch:
                    exitStatus = reMatch.group(1)
                    break
            if addStatus:
                jobStatus += ' ' + str(exitStatus)
        elif rstate == 'PEND':
            jobStatus = 'PENDING'
        elif rstate == 'RUN':
            jobStatus = 'RUNNING'
        elif rstate == 'SUSP':
            jobStatus = 'SUSPENDED'
        elif rstate == 'DONE':
            if addStatus:
                jobStatus = 'COMPLETED 0'
            else:
                jobStatus = 'COMPLETED'
        return jobStatus

    def killJob(self, idsOnCluster):
        cmd = ['bkill'] + [str(x) for x in idsOnCluster]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()
        except CalledProcessError as e:
            output = e.output.splitlines()
        for jobId in idsOnCluster:
            res = ''
            for l in output:
                if str(jobId) in l:
                    res = l
                    break
            if not res:
                continue
            reAnsw = r'Job\s+<{}>\s+is being terminated'.format(jobId)
            reMatch = re.search(reAnsw, res)
            if reMatch:
                continue
            reAnsw = r'Job has already finished'
            reMatch = re.search(reAnsw, res)
            if reMatch:
                # job has already finished
                continue
            return 1
        return 0

    def __getLSBHosts(self):
        if 'LSB_MCPU_HOSTS' in os.environ:
            # host, slot number pairs
            return (True, os.environ['LSB_MCPU_HOSTS'].split(' '))
        else:
            # list with host names
            return (False, os.environ['LSB_HOSTS'].split(' '))

    def getNodeCount(self):
        isShortHostnameSlotFormat, slots = self.__getLSBHosts()
        if isShortHostnameSlotFormat:
            return sum([int(y) for x, y in enumerate(slots) if x%2])
        else:
            return len(slots)

    def startNode(self, num, cmdargs):
        isShortHostnameSlotFormat, slots = self.__getLSBHosts()
        if isShortHostnameSlotFormat:
            slots = sum([[slots[x]]*int(slots[x+1]) for x, _ in enumerate(slots) if x%2 != 1], [])
        subprocess.check_call(['blaunch', slots[int(num)]] + cmdargs)

class SunGridEngineSiteCluster(SiteCluster):

    def __init__(self, use_argv=True):
        SiteCluster.__init__(self, use_argv=use_argv)

    def getQueues(self):
        cmd = ['qconf', '-sql']
        reAnsw = r'([a-zA-Z0-9_\.-]+)$'
        queueNames = []
        for s in [s.strip() for s in subprocess.check_output(cmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                queueNames.append(reMatch.group(1))
        return queueNames

    def submitJob(self, options, cmdargs):
        #  sub job start within job
        if options.startnode:
            self.startNode(options.startnode, cmdargs)
            return str(int(os.environ['JOB_ID']))

        submitCmd = ['qsub', '-V']
        # destination  queue of the job
        if options.queue:
            submitCmd += ['-q', options.queue]
        # name of the job
        if options.jobname:
            submitCmd += ['-N', options.jobname]
        # resources
        resources = []
        if options.nodes:
            # number of nodes to be reserved for the job.
            resources += ['nodes=%d'% options.nodes]
        if options.memory:
            # per-process maximum memory limit in bytes.
            resources += ['s_vmem=%s'% options.memory]
        if resources:
            submitCmd += ['-l', ':'.join(resources)]
        # list of email addresses to notify
        if options.email:
            submitCmd += ['-M', options.email]
            # email is sent by default on following events:
            #   a - when the job is aborted by the batch system.
            #   b - when the job begins execution.
            #   e - when the job terminates.
            submitCmd += ['-m', 'abe']
        # time after which the job is eligible for execution
        if options.attime:
            submitCmd += ['-a', options.attime]
        # time when the job should be finished
        if options.endtime:
            submitCmd += ['-dl', options.endtime]
        # dependency between other jobs
        if options.after:
            afterJobs = eval(options.after)
            if afterJobs != []:
                submitCmd += ['-W', 'depend=after:%s' % ":".join(afterJobs)]

        # project options for submit
        if options.project:
            submitCmd += ['-P', options.project]
        # group option for submit doesn't exist in SGE
        if options.group:
            submitCmd += ['-A', options.group]
        # custom arguments is an array 
        # TODO need to decide how to process arguments if duplicates are not allowed
        if options.customargs:
            customArgArray = []
            # just append when multiple customargs arguments existed
            for entry in options.customargs:
                customArgArray += shlex.split(entry, posix=False)
            submitCmd += customArgArray
        # the command to submit and its arguments
        submitCmd += cmdargs
        # perform the job submission
        res = ''
        reAnsw = r'[Yy]our job[ ]+([0-9]+).*'
        for s in [s for s in subprocess.check_output(submitCmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                res = str(reMatch.group(1))
        return res

    def __getQacctStatus(self, idOnCluster):
        cmdhist = ['qacct', '-j', idOnCluster]
        answUnk = "job id %s not found" % idOnCluster
        try:
            output = [s for s in subprocess.check_output(cmdhist, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()]
        except CalledProcessError as err:
            # LSF error code is always 255 so just look for string
            if answUnk in err.output:
                return "UNKNOWNID"
            raise

        for field in output:
            if 'exit_status' in field:
                return field.strip().split()[1]
        return "UNKNOWNID" # not found

    def getJobStatus(self, idOnCluster, addStatus=False):
        cmd = ['qstat']
        reAnsw = r'\s+{}\s+[\d\.]+\s+\S+\s+\S+\s+(\S+)\s+.*'.format(idOnCluster)
        rstate = ''
        for s in [s for s in subprocess.check_output(cmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                rstate = reMatch.group(1)
                break
        jobStatus = 'PENDING'
        if rstate == '':
            jobStatus = 'RUNNING'
            qacct_code = self.__getQacctStatus(str(idOnCluster))
            if qacct_code == "UNKNOWNID":
                return qacct_code
            if qacct_code == '0':
                if addStatus:
                    jobStatus = 'COMPLETED 0'
                else:
                    jobStatus = 'COMPLETED'
            else:
                if addStatus:
                    jobStatus = 'COMPLETED ' + qacct_code # non-zero exit status
                else:
                    jobStatus = 'COMPLETED'
        elif rstate == 'r':
            jobStatus = 'RUNNING'
        return jobStatus

    def killJob(self, idsOnCluster):
        cmd = ['qdel'] + [ str(x) for x in idsOnCluster ]
        try:
            output = subprocess.check_output(cmd, universal_newlines=True).splitlines()
        except CalledProcessError as e:
            output = e.output.splitlines()
        for jobId in idsOnCluster:
            res = ''
            for l in output:
                if str(jobId) in l:
                    res = l
                    break
            if not res:
                continue
            reAnsw = r'(has registered the job\s+{}\s+for deletion)'.format(jobId)
            reMatch = re.search(reAnsw, res)
            if reMatch:
                # job was already killed
                continue
            reAnsw = r'^(denied:)'
            reMatch = re.search(reAnsw, res)
            if reMatch:
                # job has already finished
                continue
            return 1
        return 0

    def __getPEHosts(self):
        if 'PE_HOSTFILE' in os.environ:
            # host, slot number pairs
            return os.environ['PE_HOSTFILE'].split(' ')
        return None

    def getNodeCount(self):
        slots = self.__getPEHosts()
        if slots:
            return sum([int(y) for x, y in enumerate(slots) if x%2])
        return 0

    def startNode(self, num, cmdargs):
        slots = self.__getPEHosts()
        if slots:
            slots = sum([[slots[x]]*int(slots[x+1]) for x, _ in enumerate(slots) if x%2 != 1], [])
        subprocess.check_call(['qrsh', '-inherit', slots[int(num)]] + cmdargs)


class SlurmSiteCluster(SiteCluster):
    def __init__(self, use_argv=True, ignore_user=True):
        SiteCluster.__init__(self, use_argv=use_argv, ignore_user=ignore_user)

    def getQueues(self):
        cmd = ['sinfo', '-s', '--noheader']
        reAnsw = r'\s*([a-zA-Z0-9_\.-]+)\*?'
        queueNames = []
        for s in [s.strip() for s in subprocess.check_output(cmd, universal_newlines=True).splitlines()]:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                queueNames.append(reMatch.group(1))
        return queueNames

    def submitJob(self, options, cmdargs):
        #  sub job start within job
        if hasattr(options, 'startnode') and options.startnode:
            self.startNode(options.startnode, cmdargs)
            return str(int(os.environ['PBS_JOBID']))

        submitCmd = ['sbatch', '-v'] #, '-W', 'umask=022']
        # destination  queue of the job
        if options.queue:
            submitCmd += ['--partition', options.queue]
        # name of the job
        if options.jobname:
            submitCmd += ['--job-name', options.jobname]
        # resources
        resources = []
        if options.nodes:
            # number of nodes to be reserved for the job.
            resources += ['--nodes={:d}'.format(options.nodes)]
        if options.threads:
            # the number of virtual processors/threads per node requested for this job
            resources += ['--cpus-per-task={}'.format(options.threads)]
        if options.memory:
            # maximum amount of physical memory used by any single process of the job
            resources += ['--mem={}'.format(options.memory)]
        if resources:
            submitCmd += ['-l', ':'.join(resources)]
        # list of email addresses to notify
        if options.email:
            submitCmd += ['--mail-user', options.email]
            # email is sent by default on following events:
            #   a - when the job is aborted by the batch system.
            #   b - when the job begins execution.
            #   e - when the job terminates.
            submitCmd += ['--mail-type', 'ALL']
        # time after which the job is eligible for execution
        if options.attime:
            submitCmd += ['--begin', options.attime]
        # time when the job should be finished
        if options.endtime:
            submitCmd += ['--deadline', options.endtime]
        # dependency between other jobs
        if options.after:
            afterJobs = eval(options.after)
            if afterJobs != []:
                submitCmd += ['--dependency=after:%s' % ":".join(afterJobs)]

        # submit as specific user (typically only allowed for administrators)
        if not self.ignore_user and options.user:
            submitCmd += ['--uid', options.user]

        # custom arguments
        if options.customargs:
            for customargs in options.customargs:
                submitCmd += shlex.split(customargs, posix=False)

        # the command to submit and its arguments
        if cmdargs:
            submitCmd += cmdargs

        # perform the job submission
        for line in subprocess.check_output(submitCmd, universal_newlines=True).splitlines():
            reMatch = re.match(r'Submitted batch job\s+([0-9]+).*', line.strip())
            if reMatch:
                return reMatch.group(1)
        return ''

    def getJobStatus(self, idOnCluster, addStatus=False):
        import re, subprocess
        cmd = ['squeue',  '--noheader', '-j', idOnCluster, '--Format=statecompact', ]
        try:
            # stderr=subprocess.STDOUT redirection is needed for getting the "Unknown Job Id" in err.output
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()
        except CalledProcessError as err:
            print(err.output, file=sys.stderr)
            # TODO PBS CODES need to be updated for Slurm
            if err.returncode == 153 or "Unknown Job Id" in err.output:
                return "UNKNOWNID"
            raise

        reAnsw = r'\s*statecompact\s*:\s*([ABCDEFGHILMNOPQRSTV]+)'
        rstate = ''
        for s in output:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                rstate = reMatch.group(1)
                break
        jobStatus = 'COMPLETED'
        exitStatus = '0'
        if rstate == '':
            jobStatus = 'COMPLETED'
        elif rstate in ['PD']:
            jobStatus = 'PENDING'
        elif rstate in ['R', 'SO', 'RS', 'CF', 'CG', 'SI', 'RQ'] :
            jobStatus = 'RUNNING'
        elif rstate in ['RH', 'RF', 'S', 'RD']:
            jobStatus = 'SUSPENDED'
        elif rstate == ['BF', 'CA', 'DL', 'F', 'NF', 'OOM', 'PR', 'TO', 'RQ', 'RV', 'SE', 'ST']:
            jobStatus = 'COMPLETED'
            #TODO refine for all possible error states
            exitStatus = 1

        if addStatus and jobStatus == 'COMPLETED':
            jobStatus += ' ' + exitStatus
        return jobStatus

    def killJob(self, idsOnCluster):
        cmd = ['scancel'] + idsOnCluster
        try:
            subprocess.check_output(cmd)
        except CalledProcessError:
            return 1
        return 0

    def getNodeCount(self):
        cmd = ["sinfo", "-N", "-o", "%N", "--noheader"]
        output = subprocess.check_output(cmd, universal_newlines=True)
        nodes = set(output.splitlines())
        return len(nodes)

    def startNode(self, num, cmdargs):
        # TODO check if this is correct way to do this
        subprocess.check_call(['srun', '-N1', str(int(num))] + cmdargs)


class ProcessSiteCluster(SiteCluster):
    """Sitecluster uses normal process execution on local host"""

    def __init__(self, use_argv=True, ignore_user=True):
        SiteCluster.__init__(self, use_argv=use_argv, ignore_user=ignore_user)

    def getQueues(self):
        """Return a dummy queue name: run_local_process"""
        return ["run_local_process"]

    def submitJob(self, options, cmdargs):
        """Submit implementated as standard process launch: returning pid of new process"""
        dir=os.getcwd()
        with tempfile.NamedTemporaryFile(dir=dir) as out, tempfile.NamedTemporaryFile(dir=dir) as err:
            proc = subprocess.Popen(cmdargs, stdout=out, stderr=err, preexec_fn=os.setpgrp, close_fds=True)
            stdout_f = "stdout.{}.txt".format(proc.pid)
            os.link(out.name, stdout_f)
            stderr_f = "stderr.{}.txt".format(proc.pid)
            os.link(err.name, stderr_f)
            os.chmod(stdout_f, os.stat(stdout_f).st_mode | stat.S_IRGRP | stat.S_IROTH )
            os.chmod(stderr_f, os.stat(stderr_f).st_mode | stat.S_IRGRP | stat.S_IROTH )
        return proc.pid

    def getJobStatus(self, idOnCluster, addStatus=False):
        """Return status of process exit state always 0 as we cannot know that for terminated process"""
        cmd = ['ps', '--no-headers', '-o', 'pid,state', '--pid', str(idOnCluster) ]
        try:
            # stderr=subprocess.STDOUT redirection is needed for getting the "Unknown Job Id" in err.output
            output = [s for s in subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True).splitlines()]
        except CalledProcessError as err:
            # process is terminated already
            output = err.output

        reAnsw = r'\s*{}\s*([DRSTtWXZ])'.format(idOnCluster)
        rstate = ''
        for s in output:
            reMatch = re.match(reAnsw, s)
            if reMatch:
                rstate = reMatch.group(1)
                break
        jobStatus = 'COMPLETED'
        exitStatus = '0'
        if rstate == '':
            jobStatus = 'COMPLETED'
        elif rstate in ['D', 'R', 'S'] :
            jobStatus = 'RUNNING'
        elif rstate in ['T', 't', 'Z']:
            jobStatus = 'SUSPENDED'
        elif rstate == ['X']:
            jobStatus = 'COMPLETED'
            exitStatus = 1

        if addStatus and jobStatus == 'COMPLETED':
            jobStatus += ' ' + exitStatus
        return jobStatus

    def killJob(self, idsOnCluster):
        """Kill processes in idsOnCluster list by sending SIGKILL to each of them"""
        for id in idsOnCluster:
            os.kill(int(id), signal.SIGKILL)
        return 0

    def getNodeCount(self):
        """Node count returns 1 as we only have local machine"""
        return 1

    def startNode(self, num, cmdargs):
        """Starts a local process and return process pid"""
        # TODO check if this is correct way to do this
        proc = subprocess.Popen(cmdargs, preexec_fn=os.setpgrp, close_fds=True)
        return proc.pid


if __name__ == '__main__':
    if 'SITE_CLUSTER_USE_PBS' in os.environ:
        PBSSiteCluster(ignore_user=True)
    elif 'SITE_CLUSTER_USE_LSF' in os.environ:
        LSFSiteCluster()
    elif 'SITE_CLUSTER_USE_SGE' in os.environ:
        SunGridEngineSiteCluster()
    elif 'SITE_CLUSTER_USE_SLURM' in os.environ:
        SlurmSiteCluster()
    elif 'SITE_CLUSTER_USE_SUBPROCESS' in os.environ:
        ProcessSiteCluster()
    else:
        print('ERROR: No sitecluster configuration enabled through a SITE_CLUSTER_USE_{PBS|LSF|SGE|SUBPROCESS} environment variable')
        SiteCluster()
