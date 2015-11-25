import gc3libs


def format_stats_data(stats):
    '''
    For each task state (and pseudo-state like ``ok`` or
    ``failed``), two values are returned: the count of managed
    tasks that were in that state when `Engine.progress()` was
    last run, and what percentage of the total managed tasks this
    is.

    Parameters
    ----------
    stats: gc3libs.core.Engine
        as returned by :py:meth:`gc3libs.core.Engine.stats()`

    Returns
    -------
    dict
        global statistics about the jobs in the :py:class:`Engine`
    '''
    data = {}
    tot = stats['total']
    for state, count in stats.items():
        data['count_' + state.lower()] = count
        data['percent_' + state.lower()] = 100.0 * count / max(tot, 1)
    return data


def get_task_data(task):
    '''
    Provide the following data for each task and recursively for each
    subtask (until `monitoring_depth` is reached) in form of a mapping:

        * "name" (*str*): name of task
        * "state" (*g3clibs.Run.State*): state of the task
        * "is_live" (*bool*): whether the task is currently processed
        * "is_done" (*bool*): whether the task is done
        * "failed" (*bool*): whether the task failed, i.e. terminated
          unsuccessfully
        * "percent_done" (*float*): percent of subtasks that are done

    Parameters
    ----------
    task: gc3libs.workflow.TaskCollection or gc3libs.Task
        submitted GC3Pie task that should be monitored

    Returns
    -------
    dict
        information for each task and its subtasks
    '''
    def get_info(task_, i):
        is_live_states = {
            gc3libs.Run.State.SUBMITTED,
            gc3libs.Run.State.RUNNING,
            gc3libs.Run.State.STOPPED
        }
        is_done = task_.execution.state == gc3libs.Run.State.TERMINATED
        failed = task_.execution.exitcode != 0
        data = {
            'id': str(task_),
            'name': task_.jobname,
            'state': task_.execution.state,
            'is_live': task_.execution.state in is_live_states,
            'is_done': is_done,
            'failed': is_done and failed,
            'percent_done': 0.0  # fix later, if possible
        }

        done = 0.0
        if isinstance(task_, gc3libs.workflow.TaskCollection):
            for child in task_.tasks:
                if (child.execution.state == gc3libs.Run.State.TERMINATED):
                    done += 1
            if len(task_.tasks) > 0:
                data['percent_done'] = done / len(task_.tasks) * 100
            else:
                data['percent_done'] = 0
        elif isinstance(task_, gc3libs.Task):
            # For an individual task it is difficult to estimate to which
            # extent the task has been completed. For simplicity and
            # consistency, we just set "percent_done" to 100% once the job
            # is TERMINATED and 0% otherwise
            if task_.execution.state == gc3libs.Run.State.TERMINATED:
                data['percent_done'] = 100
        else:
            raise NotImplementedError(
                "Unhandled task class %r" % (task_.__class__))

        if isinstance(task_, gc3libs.workflow.TaskCollection):
            data['subtasks'] = [get_info(t, i+1) for t in task_.tasks]

        return data

    return get_info(task, 0)