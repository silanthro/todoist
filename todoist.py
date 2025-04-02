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
    due_date: Optional[str] = None,
    priority: Literal[1, 2, 3, 4] = 1,
) -> str:
    """
    Create a new task in your Todoist

    Args:
    - title (str): Title of task
    - description (str): Description of task, defaults to empty string
    - due_date (Optional[str]): Task due date in YYYY-MM-DD format, defaults to None
    - priority (int): A priority level from 1 to 4, defaults to 1

    Returns:
        A string "Task added"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    API.add_task(
        content=title,
        description=description,
        due_date=due_date,
        priority=priority,
    )
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
    update_kwargs: dict,
) -> str:
    """
    Update a task

    Args:
    - task_id (str): Task ID to update
    - update_kwargs: A dictionary with the attributes to update, see below for accepted attributes
        - title (str): Update title of task e.g. {"title": "New title"}
        - description (str): Update description of task
        - due_date (str): Update due date of task with string as YYYY-MM-DD
        - labels (list[str]): Update task labels with list of strings
        - priority (int): Update task priority with an integer from 1 to 4, where 1 indicates highest priority

    Returns:
        A string "Task updated"
    """
    API = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
    # Rename "title" to "content"
    if "title" in update_kwargs:
        update_kwargs["content"] = update_kwargs["title"]
        del update_kwargs["title"]
    API.update_task(
        task_id=task_id,
        **update_kwargs,
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
