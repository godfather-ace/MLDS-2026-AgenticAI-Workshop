import os
import asyncio
import streamlit as st
from pydantic import BaseModel
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents import set_tracing_export_api_key

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Locally Deployed AI Agent")
st.title("Locally Deployed AI Research Agent")
st.write("This locally deployed AI agent assists in research queries.")

provider = st.sidebar.selectbox(
    "Select the LLM provider",
    ["OpenAI"]
)

openai_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password"
)

if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    set_tracing_export_api_key(openai_key)
else:
    st.warning("Please enter your OpenAI API Key in the sidebar.")
    st.stop()

# -----------------------------
# Output Schema
# -----------------------------
class ResearchOutput(BaseModel):
    is_research: bool
    reasoning: str


# -----------------------------
# Agents
# -----------------------------
guardrail_agent = Agent(
    name="Guardrail Check",
    instructions="Determine whether the user is asking a research-related question. "
                "Return is_research=True only if it is clearly research focused.",
    output_type=ResearchOutput
)

physics_research_agent = Agent(
    name="Physics Researcher",
    handoff_description="Specialist agent for Physics Research",
    instructions=(
        "You assist with Physics research. "
        "Explain reasoning step-by-step and provide relevant examples."
    )
)

financial_research_agent = Agent(
    name="Financial Researcher",
    handoff_description="Specialist agent for Financial Research",
    instructions=(
        "You assist with Financial research. "
        "Explain key events, frameworks, and context clearly."
    )
)

# -----------------------------
# Guardrail Function
# -----------------------------
async def research_guardrail(ctx, agent, input_data):
    result = await Runner.run(
        guardrail_agent,
        input_data,
        context=ctx.context
    )

    final_output = result.final_output_as(ResearchOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_research
    )


# -----------------------------
# Triage Agent
# -----------------------------
triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Decide whether the query relates to Physics or Financial research "
        "and route accordingly."
    ),
    handoffs=[physics_research_agent, financial_research_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=research_guardrail)
    ]
)

# -----------------------------
# Async Execution Wrapper
# -----------------------------
async def run_agent(user_query: str):
    result = await Runner.run(triage_agent, user_query)
    return result.final_output


# -----------------------------
# UI Execution
# -----------------------------
user_input = st.text_input("Enter your research query:")

if st.button("Submit"):

    if not user_input.strip():
        st.error("Please enter a valid research query.")
        st.stop()

    with st.spinner("Processing..."):
        response = asyncio.run(run_agent(user_input))

    st.success("Response:")
    st.write(response)