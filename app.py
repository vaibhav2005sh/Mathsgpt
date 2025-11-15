"""
Requirements (add to requirements.txt):
streamlit
langchain
langchain-groq
wikipedia
python-dotenv
sympy
#Vking

Run:
pip install -r requirements.txt
streamlit run Maths.py
"""
import os
import traceback
import streamlit as st
from dotenv import load_dotenv

# load .env if present
load_dotenv()

try:
    from langchain_groq import ChatGroq
except Exception:
    try:
        from langchain.chat_models import ChatGroq  # noqa
    except Exception:
        ChatGroq = None

try:
    from langchain.callbacks.streamlit import StreamlitCallbackHandler
except Exception:
    try:
        from langchain.callbacks import StreamlitCallbackHandler
    except Exception:
        StreamlitCallbackHandler = None

try:
    from langchain.utilities import WikipediaAPIWrapper as WikiWrapper
except Exception:
    try:
        from langchain.tools import WikipediaAPIWrapper as WikiWrapper
    except Exception:
        WikiWrapper = None

try:
    from langchain.agents import Tool
except Exception:
    try:
        from langchain.tools import Tool
    except Exception:
        Tool = None

try:
    from langchain.agents import initialize_agent, AgentType
except Exception:
    initialize_agent = None
    AgentType = None

try:
    from langchain.chains.llm_math import LLMMathChain
except Exception:
    LLMMathChain = None

# sympy for local symbolic math
try:
    from sympy import sympify, Eq, solve, SympifyError
except Exception:
    sympify = None
    Eq = None
    solve = None
    SympifyError = None

# ---------------------------
# Helper: safe wikipedia wrapper
# ---------------------------
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as ReqConnError


def safe_wiki_search(query: str):
    """Safe wrapper around Wikipedia lookups. Returns a short summary or a friendly fallback message.
    The wrapper never raises network exceptions; it returns a string so the agent can continue.
    """
    try:
        if WikiWrapper is not None:
            # langchain wrapper; call its run() method
            try:
                return WikiWrapper().run(query)
            except Exception as e:
                # fallthrough to wikipedia package if possible
                pass

        # fallback: use wikipedia package if available
        import wikipedia
        wikipedia.set_lang("en")
        results = wikipedia.search(query, results=3)
        if not results:
            return "No Wikipedia results found."
        summary = wikipedia.summary(results[0], sentences=2)
        return summary

    except (Timeout, ReqConnError, RequestException) as e:
        return f"Wikipedia lookup failed (network issue): {e}. Proceeding without external wiki."
    except Exception as e:
        # generic catch: return message rather than raising
        return f"Wikipedia lookup not available or failed: {e}. Proceeding without external wiki."

# ---------------------------
# SymPy solver (local math)
# ---------------------------

def sympy_solver(expr_str: str):
    """Try to solve algebraic equations or evaluate expressions using SymPy.
    Returns a human-friendly string result or a parse error message.
    """
    if sympify is None:
        return "SymPy not installed or not available."

    try:
        s = expr_str.strip()
        # normalize common input forms
        s = s.replace('^', '**')

        # if looks like an equation, split and solve
        if "=" in s or s.lower().startswith("solve"):
            # allow inputs like 'solve x^2-5x+6=0' or 'x^2-5x+6=0'
            if s.lower().startswith("solve"):
                s = s.split(None, 1)[1] if len(s.split()) > 1 else s
            if "=" in s:
                left, right = s.split("=", 1)
                left_expr = sympify(left)
                right_expr = sympify(right)
                eq = Eq(left_expr, right_expr)
            else:
                # assume expression = 0
                eq = Eq(sympify(s), 0)
            sol = solve(eq)
            return f"Solution: {sol}"
        else:
            # try to simplify or evaluate
            val = sympify(s)
            try:
                return f"Result: {val.evalf()}"
            except Exception:
                return f"Simplified: {val}"
    except SympifyError as e:
        return f"SymPy could not parse the expression: {e}"
    except Exception as e:
        return f"SymPy error: {e}"

# ---------------------------
# Streamlit UI and config
# ---------------------------
st.set_page_config(page_title="MathsGPT", layout="wide")
st.title("MathsGPT — Streamlit + LangChain + Groq (patched)")

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Configuration")
    groq_key = st.text_input(
        "GROQ API Key (or set GROQ_API_KEY env var)",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
    )
    # default to a currently supported model (change if you prefer another)
    model_name_input = st.text_input("Model name", value="llama-3.3-70b-versatile")
    show_verbose = st.checkbox("Verbose agent logs", value=False)
    show_traces = st.checkbox("Show tracebacks on error (dev only)", value=False)

with col2:
    st.header("Chat / Question")
    default_example = (
        "Sarah has twice as many apples as Tom. If Tom has 5 apples and they buy 6 more apples each, "
        "how many apples do they have together now?"
    )
    question = st.text_area("Enter your question", value=default_example, height=140)

# ---------------------------
# Initialize LLM (ChatGroq) with fallbacks
# ---------------------------
groq_api_key = groq_key or os.getenv("GROQ_API_KEY", None)
if not groq_api_key:
    st.error("GROQ API key is required. Set GROQ_API_KEY env var or enter it above.")
    st.stop()

if ChatGroq is None:
    st.error("ChatGroq client not found. Make sure `langchain-groq` (or compatible package) is installed.")
    st.stop()

# create llm instance with flexible arg names
llm = None
try:
    llm = ChatGroq(model=model_name_input, groq_api_key=groq_api_key)
except TypeError:
    try:
        llm = ChatGroq(model_name=model_name_input, groq_api_key=groq_api_key)
    except Exception as e:
        st.error(f"Failed to construct ChatGroq client: {e}")
        st.stop()
except Exception as e:
    st.error(f"Failed to construct ChatGroq client: {e}")
    st.stop()

st.success("ChatGroq client initialized.")

# ---------------------------
# Build tools (Wikipedia safe wrapper, SymPy)
# ---------------------------
tools = []

if Tool is not None:
    tools.append(
        Tool(
            name="Wikipedia",
            func=safe_wiki_search,
            description="Search Wikipedia (safe wrapper). Returns fallback message on network errors.",
        )
    )

    # add SymPy tool if sympy is available
    if sympify is not None:
        tools.append(
            Tool(
                name="SymPy",
                func=sympy_solver,
                description="Solve algebraic equations and evaluate expressions locally using SymPy.",
            )
        )

# optional: LLMMathChain if available
math_chain = None
if LLMMathChain is not None:
    try:
        math_chain = LLMMathChain(llm=llm, verbose=False)
        if Tool is not None:
            tools.append(
                Tool(
                    name="Calculator",
                    func=math_chain.run,
                    description="Performs multi-step math calculations using the LLM.",
                )
            )
    except Exception:
        pass

# ---------------------------
# Initialize agent (if available and we have tools)
# ---------------------------
agent = None
if initialize_agent is not None and tools:
    try:
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=show_verbose,
        )
        st.success("Agent initialized with tools.")
    except Exception as e:
        st.warning(f"Failed to initialize agent: {e}. Falling back to direct LLM usage.")
        agent = None
else:
    if initialize_agent is None:
        st.info("LangChain agents initialize_agent() not available; will use direct LLM call.")
    elif not tools:
        st.info("No tools available to create an agent; will use direct LLM call.")

# ---------------------------
# Chat session state
# ---------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi — I'm MathsGPT. Ask me a math or knowledge question!"}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# ---------------------------
# Main execution with SymPy-first pre-check
# ---------------------------
run_button = st.button("Find my answer")

if run_button:
    q = question.strip()
    if not q:
        st.warning("Please enter a question.")
    else:
        # append user message once
        st.session_state["messages"].append({"role": "user", "content": q})
        st.chat_message("user").write(q)

        st_cb = None
        if StreamlitCallbackHandler is not None:
            try:
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            except Exception:
                st_cb = None

        # Prefer SymPy for algebraic/equation-like queries
        response = None
        try:
            is_likely_algebra = any(k in q.lower() for k in ["solve", "=", "x", "**", "^", "sqrt", "factor", "root"])
            if is_likely_algebra and sympify is not None:
                try:
                    sympy_out = sympy_solver(q)
                    # if sympy returns a parse/solution message, accept it
                    if sympy_out and not sympy_out.lower().startswith("sympy could not parse"):
                        response = sympy_out
                except Exception:
                    response = None

            # If SymPy didn't answer, use agent/llm
            if response is None:
                try:
                    with st.spinner("Generating response..."):
                        if agent is not None:
                            response = agent.run(q, callbacks=[st_cb]) if st_cb else agent.run(q)
                        else:
                            # fallback to llm direct calls
                            if hasattr(llm, "generate"):
                                try:
                                    out = llm.generate([{"role": "user", "content": q}])
                                    response = None
                                    if hasattr(out, "generations"):
                                        gens = out.generations
                                        if gens and len(gens) and len(gens[0]) and hasattr(gens[0][0], "text"):
                                            response = gens[0][0].text
                                    if response is None:
                                        response = str(out)
                                except Exception:
                                    out = llm.generate([q])
                                    response = str(out)
                            elif hasattr(llm, "predict"):
                                response = llm.predict(q)
                            elif callable(llm):
                                response = llm(q)
                            else:
                                raise RuntimeError("LLM does not expose a known call method. Update client code.")
                except Exception as e:
                    # handle decommissioned-model or other API errors
                    err_text = str(e)
                    if "model_decommissioned" in err_text or "has been decommissioned" in err_text or "decommission" in err_text:
                        st.error(
                            "The model you requested appears to have been decommissioned by the provider.\n\n"
                            "Change the model name in the sidebar to a supported model (e.g. 'llama-3.3-70b-versatile')\n"
                            "or check provider docs for current models."
                        )
                        response = f"Agent/LLM run failed: {err_text}"
                    else:
                        response = f"Agent/LLM run failed: {err_text}"
                        if show_traces:
                            with st.expander("Show error details (traceback)"):
                                st.text(traceback.format_exc())

        except Exception as outer_e:
            # catch-any to avoid crashing the app
            response = f"Unexpected error during processing: {outer_e}"
            if show_traces:
                with st.expander("Show error details (traceback)"):
                    st.text(traceback.format_exc())

        # append assistant response once and display
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

        st.markdown("### Response")
        st.success(response)
