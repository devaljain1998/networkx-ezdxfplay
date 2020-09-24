# Take input
name = input("What is your name? ")
print('Input', name)

# slice
course = 'Python'
print('Slice', course[1:3])

# Multiline strings
multiline = """Hello
What's up?
I'm Naman"""
print('Multiline', multiline)

# Formatted Strings, use "", not ''
age = 23
message = f"Hi, my name is {name} and age is {age}"
print('Formatted Strings', message)

# Assignment augmented operator
age += 10
print('Assignment augmented operator', age)

# Use type of exceptions
try:
    age = int(input('Age: '))
    income = 20000
    risk = income / age
    print(age)
except ValueError:
    print('ValueError', 'Not a valid number')
except ZeroDivisionError:
    print('ZeroDivisionError', 'Age cannot be 0')


class ClassName(object):
    """docstring for ClassName"""

    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg


class Person(object):
    # Class - Capital start letter
    # parent class

    # __init__ is known as the constructor
    def __init__(self, name, idnumber):
        self.name = name
        self.idnumber = idnumber

    def display(self):
        print(self.name)
        print(self.idnumber)


class Employee(Person):
    # child class

    def __init__(self, name, idnumber, salary, post, manager):
        self.salary = salary
        self.post = post
        self.manager = manager
        # invoking the __init__ of the parent class
        Person.__init__(self, name, idnumber)

        print('Access variable of parent class', self.name)
        print('Access function of parent class:')
        self.display()

    def __str__(self):
        return f'Employee {self.salary} {self.post}'


# creation of an object variable or an instance
a = Employee('Rahul', 886012, 2000, 'CEO', None)
a.post = "CTO"  # change the variable in object

b = Employee('Arjun', 886012, 2000, 'Tech', a)

# objects to json - serialize
import json
json_dump1 = json.dumps(a.__dict__, indent=4)
print('json_dump', type(json_dump1), json_dump1)  # str

json_dump2 = json.dumps(b.__dict__, default=lambda o: o.__dict__, indent=4)
print('json_dump', type(json_dump2), json_dump2)  # str

# Save as .json
with open('data.json', 'w') as f:
    json.dump(json_dump2, f)

# Read from .json
with open('data.json', 'r') as openfile:
    json_object = json.load(openfile)
print(json_object, type(json_object), json_object)

# objects from json - deserialize
# TO DO
x = json.loads(json_dump2)
print(type(x), x)

exit()
# calling a function of the class Person using its instance
a.display()

# Use str() to define class string
print('str()', str(a))  # If same funnction name, child's function is called

# Packages - A package is a directory with __init__.py in it. It can
# contain one or more modules.
print('Use packages and modules')


def args_func(arg1, *argv):
    # *args for variable number of arguments
    print('arg1', arg1)
    for arg in argv:
        print('arg in *args', arg)


args_func('Hello', 'Welcome', 'to', 'GeeksforGeeks')


def kwargs_func(arg1, **kwargs):
    # *kwargs for keyworded variable number of arguments
    for key, value in kwargs.items():
        print("%s == %s" % (key, value))


kwargs_func("Hi", first='Geeks', mid='for', last='Geeks')

import math
# All the modules, variables and functions that are defined in a module
content = dir(math)
print(content)

# Dictionary containing the class's namespace
print('__dict__ Person', Person.__dict__)
print('__dict__ Employee', Employee.__dict__)


class Vector:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return 'Vector (%d, %d)' % (self.a, self.b)

    def __add__(self, other):
        return Vector(self.a + other.a, self.b + other.b)


v1 = Vector(2, 10)
v2 = Vector(5, -2)
print(v1 + v2)  # Operator Overloading

# Logging
import logging

# Use  only following 3 - No info and debug
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
