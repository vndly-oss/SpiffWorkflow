# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import os
import sys
import unittest

from SpiffWorkflow.operators import Attrib, Equal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Join, WorkflowSpec, Simple, ExclusiveChoice
from SpiffWorkflow import Workflow, Task


class JoinTest(TaskSpecTest):
    CORRELATE = Join

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']

        return Join(self.wf_spec,
                    'testtask',
                    description='foo')

    def setup_workflow(self, structured=True):
        wf_spec = WorkflowSpec()
        split = Simple(wf_spec, 'split')
        wf_spec.start.connect(split)

        if structured:
            join = Join(wf_spec, 'join', split_task=split.name)
        else:
            join = Join(wf_spec, 'join')

        single = Simple(wf_spec, 'first')
        default = Simple(wf_spec, 'default')
        choice = ExclusiveChoice(wf_spec, 'choice', manual=True)
        end = Simple(wf_spec, 'end')

        single.connect(join)
        join_condition = Equal(Attrib('should_join'), True)
        choice.connect_if(join_condition, join)
        choice.connect(default)

        split.connect(single)
        split.connect(choice)
        join.connect(end)

        workflow = Workflow(wf_spec)
        return workflow

    def test_join_complete_status_structured(self):
        """ Test that a join is not considered complete if the all the tasks
        are complete AND they were completed with the correct condition to
        satisfy the join"""

        workflow = self.setup_workflow()

        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('split')[0].id)
        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('first')[0].id)
        # Complete the choice task but set the data to match the join condition
        choice_task = workflow.get_tasks_from_spec_name('choice')[0]
        choice_task.set_data(should_join=True)
        workflow.complete_task_from_id(choice_task.id)

        # Join should be in completed state
        self.assertEqual(Task.COMPLETED,
                         workflow.get_tasks_from_spec_name('join')[0].state)

    def test_join_complete_status_unstructured(self):
        """ Test that a join is not considered complete if the all the tasks
            are complete AND they were completed with the correct condition to
            satisfy the join"""

        workflow = self.setup_workflow(structured=False)

        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('split')[0].id)
        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('first')[0].id)
        # Complete the choice task but set the data to match the join condition
        choice_task = workflow.get_tasks_from_spec_name('choice')[0]
        choice_task.set_data(should_join=True)
        workflow.complete_task_from_id(choice_task.id)

        # Join should be in completed state
        self.assertEqual(Task.COMPLETED,
                         workflow.get_tasks_from_spec_name('join')[0].state)

    def test_join_conditional_not_ready_status_structured(self):
        """ Test that a join is not considered complete if the all the tasks
            are complete AND they were completed with the correct condition to
            satisfy the join"""

        workflow = self.setup_workflow()

        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('split')[0].id)
        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('first')[0].id)
        choice_task = workflow.get_tasks_from_spec_name('choice')[0]

        workflow.complete_task_from_id(choice_task.id)

        # Join should be in waiting state NOT completed
        self.assertEqual(Task.WAITING,
                         workflow.get_tasks_from_spec_name('join')[
                             0].state)

    def test_join_conditional_not_ready_status_unstructured(self):
        """ Test that a join is not considered complete if the all the tasks
            are complete AND they were completed with the correct condition to
            satisfy the join"""

        workflow = self.setup_workflow(structured=False)

        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('split')[0].id)
        workflow.complete_task_from_id(
            workflow.get_tasks_from_spec_name('first')[0].id)
        choice_task = workflow.get_tasks_from_spec_name('choice')[0]

        workflow.complete_task_from_id(choice_task.id)

        # Join should be in waiting state NOT completed
        self.assertEqual(Task.WAITING,
                         workflow.get_tasks_from_spec_name('join')[
                             0].state)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(JoinTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
