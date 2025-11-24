"""
Sample Python file for testing CodeAudit
This file intentionally contains various code quality issues
"""

import os
import sys

# Bad practice: hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

def calculateSum(x, y):  # Bad: CamelCase for function
    """Calculate sum"""
    print("Calculating...")  # Bad: print statement
    result = x + y
    print(f"Result is {result}")
    return result

def complex_function(a, b, c, d, e):
    """This function is too complex"""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0

# Unused variables
unused_var = 100
another_unused = "test"

# SQL injection vulnerability
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection risk
    return query

# Missing error handling
def divide(x, y):
    return x / y  # No zero division check

class myClass:  # Bad: lowercase class name
    def __init__(self):
        self.value = 0
    
    def getValue(self):  # Bad: CamelCase method
        return self.value

# Main execution
if __name__ == "__main__":
    result = calculateSum(10, 20)
    print(f"Final result: {result}")
    
    obj = myClass()
    print(obj.getValue())
