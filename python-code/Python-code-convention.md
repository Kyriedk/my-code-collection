# development guide

## code convention

Please use python type hint when writing classes or functions, Type hint will make our coding much easier.

[python-style-guide](https://google.github.io/styleguide/pyguide.html)

## static code check

### code quality

Mypy is a static type checker for Python.

Type checkers help ensure that you're using variables and functions in your code
correctly. With mypy, add type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/))
to your Python programs, and mypy will warn you when you use those types
incorrectly.

Python is a dynamic language, so usually you'll only see errors in your code
when you attempt to run it. Mypy is a *static* checker, so it finds bugs
in your programs without even running them!

Here is a small example:

```python
number = input("What is your favourite number?")
print("It is", number + 1)  # error: Unsupported operand types for + ("str" and "int")
```

for python file check, it's very easy, just use the command ``python file_name.py`.

### code style

Our code must conform with PEP8 standards, so before committing, the code has to
be checked against various standards. We recommend using pre-commit tool to
auto-check your code before commit, it can not only check codes but also
correct some minor formatting errors without manual intervention. The steps below
show how to use this tool.

1. make sure your coding environment has python and pip installed.

2. using command `pip install pre-commit`, **this step requires internet access**

3. using command `pre-commit install`

4. submit commits then it will automatically initialize and check your code.
**the first time to use pre-commit needs internet access**

5. revise your code util all examinations pass
