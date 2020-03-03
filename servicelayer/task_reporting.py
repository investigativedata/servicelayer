from datetime import datetime

from normality import stringify

from servicelayer.jobs import Task
from servicelayer.settings import WORKER_REPORTING_DISABLED
from servicelayer.util import dump_json


OP_REPORT = 'report'


class Status:
    START = 'start'
    END = 'end'
    ERROR = 'error'


class TaskReporter:
    def __init__(
            self,
            conn,
            task=None,
            job=None,
            stage=None,
            dataset=None,
            status=None,
            clean_payload=None,
            **defaults):
        self.conn = conn
        self.task = task
        self.job = job
        self.stage = stage
        self.dataset = dataset
        self.status = status
        self.clean_payload = clean_payload
        self.defaults = defaults
        self.reporting_enabled = not WORKER_REPORTING_DISABLED

    def start(self, **data):
        self.handle(status=Status.START, **data)

    def end(self, **data):
        self.handle(status=Status.END, **data)

    def error(self, exception, **data):
        self.handle(status=Status.ERROR, exception=exception, **data)

    def get_report_data(self, job, status, stage, dataset, dump=None, **extra):
        now = datetime.now()
        exception = extra.pop('exception', None)
        data = {**self.defaults, **{
            'job': job,
            'updated_at': now,
            '%s_at' % status: now,
            'stage': stage,
            'status': status,
            'dataset': dataset,
            'original_dump': dump
        }, **extra}
        if exception:
            data.update({
                'status': 'error',
                'has_error': True,
                'error_name': exception.__class__.__name__,
                'error_msg': stringify(exception)
            })
        if self.clean_payload:
            return self.clean_payload(data)
        return data

    def handle(self, **data):
        if self.reporting_enabled:
            if self.task:
                self._handle_task(self.task, **data)
            else:
                self._handle_data(self.stage, self.dataset, self.job, **data)

    def _handle_task(self, task, **extra):
        """queue a new reporting task based on given `task`"""
        status = extra.pop('status')
        stage = extra.pop('stage', None)
        payload = self.get_report_data(
            job=task.job.id,
            status=status,
            stage=stage or task.stage.stage,
            dataset=task.job.dataset.name,
            dump=task.serialize(),
            **extra
        )
        stage = task.job.get_stage(OP_REPORT)
        stage.queue(payload)

    def _handle_data(self, stage, dataset, job, **data):
        """queue a new reporting task based on `data`"""
        task = Task.unpack(self.conn, dump_json({
            'stage': stage,
            'dataset': dataset,
            'job': job
        }))
        self._handle_task(task, **data)

    def from_task(self, task):
        return TaskReporter(conn=self.conn, task=task)

    def copy(self, **data):
        """return a new reporter with updated data"""
        base = {
            'task': self.task,
            'job': self.job,
            'stage': self.stage,
            'dataset': self.dataset,
            'status': self.status,
            'clean_payload': self.clean_payload
        }
        return TaskReporter(self.conn, **{**base, **self.defaults, **data})
