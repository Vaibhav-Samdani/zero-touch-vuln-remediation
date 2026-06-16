# import asyncio
# import random
# import json
# import operator
# import aiosqlite
# from typing import TypedDict, Optional, Annotated

# from langgraph.graph import StateGraph, START, END, MessagesState
# from langgraph.types import interrupt
# from langgraph.config import RunnableConfig
# from langgraph.prebuilt import ToolNode

# from langchain_core.tools import tool
# from langchain_core.messages import AIMessage
# from langchain_openai import ChatOpenAI

# # --- MOCK LLM SETUP ---
# class MockChatOpenAI:
#     """A dummy LLM that bypasses OpenAI and returns structured mock data."""
#     def __init__(self, *args, **kwargs):
#         self.schema = None
#         self.include_raw = False

#     def bind_tools(self, tools, *args, **kwargs):
#         return self

#     def with_structured_output(self, schema, include_raw=False, *args, **kwargs):
#         self.schema = schema
#         self.include_raw = include_raw
#         return self

#     async def ainvoke(self, messages, *args, **kwargs):
#         if self.schema:
#             if self.schema.__name__ == "RemediationOutput":
#                 parsed_data = self.schema(
#                     script_content="#!/bin/bash\n\necho 'Mock remediation applied successfully!'\nexit 0",
#                     branch_name="fix/mock-vulnerability-123",
#                     fix_summary="Mocked security patch generated for local testing."
#                 )
#             elif self.schema.__name__ == "GitWorkflowOutput":
#                 parsed_data = self.schema(
#                     pr_url="https://github.com/mock-org/mock-repo/pull/12",
#                     pr_number=12 
#                 )
#             else:
#                 parsed_data = None

#             raw_msg = AIMessage(content="Mock structured output generated.")
#             if self.include_raw:
#                 return {"raw": raw_msg, "parsed": parsed_data}
#             return parsed_data

#         return AIMessage(content="[MOCK LLM] Operation bypassed successfully.")

# @tool
# def mock_github_action(action: str) -> str:
#     """A dummy tool to bypass MCP initialization during local testing."""
#     return f"Simulated action: {action}"

# # --- INITIALIZATION ---
# tools = None
# git_llm = None
# tool_node = None
# git_branch_llm = None
# remediation_llm = None

# async def initialize_agent_components():
#     """Bypasses live GitHub MCP connection for local UI/Webhook testing."""
#     global tools, git_llm, tool_node, git_branch_llm, remediation_llm

#     if all(x is not None for x in [tools, git_llm, tool_node]):
#         return

#     print("\n[SYSTEM] ⚠️ WARNING: Booting TEMPORARY mock agent components.")
#     print("[SYSTEM] Bypassing live GitHub MCP connection...")

#     tools = [mock_github_action]
#     remediation_workflow_tools = tools

#     git_llm = MockChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(remediation_workflow_tools)
#     tool_node = ToolNode(remediation_workflow_tools, handle_tool_errors=True)
#     git_branch_llm = MockChatOpenAI(model="gpt-4o-mini", temperature=0)
#     remediation_llm = MockChatOpenAI(model="gpt-4o-mini", temperature=0)

#     print("[SYSTEM] ✅ Temporary components loaded successfully. Graph ready to compile.\n")


# # --- STATE SCHEMA ---
# class AgentState(MessagesState):
#     issue_description: Optional[str]
#     repo_owner: Optional[str]
#     repo_name: Optional[str]
#     target_file: Optional[str]
#     vuln_id: Optional[str]
#     log_message: Optional[str]
#     ci_status: Optional[str]
#     pr_number: Optional[int]
#     pr_merged: Optional[bool]
#     pr_state: Optional[str]
#     active_execution_time: Annotated[float, operator.add]
#     total_cost: Annotated[float, operator.add]
#     input_tokens: Annotated[int, operator.add]


# # --- MOCKED NODES ---
# async def generate_remediation_script(state: AgentState):
#     await asyncio.sleep(1.5)
#     print(state)
#     return {"log_message": "[AGENT] 🧠 Generating bash remediation script..."}

# async def create_prompt(state: AgentState):
#     await asyncio.sleep(1)
#     return {"log_message": "[AGENT] 🛠️ Formulating Git patch payload..."}

# async def github_workflow(state: AgentState):
#     await asyncio.sleep(2)
#     return {"log_message": "[GIT] 🚀 Pushing code changes to remote repository..."}

# async def extract_pr_details(state: AgentState, config: RunnableConfig):
#     await asyncio.sleep(1)
#     pr_num = 12 # Hardcoded for webhook testing
    
#     # CRITICAL: We must map the mock PR number to the thread_id so the webhook can find it!
#     async with aiosqlite.connect("state_db.sqlite") as db:
#         await db.execute(
#             "INSERT OR REPLACE INTO pr_mappings (pr_number, thread_id) VALUES (?, ?)",
#             (pr_num, config["configurable"]["thread_id"])
#         )
#         await db.commit()

#     return {
#         "log_message": f"[SYSTEM] 🔑 Pull Request generated and mapped. (PR #{pr_num})",
#         "pr_number": pr_num
#     }

# async def check_ci_status(state: AgentState):
#     await asyncio.sleep(2)
#     return {"ci_status": "success", "log_message": "[CI/CD] 🧪 Monitoring live pipeline status... PASSED"}

# async def fetch_and_delete_error_logs(state: AgentState):
#     return {"log_message": "[AWS S3] 📥 Fetching failed CI/CD execution logs..."}

# async def open_for_resume_request(state: AgentState):
#     await asyncio.sleep(1)
#     return {"log_message": "[SYSTEM] ✅ Updating PR with wait status..."}

# async def wait_for_human_approval(state: AgentState):
#     pr_number = state.get("pr_number", 12)
    
#     print(f"\n[AGENT] 💤 Entering standby state. Awaiting Human Peer Review or merge action on PR #{pr_number}...")
    
#     resume_data = interrupt({"info": "Waiting for human review...", "pr_number": pr_number})
    
#     if isinstance(resume_data, dict) and "pr_merged" in resume_data:
#         print("[SYSTEM] Webhook decision received. Bypassing live GitHub API verification.")
#         return {
#             "pr_merged": resume_data["pr_merged"], 
#             "pr_state": resume_data.get("pr_state", "closed")
#         }
    
#     # Fallback if no specific data was injected
#     return {"pr_merged": False, "pr_state": "open"}

# async def fetch_pr_feedback(state: AgentState):
#     await asyncio.sleep(1)
#     return {"log_message": "[AGENT] 🔄 Waking up. Fetching human peer review feedback..."}

# async def calculate_tokens_and_cost_consumption(state: AgentState):
#     await asyncio.sleep(1)
#     return {
#         "total_cost": round(random.uniform(1.0, 5.0), 2),
#         "input_tokens": random.randint(1500, 5000),
#         "log_message": "[SYSTEM] 🎉 Workflow Complete. Vulnerability Mitigated."
#     }

# # --- ROUTING LOGIC ---
# def route_after_ci(state: AgentState):
#     if state.get("ci_status") == "success":
#         return "open_for_resume_request"
#     return "fetch_and_delete_error_logs"

# def route_after_human_decision(state: AgentState):
#     if state.get("pr_merged") or state.get("pr_state") == "closed":
#         return "calculate_tokens_and_cost_consumption"
#     return "fetch_pr_feedback"

# # --- GRAPH BUILDER ---
# async def build_graph(checkpointer):
#     workflow = StateGraph(AgentState)
    
#     workflow.add_node("generate_remediation_script", generate_remediation_script)
#     workflow.add_node("create_prompt", create_prompt)
#     workflow.add_node("github_workflow", github_workflow)
#     workflow.add_node("extract_pr_details", extract_pr_details)
#     workflow.add_node("check_ci_status", check_ci_status)
#     workflow.add_node("fetch_and_delete_error_logs", fetch_and_delete_error_logs)
#     workflow.add_node("open_for_resume_request", open_for_resume_request)
#     workflow.add_node("wait_for_human_approval", wait_for_human_approval)
#     workflow.add_node("fetch_pr_feedback", fetch_pr_feedback)
#     workflow.add_node("calculate_tokens_and_cost_consumption", calculate_tokens_and_cost_consumption)

#     workflow.add_edge(START, "generate_remediation_script")
#     workflow.add_edge("generate_remediation_script", "create_prompt")
#     workflow.add_edge("create_prompt", "github_workflow")
#     workflow.add_edge("github_workflow", "extract_pr_details") 
#     workflow.add_edge("extract_pr_details", "check_ci_status")
    
#     workflow.add_conditional_edges("check_ci_status", route_after_ci, {
#         "fetch_and_delete_error_logs": "fetch_and_delete_error_logs",
#         "open_for_resume_request": "open_for_resume_request"
#     })
    
#     workflow.add_edge("fetch_and_delete_error_logs", "generate_remediation_script")
#     workflow.add_edge("open_for_resume_request", "wait_for_human_approval")
    
#     workflow.add_conditional_edges("wait_for_human_approval", route_after_human_decision, {
#         "calculate_tokens_and_cost_consumption": "calculate_tokens_and_cost_consumption",
#         "fetch_pr_feedback": "fetch_pr_feedback"
#     })
    
#     workflow.add_edge("fetch_pr_feedback", "generate_remediation_script")
#     workflow.add_edge("calculate_tokens_and_cost_consumption", END)

#     return workflow.compile(checkpointer=checkpointer)








