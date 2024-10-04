# Contributing to url-snapshotter

Thank you for your interest in contributing to `url-snapshotter`! Contributions of all kinds are welcome: bug reports, feature requests, code improvements, documentation enhancements, and more. Below are the guidelines to help you contribute effectively.

## Table of Contents
- [Contributing to url-snapshotter](#contributing-to-url-snapshotter)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Code of Conduct](#code-of-conduct)
  - [How to Contribute](#how-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Enhancements](#suggesting-enhancements)
    - [Pull Requests](#pull-requests)
  - [Coding Standards](#coding-standards)

## Getting Started

1. **Fork the Repository**: First, fork the repository to your GitHub account.
2. **Clone Your Fork**: Clone your fork locally to work on it.

   ```bash
   git clone git@github.com:vvdaal/url-snaphotter.git
   cd url-snaphotter
   ```

3. **Set Up the Development Environment**: Follow the instructions in the `README.md` to install the necessary tools and dependencies using `pyenv` and `Poetry`.

## Code of Conduct

We expect all contributors to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please make sure to read it before contributing.

## How to Contribute

### Reporting Bugs

If you find a bug in `url-snapshotter`, we would love to hear about it!

- **Check Existing Issues**: Before reporting, check if the issue already exists.
- **Open a New Issue**: If it doesn’t exist, create a new issue with a detailed description of the problem, including steps to reproduce it.

### Suggesting Enhancements

Do you have an idea for a feature or an improvement? Great! We welcome suggestions that make `url-snapshotter` more useful.

- **Open a Feature Request**: Create an issue and label it as a feature request. Provide as much context as possible to help us understand your idea.

### Pull Requests

We love pull requests! If you'd like to make a code change:

1. **Branching**: Make sure you are working on your fork. Create a new branch for your contribution.

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Work on Your Change**: Write your code, following the coding standards outlined below. Make sure to include relevant tests.

3. **Commit Your Changes**: Make sure your commit messages are descriptive and use the following format:

4. **Submit a Pull Request**: When you’re ready, push your changes and submit a pull request to the main repository. Please include a detailed description of your changes.

## Coding Standards

- **Python Version**: We use Python 3.12+.
- **PEP 8**: Adhere to PEP 8 standards. Use `black` for formatting your code.
  - **Docstrings**: When writing a docstring, make sure there is a blank newline after it.
- **Type Hints**: Use type hints for better readability. Use native Python 3.12 type annotations instead of importing from `typing`.
- **Testing**: Write tests for your changes. We use `pytest` for testing. Make sure all tests pass before submitting your pull request.
- **Logging**: Use `setup_logger()` from `url_snapshotter.logger_utils` for logging, ensuring consistent and useful log messages.

We appreciate any contribution to `url-snapshotter`!
