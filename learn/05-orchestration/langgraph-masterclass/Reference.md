# Python Quick Reference

---

## Type Hints

**Union** - "This can be either A or B"
```python
def process(value: Union[str, int]) -> str:
    return str(value)
```

**Optional** - "This might be empty"
```python
def greet(name: Optional[str] = None) -> str:
    return f"Hello, {name}" if name else "Hello"
```

**Any** - "I don't care what type this is"
```python
def log(data: Any) -> None:
    print(data)
```

**Literal** - "Only these exact values are allowed"
```python
def set_status(status: Literal["pending", "approved"]) -> None:
    print(status)
```

---

## Data Structures

**TypedDict** - "A dictionary with a specific shape"
```python
class User(TypedDict):
    name: str
    age: int

user: User = {"name": "Alice", "age": 30}
```

**Dataclass** - "A class that holds data without boilerplate"
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    active: bool = True

user = User("Alice", 30)
```

**Dataclass with Options**
```python
@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080
    debug: bool = field(default=False)
```

---

## Functions

**Lambda** - "A quick throwaway function"
```python
square = lambda x: x * x
add = lambda a, b: a + b
sorted(users, key=lambda u: u["age"])
```

---

## Decorators

**Decorator** - "Wrap a function to add extra behavior"
```python
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logger
def say_hello():
    print("Hello!")
```

**Decorator with Arguments** - "A customizable wrapper"
```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hi!")
```

**Built-in Decorators**
```python
@staticmethod   # "Belongs to class, doesn't need instance"
@classmethod    # "Gets the class itself, not an instance"
@property       # "Call a method like it's a variable"
```

---

## Async/Await

**Async** - "Do something without blocking everything else"
```python
async def fetch_data():
    await asyncio.sleep(1)
    return "data"

result = asyncio.run(fetch_data())
```

**Gather** - "Run multiple things at the same time"
```python
results = await asyncio.gather(task1(), task2(), task3())
```

**Async Context Manager** - "Open something, use it, close it automatically"
```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()
```
