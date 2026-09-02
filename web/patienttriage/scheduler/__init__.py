"""
Dynamic Priority Scheduler Module for PatientTriage.ai
Continuous Max Heap queue management with sub-linear logarithmic time decay and surge mitigation.
"""

from patienttriage.scheduler.scoring import compute_priority_score
from patienttriage.scheduler.max_heap import DynamicMaxHeapQueue, PatientQueueEntry

__all__ = ["compute_priority_score", "DynamicMaxHeapQueue", "PatientQueueEntry"]

