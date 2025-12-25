# Graphs

---

## 1. [Graph 1: Hello World](graph1_hello_world.ipynb)
**Main Goal:** Learn how to handle a single node.

### Objectives
*   Understand and define the `AgentState` structure.
*   Create simple node functions to process and update state.
*   Set up a basic LangGraph structure.
*   Compile and invoke a LangGraph graph.
*   Understand how data flows through a single node.

[**Go to Exercise 1**](exercises/exercise_graph1.ipynb)

---

## 2. [Graph 2: Multiple Inputs](graph2_multiple_inputs.ipynb)
**Main Goal:** Learn how to handle multiple inputs.

### Objectives
*   Define a more complex `AgentState`.
*   Create a processing node that performs operations on list data.
*   Set up a LangGraph that processes and outputs computed results.
*   Invoke the graph with structured inputs and retrieve outputs.

[**Go to Exercise 2**](exercises/exercise_graph2.ipynb)

--- 

## 3. [Graph 3: Sequential Graph](graph3_sequential.ipynb)
**Main Goal:** Create and handle multiple nodes.

### Objectives
*   Create multiple nodes that sequentially process and update different parts of the state.
*   Connect nodes together in a graph.
*   Invoke the graph and see how the state is transformed step-by-step.

[**Go to Exercise 3**](exercises/exercise_graph3.ipynb)

---

## 4. [Graph 4: Conditional Graph](graph4_conditional_graph.ipynb)
**Main Goal:** Use `add_conditional_edge` to control graph flow.

### Objectives
*   Implement conditional logic to route the flow of data to different nodes.
*   Use `START` and `END` nodes to manage entry and exit points.
*   Design multiple nodes to perform different operations.
*   Create a router node to handle decision making and control graph flow.

[**Go to Exercise 4**](exercises/exercise_graph4.ipynb)
