# LangGraph Explained: The Relay Race

Imagine you are organizing a relay race. To make it work, you need three things:
1.  **Runners** (Nodes) who do the work.
2.  **A Baton** (State) that carries the message.
3.  **A Track** (Edges) that tells runners where to go next.

LangGraph is just a tool that helps us organize this race for computer programs.

---

## 1. The Core Concepts

### The State (The Baton)
In a relay race, the baton is the *only* thing that connects one runner to the next. It holds the "proof" that the previous runners finished their job.

In LangGraph, the **State** is like a shared clipboard or a baton.
-   It holds all the current information (messages, data, errors).
-   Every "Runner" (Node) takes the clipboard, reads what's on it, maybe adds a note, and passes it on.

### Nodes (The Runners)
Nodes are the people in the race. They actually *do* something.
-   One node might be "The Researcher" (searches the web).
-   Another node might be "The Writer" (summarizes the search).
-   Each node receives the **State** (the baton), does its job, updates the State, and stops.

### Edges (The Track)
Nodes don't know who comes next automatically. The **Edges** are the lines painted on the track. They connect Runner A to Runner B.
-   **Normal Edge**: "After Runner A finishes, go to Runner B."
-   **Conditional Edge**: "If Runner A is tired, go to the Bench; otherwise, go to Runner B."

---

## 2. The Dictionary (The Rulebook)

When passing notes (State), we need to agree on how to write them.

### Normal Dictionary (Scrap Paper)
Imagine writing on a napkin. You can write anything, anywhere.
```python
movie = {"name": "Avengers", "year": 2019}
```
-   **Pros**: Fast, easy.
-   **Cons**: Messy. What if someone writes "Year" instead of "year"? The next person won't understand.

### Typed Dictionary (Official Form)
This is like a government form with boxes. You *must* write the name in the "Name" box and the date in the "Year" box.
```python
class Movie(TypedDict):
    name: str  # Must be text
    year: int  # Must be a number
```
-   **Pros**: Safe. Everyone knows exactly where to look for information.
-   **Cons**: Takes a few seconds longer to set up.

---

## 3. Advanced Moves

### Conditional Edges (The Traffic Cop)
Sometimes the path isn't a straight line.
-   "If the email is angry, send it to Customer Support."
-   "If the email is happy, send it to the Thank You Bot."

This logic lives in a **Conditional Edge**. It looks at the State and decides which Node runs next.

### Tools (The Backpack)
Sometimes a runner needs help (a calculator, a map, a phone).
-   **Nodes** are the runners.
-   **Tools** are the unexpected items they pull out of their backpack to get the job done (like `search_google` or `calculate_sum`).

---

![Runner Diagram](assets/coreconcepts.png)

## 4. The Big Picture

When you put it all together, you get a **Graph**.
It is simply a map of:
1.  **Start** here.
2.  Pass the **State** to this **Node**.
3.  Follow the **Edge** to the next Node.
4.  Repeat until you hit **End**.

*Simple to understand, complex in power.*
