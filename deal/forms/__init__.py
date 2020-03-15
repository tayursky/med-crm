from .comment import DealCommentForm
from .deal import DealForm, DealPersonForm
from .expense import ExpenseForm, DealExpenseForm
from .online import OnlineDealForm, OnlineDealPersonForm
from .task import DealTaskForm

__all__ = [
    'DealForm',
    'DealPersonForm',
    'DealCommentForm',
    'DealTaskForm',
    'ExpenseForm', 'DealExpenseForm',
    'OnlineDealForm',
    'OnlineDealPersonForm'
]
