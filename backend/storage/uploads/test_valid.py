"""
A simple calculator module.
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

if __name__ == "__main__":
    result = add(5, 3)
    print(f"Result: {result}")