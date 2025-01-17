import logging
import logging.config
import os

from automata.core.utils import (
    get_logging_config,
    get_root_fpath,
    get_root_py_fpath,
)
from automata.tasks.task_base import Task
from automata.tasks.task_error import TaskInstructionsError

logger = logging.getLogger(__name__)


# TODO - We should make it clearer which arguments are permissible for the task
# Note, this is a function of the task type.
class AutomataTask(Task):
    """A task that is to be executed by the TaskExecutor."""

    def __init__(self, *args, **kwargs):
        """
        Keyword Args:
            instructions (str): The instructions for the task.
            path_to_root_py (str): The path to the root python folder.
        """
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        if (
            "instructions" not in self.kwargs
            or self.kwargs["instructions"] == ""
        ):
            raise TaskInstructionsError("Task instructions cannot be empty.")
        self.instructions = self.kwargs["instructions"]
        self.record_conversation = self.kwargs.get("record_conversation", True)

        # Note, this  assumes the python folder is in the root folder
        default_python_folder = os.path.relpath(
            get_root_py_fpath(), get_root_fpath()
        )
        self.path_to_root_py = kwargs.get(
            "path_to_root_py", default_python_folder
        )

    def initialize_logging(self) -> None:
        """
        Initializes logging for the task by creating a log file in the task directory.
        If the task directory does not exist, it is created.
        """

        log_dir = self._get_log_dir()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(
            log_dir,
            Task.TASK_LOG_NAME.replace("SESSION_ID", str(self.session_id)),
        )
        log_level = (
            logging.DEBUG if self.kwargs.get("verbose") else logging.INFO
        )
        logging.config.dictConfig(
            get_logging_config(log_level=log_level, log_file=log_file)
        )
        logging.debug("Logging initialized.")

    def get_logs(self) -> str:
        """Gets the logs for the task."""

        log_dir = self._get_log_dir()
        log_file = os.path.join(
            log_dir,
            Task.TASK_LOG_NAME.replace("SESSION_ID", str(self.session_id)),
        )

        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Log file {log_file} not found.")
        with open(log_file, "r") as f:
            log_content = f.read()
        return log_content
