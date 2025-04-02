import os
import re
from typing import Literal, Optional, TypedDict

from todoist_api_python.api import TodoistAPI


class Task(TypedDict):
    id: str
    title: str
    description: str
    labels: list[str]
    priority: int
    due_date: str
    created_at: str


def create_task(
    title: str,
    description: str = "",
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Literal[1, 2, 3, 4] = 1,
) -> str:
    """
    Create a new task in your Todoist

    Args:
    - title (str): Title of task
    - description (str): Description of task, defaults to empty string
    - due_string (Optional[str]): Task due date in natural language e.g. "today", "tomorrow", defaults to None
    - due_date (Optional[str]): Task due date in YYYY-MM-DD format, defaults to None, ignored if due_string is provided
    - priority (int): A priority level from 1 to 4, defaults to 1

    Returns:
        A string "Task added"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    kwargs = {
        "content": title,
        "description": description,
        "priority": priority,
    }
    if due_date is not None:
        kwargs["due_date"] = due_date
    if due_string is not None:
        if "due_date" in kwargs:
            del kwargs["due_date"]
        kwargs["due_string"] = due_string
    API.add_task(**kwargs)
    return "Task added"


def get_tasks(
    project_id: Optional[str] = None,
    search_query: Optional[str] = None,
    due_date_filter: Optional[str] = None,
    priority: list[Literal[1, 2, 3, 4]] = [1, 2, 3, 4],
    other_filters: Optional[str] = None,
    limit: int = 10,
) -> list[Task]:
    """
    Retrieves a list of tasks

    Args:
    - project_id (Optional[str]): Project ID to retrieve tasks for, defaults to None
    - search_query (Optional[str]): Search for tasks that contain this query string, defaults to None
    - due_date_filter (Optional[str]): Filter tasks by due date, see accepted formats below, defaults to None
        - Formatted date string (e.g. 2025-12-31)
        - Natural language (e.g. "today", "tomorrow", "Friday")
        - Before or after a date using "due before:" or "due after:" prefixes (e.g. "due before: today" or "due after: today")
    - priority (list[int]): List of priorities to filter by, defaults to [1,2,3,4]
    - other_filters (Optional[str]): Other filters to apply, see examples below, defaults to None
        - Labels: indicated with a "@" prefix
        - Projects: indicated with a "#" prefix
        - Accepted operators:
            - |: OR e.g. "#Work | #School"
            - &: AND e.g. "@chore & @shopping"
            - !: NOT e.g. "!#Work"
            - (): parentheses indicating query order e.g. "(#Work | #School) & @chore"
            - \\: Escape character for operators or to denote spaces in label or project names e.g. "#Shopping\\ list"
    - limit (int): Max number of tasks to retrieve, defaults to 10

    Returns:
        List of tasks
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    filters = []
    if search_query:
        re.sub(re.compile("[|&!()\\s]"), lambda m: "\\" + m.group(), search_query)
        filters.append(f"search: {search_query}")
    if due_date_filter:
        filters.append(due_date_filter)
    if priority:
        filters.append("(" + "|".join(f"p{p}" for p in priority) + ")")
    if other_filters:
        filters.append(other_filters)
    tasks = API.get_tasks(
        project_id=project_id,
        filter="&".join(filters) if filters else None,
    )
    return [
        {
            "id": task.id,
            "title": task.content,
            "description": task.description,
            "labels": task.labels,
            "priority": task.priority,
            "due_date": task.due.date if task.due else None,
            "created_at": task.created_at,
        }
        for task in tasks[:limit]
    ]


def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    labels: Optional[list[str]] = None,
    priority: Optional[Literal[1, 2, 3, 4]] = None,
) -> str:
    """
    Update a task

    Args:
    - task_id (str): Task ID to update
    - title (Optional[str]): Use this to update the task title
    - description (Optional[str]): Use this to update the task description
    - due_string (Optional[str]): Task due date in natural language e.g. "today", "tomorrow", defaults to None
    - due_date (Optional[str]): Task due date in YYYY-MM-DD format, defaults to None, ignored if due_string is provided
    - labels (Optional[list[str]]): Use this to update the task labels with list of strings
    - priority (Optional[Literal[1,2,3,4]]): Use this to update the task priority with an integer from 1 to 4, where 1 indicates highest priority

    Returns:
        A string "Task updated"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    kwargs = {}
    if title is not None:
        kwargs["content"] = title
    if description is not None:
        kwargs["description"] = description
    if labels is not None:
        kwargs["labels"] = labels
    if priority is not None:
        kwargs["priority"] = priority

    if due_date is not None:
        kwargs["due_date"] = due_date
    if due_string is not None:
        if "due_date" in kwargs:
            del kwargs["due_date"]
        kwargs["due_string"] = due_string
    API.update_task(
        task_id=task_id,
        **kwargs,
    )
    return "Task updated"


def complete_task(task_id: str) -> str:
    """
    Mark a task as completed

    Args:
    - task_id (str): Task ID to complete

    Returns:
        A string "Task completed"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    API.close_task(task_id)
    return "Task completed"


def delete_task(task_id: str):
    """
    Delete a task

    Args:
    - task_id (str): Task ID to delete

    Returns:
        A string "Task deleted"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    API.delete_task(task_id)
    return "Task deleted"
