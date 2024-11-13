import sys


def error_message_detail(error, error_detail: sys):
    """
    Method Name : error_message_detail
    Description : Format and return an error message with traceback details.
    Return : str
    Args  :
        error (Exception): The error object or message.
        error_detail (sys): The traceback information from the error.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = "Error occurred in python script name [{0}] at line number [{1}]. Error message: {2}".format(
        file_name, exc_tb.tb_lineno, str(error)
    )
    return error_message


class FineTuningException(Exception):
    """
    Custom exception class for handling fine-tuning related errors.
    Captures detailed error information including file name and line number.
    """

    def __init__(self, error_message, error_detail: sys):
        """
        Initialize the FineTuningException with detailed error information.

        Args:
            error_message (str): The main error message
            error_detail (sys): System information for error tracking

        Example:
            try:
                # Some fine-tuning code
                raise ValueError("Model checkpoint not found")
            except Exception as e:
                raise FineTuningException(e, sys) from e
        """
        self.error_message = error_message_detail(error_message, error_detail)
        super().__init__(self.error_message)

    def __str__(self):
        """
        Return the string representation of the error.

        Returns:
            str: Formatted error message with details
        """
        return self.error_message


class ModelLoadException(FineTuningException):
    """
    Exception raised for errors during model loading.
    """
    pass


class DataPreprocessException(FineTuningException):
    """
    Exception raised for errors during data preprocessing.
    """
    pass


class TrainingException(FineTuningException):
    """
    Exception raised for errors during model training.
    """
    pass


class ValidationException(FineTuningException):
    """
    Exception raised for errors during model validation.
    """
    pass


class ConfigurationException(FineTuningException):
    """
    Exception raised for errors in configuration settings.
    """
    pass