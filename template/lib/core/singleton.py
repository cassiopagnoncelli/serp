def singleton(cls):
  instances = {}
  def wrapper(*args, **kwargs):
    if cls not in instances:
      instances[cls] = cls(*args, **kwargs)
    return instances[cls]
  return wrapper

# # Example

# @singleton
# class MySingleton:
#   x = random.randint(0, 100)
#   def __init__(self):
#     print("Init!")

# # Usage
# a = MySingleton()
# b = MySingleton()
# print(a is b)  # True
# a.x
# b.x
