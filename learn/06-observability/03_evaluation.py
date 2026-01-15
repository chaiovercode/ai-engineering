"""
LangSmith Evaluation

Demonstrates:
- Creating datasets for evaluation
- Running evaluations with custom evaluators
- Built-in evaluators (correctness, helpfulness, etc.)
"""

import os
from dotenv import load_dotenv

load_dotenv()

from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LangSmith client
client = Client()

# Initialize the model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create the chain to evaluate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer questions concisely."),
    ("human", "{question}")
])
chain = prompt | llm | StrOutputParser()


def create_example_dataset():
    """Create a dataset for evaluation."""
    dataset_name = "qa-examples"

    # Check if dataset exists
    datasets = list(client.list_datasets(dataset_name=dataset_name))
    if datasets:
        print(f"Dataset '{dataset_name}' already exists")
        return dataset_name

    # Create dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Example Q&A pairs for evaluation"
    )

    # Add examples
    examples = [
        {
            "inputs": {"question": "What is the capital of France?"},
            "outputs": {"answer": "Paris"}
        },
        {
            "inputs": {"question": "What is 2 + 2?"},
            "outputs": {"answer": "4"}
        },
        {
            "inputs": {"question": "Who wrote Romeo and Juliet?"},
            "outputs": {"answer": "William Shakespeare"}
        }
    ]

    for example in examples:
        client.create_example(
            inputs=example["inputs"],
            outputs=example["outputs"],
            dataset_id=dataset.id
        )

    print(f"Created dataset '{dataset_name}' with {len(examples)} examples")
    return dataset_name


def target_function(inputs: dict) -> dict:
    """The function being evaluated."""
    response = chain.invoke({"question": inputs["question"]})
    return {"answer": response}


def run_evaluation():
    """Run evaluation on the dataset."""
    dataset_name = create_example_dataset()

    # Define evaluators
    evaluators = [
        LangChainStringEvaluator("qa"),  # Checks if answer is correct
        LangChainStringEvaluator("helpfulness"),  # Rates helpfulness
    ]

    # Run evaluation
    results = evaluate(
        target_function,
        data=dataset_name,
        evaluators=evaluators,
        experiment_prefix="qa-eval",
    )

    print("\n=== Evaluation Complete ===")
    print("Check LangSmith dashboard for detailed results")
    return results


if __name__ == "__main__":
    run_evaluation()
