# Coding Style Guide for the **url-snapshotter** Project

This style guide outlines the coding standards and best practices for the **url-snapshotter** project. Adhering to these guidelines will ensure code consistency, readability, and maintainability across the project.

---

## General Formatting

- **Code Formatter**: Use [Black](https://black.readthedocs.io/en/stable/) for code formatting with default settings. Black enforces a consistent code style and handles line lengths, indentation, and other formatting concerns automatically.

- **Line Length**: Although Black handles line lengths, aim to keep lines under 88 characters when possible for better readability.

- **Blank Lines**:
  - Include a blank line after each long comment or docstring to separate it from the following code.
  - Use blank lines to separate logical sections of code within functions for clarity.

## File Structure

- **File Header**:
  - Each Python file should start with a comment indicating its path and filename.
    ```python
    # path/to_filename.py
    ```
  - Follow this with a blank line and a comment describing the purpose of the file.
    ```python
    # This module provides the functionality to do awesome things.
    ```

## Comments and Docstrings

- **Comments**:
  - Use comments liberally to explain complex logic, assumptions, and important details.
  - Ensure comments are clear, concise, and add value to the code.
  - Comments should be in English and use proper grammar and punctuation.

- **Docstrings**:
  - Every function, class, and module should have a docstring describing its purpose and usage.
  - Use triple double-quotes `"""` for docstrings.
  - Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstring conventions.

### Docstring Structure

- **Functions and Methods**:
  - **Short Summary**: Begin with a concise summary of the function's purpose.
  - **Args**: List and describe each argument.
  - **Returns**: Describe the return value(s).
  - **Raises**: List any exceptions the function might raise.
  - **Example** (optional): Provide usage examples if helpful.

  ```python
  def example_function(param1, param2):
      """
      Brief description of the function.

      Args:
          param1 (Type): Description of param1.
          param2 (Type): Description of param2.

      Returns:
          ReturnType: Description of the return value.

      Raises:
          ExceptionType: Description of the exception.

      Example:
          >>> example_function(value1, value2)
          Expected output
      """

      # Rest of the functions code here
  ```

- **Classes**:
  - Include a docstring immediately after the class definition.
  - Describe the class's purpose and any important details.

  ```python
  class ExampleClass:
      """
      Description of the class.

      Attributes:
          attribute1 (Type): Description of attribute1.
          attribute2 (Type): Description of attribute2.
      """

      # Your class implementation
  ```

- **Modules**:
  - At the top of each module, include a docstring summarizing its purpose and functionality.

## Naming Conventions

- **Variables and Functions**:
  - Use lowercase letters with words separated by underscores (`snake_case`).
  - Choose meaningful and descriptive names that convey the purpose of the variable or function.

- **Classes**:
  - Use `CamelCase` for class names.
  - Class names should be nouns that describe the object's purpose.

- **Constants**:
  - Use uppercase letters with words separated by underscores (`ALL_CAPS`).
  - Define constants at the module level.

## Import Statements

- **Ordering**:
  - Group imports in the following order:
    1. Standard library imports
    2. Related third-party imports
    3. Local application/library-specific imports

P.S. If you use `black` for formatting, it takes care of this ordering.

- **Formatting**:
  - Use absolute imports whenever possible.
  - Place each import on a separate line.
  - Avoid wildcard imports (`from module import *`).

  ```python
  # Standard library imports
  import os
  import sys

  # Third-party imports
  from sqlalchemy import create_engine, Column, Integer, String
  from rich.console import Console

  # Local imports
  from url_snapshotter.db_utils import DatabaseManager
  ```

## Error Handling and Exceptions

- Use try-except blocks to handle exceptions gracefully.
- Catch specific exceptions rather than using a bare `except`.
- Log exceptions with meaningful messages to aid in debugging.
- Avoid suppressing exceptions unless necessary.

## Logging

- **Logger Configuration**:
  - Use the centralized logging configuration (`logging_config.py`) to manage logging across the project.
  - Configure loggers to output messages at appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).

- **Usage**:
  - Import the logger using:
    ```python
    import logging
    logger = logging.getLogger("url_snapshotter")
    ```
  - Use the logger to record events, errors, and debug information.
  - Include enough context in log messages to make them informative.

- **Examples**:
  ```python
  logger.debug("Debugging information about variable state.")
  logger.info("General information about program execution.")
  logger.warning("An unexpected event that is not necessarily an error.")
  logger.error("An error occurred while processing the request.")
  logger.exception("An exception occurred.", exc_info=True)
  ```

## Type Annotations

- Use type annotations to indicate the expected types of function arguments and return values.
- For built-in types, use the type directly without importing from `typing`.
  - **Correct**:
    ```python
    def add_numbers(a: int, b: int) -> int:
        return a + b
    ```
  - **Avoid** importing from `typing` for basic types in Python 3.12.

## Asynchronous Programming

- When using asynchronous functions, clearly indicate them with the `async` keyword.
- Use `await` when calling asynchronous functions.
- Handle exceptions within asynchronous functions appropriately.

## Security Practices

- **Input Validation**:
  - Validate user inputs to prevent injection attacks and unexpected behavior.
  - Sanitize file paths, URLs, and other external inputs.

- **Error Messages**:
  - Avoid revealing sensitive information in error messages or logs.
  - Provide user-friendly error messages without exposing internal details.

## Code Organization

- **Modules**:
  - Group related functions and classes into modules.
  - Keep modules focused on a single responsibility.

- **Packages**:
  - Organize modules into packages for better structure.
  - Include an `__init__.py` file in each package directory.

## Testing

Note: This is a work in progress and this project could definitely use more tests!

- Write unit tests for functions and classes.
- Use a testing framework like `unittest` or `pytest`.
- Ensure tests cover various scenarios, including edge cases and error conditions.

## Version Control

- Commit code frequently with clear and descriptive commit messages.
- Follow a consistent branching strategy (e.g., `your-awesome-patch`, `feature/*`).
- Code reviews are required

## Example File Template

```python
# path/to_filename.py

# This module provides the functionality to do awesome things.

import os
import logging

from rich.console import Console

console = Console()
logger = logging.getLogger("url_snapshotter")

def example_function(param1, param2):
    """
    Brief description of the function.

    Args:
        param1 (Type): Description of param1.
        param2 (Type): Description of param2.

    Returns:
        ReturnType: Description of the return value.

    Raises:
        ExceptionType: Description of the exception.
    """

    # Function implementation

    # Additional comments explaining complex logic

    return result
```
