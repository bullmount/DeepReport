from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display


class State(TypedDict):
    input: str
    user_feedback: str


def step_1(state):
    print("---Step 1---")
    pass


def human_feedback(state):
    print("---human_feedback---")
    feedback = interrupt({'question':"vuoi continuare (s o n)?"})
    return {"user_feedback": feedback}

def should_continue(state):
    feedback = state["user_feedback"]
    if feedback == "s":
        return "step_1"
    else:
        return "step_2"

def step_2(state):
    print("---Step 2---")
    pass


builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_2", step_2)

builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")

builder.add_conditional_edges(
    "human_feedback",
    should_continue,
)
builder.add_edge("step_2", END)

# Set up memory
memory = MemorySaver()

# Add
graph = builder.compile(checkpointer=memory)

# View
display(Image(graph.get_graph().draw_mermaid_png()))
graph.get_graph().draw_mermaid_png(output_file_path="test_human_in_the_loop.png")

# Input
initial_input = {"input": "hello world"}

# Thread
thread = {"configurable": {"thread_id": "1"}}

# res = graph.invoke(initial_input, config=thread, stream_mode="updates")
# print (res)
# hres = input("ciao")
# res = graph.invoke(Command(resume=hres), config=thread)
# print (res)

inputv = initial_input

while True:
    # Run the graph until the first interruption
    for event in graph.stream(inputv, thread, stream_mode="updates"):
        print(f"EVENT: {event}")
        if '__interrupt__' in event:
            interrupt_value = event['__interrupt__'][0].value
            hres = input(event['__interrupt__'][0].value['question'])
            inputv = Command(resume=hres)
        # print(graph.get_state(thread).next)
        # print("\n")
    if graph.get_state(thread).next == ():
        break

