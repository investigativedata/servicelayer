from unittest import TestCase

from servicelayer.cache import get_fakeredis
from servicelayer.process import Job, JobOp, RateLimit, Progress


class ProcessTest(TestCase):

    def test_job_queue(self):
        conn = get_fakeredis()
        ds = 'test_1'
        job_id = 'job_1'
        job_op = JobOp(conn, JobOp.OP_INGEST, job_id, ds)
        status = job_op.progress.get()
        assert status['pending'] == 0
        assert status['finished'] == 0
        assert job_op.is_done()
        job_op.queue_task({'test': 'foo'}, {})
        status = job_op.progress.get()
        assert status['pending'] == 1
        assert status['finished'] == 0
        assert not job_op.is_done()
        task = JobOp.get_operation_task(conn, JobOp.OP_INGEST, timeout=None)
        nq, payload, context = task
        assert nq.dataset == job_op.dataset
        assert payload['test'] == 'foo'
        status = job_op.progress.get()
        assert status['pending'] == 1
        assert status['finished'] == 0
        job_op.queue_task({'test': 'bar'}, {})
        status = job_op.progress.get()
        assert status['pending'] == 2
        assert status['finished'] == 0
        job_op.task_done()
        status = job_op.progress.get()
        assert status['pending'] == 1
        assert status['finished'] == 1
        job_op.task_done()
        assert Progress.get_dataset_job_ids(conn, ds) == []
        status = job_op.progress.get()
        assert status['pending'] == 0
        assert status['finished'] == 0
        task = JobOp.get_operation_task(conn, JobOp.OP_INGEST, timeout=1)
        nq, payload, context = task
        assert payload is None

    def test_queue_clear(self):
        conn = get_fakeredis()
        ds = 'test_1'
        job_id = 'job_1'
        job_op = JobOp(conn, JobOp.OP_INGEST, job_id, ds)
        job_op.queue_task({'test': 'foo'}, {})
        status = job_op.progress.get()
        assert status['pending'] == 1
        Job.remove_dataset(conn, ds)
        status = job_op.progress.get()
        assert status['pending'] == 0
        assert Progress.get_dataset_job_ids(conn, ds) == []

    def test_fetch_multiple_task(self):
        conn = get_fakeredis()
        ds = 'test_1'
        job_id = 'job_1'
        job_op = JobOp(conn, JobOp.OP_INGEST, job_id, ds)
        job_op.queue_task({'test': 'foo'}, {})
        job_op.queue_task({'test': 'bar'}, {})
        status = job_op.progress.get()
        assert status['pending'] == 2
        tasks = list(job_op.get_tasks(limit=5))
        assert len(tasks) == 2
        for task in tasks:
            assert len(task) == 3
            assert isinstance(task[0], JobOp)
        assert tasks[0][1] == {'test': 'foo'}
        assert tasks[1][1] == {'test': 'bar'}
        Job.remove_dataset(conn, ds)

    def test_progress(self):
        conn = get_fakeredis()
        ds = 'test_2'
        job_id = 'job_2'
        progress = Progress(conn, JobOp.OP_INGEST, job_id, ds)
        status = progress.get()
        assert status['pending'] == 0
        assert status['finished'] == 0
        progress.mark_pending()
        status = progress.get()
        assert status['pending'] == 1
        assert status['finished'] == 0
        full = Progress.get_dataset_status(conn, ds)
        assert full['pending'] == 1
        job_status = Progress.get_job_status(conn, ds, job_id)
        assert job_status['pending'] == 1
        progress.mark_finished()
        status = progress.get()
        assert status['pending'] == 0
        assert status['finished'] == 1
        job_status = Progress.get_job_status(conn, ds, job_id)
        assert job_status['pending'] == 0
        assert job_status['finished'] == 1
        progress.remove()
        status = progress.get()
        assert status['finished'] == 0

    def test_rate(self):
        conn = get_fakeredis()
        limit = RateLimit(conn, 'banana', limit=10)
        assert limit.check()
        limit.update()
        assert limit.check()
        for i in range(13):
            limit.update()
        assert not limit.check()
