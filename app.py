import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

# --- 1. MODELS ---

class ProjectRisk(BaseModel):
    category: str = Field(description="Risk category (e.g., Technical, Financial, Timeline)")
    description: str = Field(description="Detailed professional explanation")
    mitigation: str = Field(description="Suggested strategy to handle this risk")
    severity: str = Field(description="Low, Medium, or High")

class ProjectPlan(BaseModel):
    summary: Optional[str] = Field(None, description="Senior-level executive summary of project goals")
    scope_included: Optional[List[str]] = Field(None, description="Detailed list of deliverables (In-Scope)")
    scope_excluded: Optional[List[str]] = Field(None, description="Explicit boundaries (Out-of-Scope)")
    missing_information: Optional[List[str]] = Field(None, description="Critical data gaps needed for estimation")
    risks: Optional[List[ProjectRisk]] = Field(None, description="Ruthless audit of project red flags")
    suggested_questions: Optional[List[str]] = Field(None, description="Strategic questions for the client")

# --- 2. ENGINE (Multi-Prompt Chaining) ---

class FlowixEngine:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.parser = JsonOutputParser(pydantic_object=ProjectPlan)
        
    def _run_expert_step(self, persona: str, instruction: str, message: str, context: str = "") -> str:
        """Helper to run a specialized AI step."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"PERSONA: {persona}\nGOAL: {instruction}"),
            ("user", f"Context: {context}\nClient Message: {message}")
        ])
        return (prompt | self.llm).invoke({"context": context, "message": message}).content

    def generate_plan(self, client_message: str, mode: str) -> ProjectPlan:
        # Get the schema instructions for the AI
        format_instructions = self.parser.get_format_instructions()
        
        # --- MULTIPLE PROMPTS LOGIC ---
        
        # Step 1: Architect Step (Always run to understand intent)
        architect_summary = self._run_expert_step(
            "Senior Technical Architect",
            "Decode the messy message. Identify the hidden technical requirements and core business goals.",
            client_message
        )

        # Step 2: Specialized Mode Execution
        if mode == "Full":
            # Multi-prompt Chain for Full Analysis
            audit_report = self._run_expert_step(
                "Risk Auditor",
                "Review the Architect's summary and the raw message. Identify all risks and missing info.",
                client_message,
                context=architect_summary
            )
            
            final_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are the Lead Project Manager. Consolidate the Architect's findings and the Auditor's report.
                Create a high-fidelity, professional project plan. 
                {format_instructions}"""),
                ("user", f"Architecture: {architect_summary}\nAudit: {audit_report}\nRaw: {client_message}")
            ])
            
        else:
            # Targeted Single Expert Prompts
            modes = {
                "Summary": ("Business Strategist", "Focus purely on decoding intent and business value."),
                "Scope": ("Systems Engineer", "Define strict technical boundaries (In-Scope vs Out-of-Scope)."),
                "Risks": ("Hard-nosed Auditor", "Ruthlessly identify every possible technical and financial risk."),
                "Gaps": ("Requirements Engineer", "List every missing detail needed for a fixed-price quote."),
                "Questions": ("Client Relationship Manager", "Draft high-level, strategic questions.")
            }
            persona, instr = modes.get(mode, modes["Summary"])
            final_prompt = ChatPromptTemplate.from_messages([
                ("system", f"PERSONA: {persona}\nGOAL: {instr}\n{format_instructions}"),
                ("user", f"Base Analysis: {architect_summary}\nRaw: {client_message}")
            ])

        # Final Parsing
        chain = final_prompt | self.llm | self.parser
        result = chain.invoke({
            "format_instructions": self.parser.get_format_instructions(),
            "client_message": client_message
        })
        return ProjectPlan(**result)

# --- 3. UI HELPERS ---

def format_section(title, items, is_list=True):
    if not items: return ""
    content = f"\n### {title}\n"
    if is_list:
        for item in items:
            if isinstance(item, dict):
                content += f"- **[{item.get('severity', 'Low')}] {item.get('category', 'Risk')}:** {item.get('description', '')}\n  *Mitigation:* {item.get('mitigation', 'N/A')}\n"
            else:
                content += f"- {item}\n"
    else:
        content += str(items)
    return content

def process_request(message, mode, chat_history):
    if not message.strip(): return "", chat_history
    plan = engine.generate_plan(message, mode)
    full_response = f"# 🔍 Analysis Mode: {mode}\n\n"
    if plan.summary: full_response += f"## 🎯 Summary\n{plan.summary}\n"
    if plan.scope_included: full_response += format_section("✅ What's Included", plan.scope_included)
    if plan.scope_excluded: full_response += format_section("🚫 Not Included", plan.scope_excluded)
    if plan.risks: full_response += format_section("⚠️ Risk Warnings", [r.model_dump() for r in plan.risks])
    if plan.missing_information: full_response += format_section("❓ Missing Information", plan.missing_information)
    if plan.suggested_questions: full_response += format_section("💬 Smart Questions", plan.suggested_questions)
    chat_history.append({"role": "user", "content": f"Analyze: {mode}"})
    chat_history.append({"role": "assistant", "content": full_response})
    return "", chat_history

# --- 4. APP ---

engine = FlowixEngine()

with gr.Blocks() as demo:
    gr.Markdown("# FlowixPro Professional\n*AI-Powered Clarity Engine for Freelancers & Agencies.*")
    chatbot = gr.Chatbot(label="FlowixPro Engine", height=300)
    with gr.Row():
        msg = gr.Textbox(placeholder="Paste messy client message here...", label="Client Input", lines=4)
    with gr.Row():
        btn_sum = gr.Button("🎯 Summary", variant="secondary")
        btn_scope = gr.Button("✅ Scope", variant="secondary")
        btn_risk = gr.Button("⚠️ Risks", variant="secondary")
        btn_gap = gr.Button("❓ Gaps", variant="secondary")
        btn_ques = gr.Button("💬 Questions", variant="secondary")
        btn_full = gr.Button("🔥 Full Analysis", variant="primary")

    btn_sum.click(lambda m, h: process_request(m, "Summary", h), [msg, chatbot], [msg, chatbot])
    btn_scope.click(lambda m, h: process_request(m, "Scope", h), [msg, chatbot], [msg, chatbot])
    btn_risk.click(lambda m, h: process_request(m, "Risks", h), [msg, chatbot], [msg, chatbot])
    btn_gap.click(lambda m, h: process_request(m, "Gaps", h), [msg, chatbot], [msg, chatbot])
    btn_ques.click(lambda m, h: process_request(m, "Questions", h), [msg, chatbot], [msg, chatbot])
    btn_full.click(lambda m, h: process_request(m, "Full", h), [msg, chatbot], [msg, chatbot])
    gr.Button("Clear All").click(lambda: [], None, chatbot)

if __name__ == "__main__":
    demo.launch(share=True)
