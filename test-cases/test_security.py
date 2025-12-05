import os
import pickle

def dangerous_code():
    user_input = input("Enter code: ")
    eval(user_input)
    
    with open("data.pkl", "rb") as f:
        data = pickle.loads(f.read())
    
    command = input("Enter command: ")
    os.system(command)