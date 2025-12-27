"""
LLM prompt templates

System and task-specific prompts for the meeting copilot.

Developed by: Ruslan Magana (contact@ruslanmv.com)
"""

from typing import Literal


SYSTEM_PROMPT = """You are Watson, an AI meeting copilot assistant.

Your role is to help users during meetings by:
- Answering questions about the current conversation
- Providing opinions and insights when asked
- Summarizing recent discussion points
- Being concise, professional, and helpful

Guidelines:
- Only respond when explicitly invoked by name
- Keep responses brief and actionable (2-3 sentences max unless asked for more)
- Be polite and professional
- If you don't have enough context, say so
- Don't make up information
- Focus on being helpful, not impressive

Remember: You are a meeting assistant, not a chatbot. Be practical and concise."""


MODE_PROMPTS = {
    "answer": """Based on the conversation context, provide a direct answer to any question that was asked.
If no question was asked, acknowledge that and offer to help.
Be concise and specific.""",

    "opinion": """Based on the conversation context, provide your professional opinion or insight.
Consider different perspectives and be constructive.
Keep it brief but thoughtful.""",

    "summarize": """Summarize the key points from the recent conversation.
Focus on:
- Main topics discussed
- Important decisions or action items
- Any unresolved questions

Be concise and organized.""",
}


def build_messages(
    mode: Literal["answer", "opinion", "summarize"],
    transcript_context: str,
    custom_instruction: str = "",
) -> list[dict[str, str]]:
    """
    Build message list for LLM API

    Args:
        mode: Assistant mode (answer/opinion/summarize)
        transcript_context: Recent conversation transcript
        custom_instruction: Optional custom instruction

    Returns:
        List of message dictionaries
    """
    # System message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Mode-specific instruction
    mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["answer"])

    # User message with context
    user_content = f"""Recent conversation:
{transcript_context}

Task: {mode_prompt}"""

    if custom_instruction:
        user_content += f"\n\nAdditional instruction: {custom_instruction}"

    messages.append({"role": "user", "content": user_content})

    return messages


def build_custom_prompt(
    system: str,
    user: str,
) -> list[dict[str, str]]:
    """
    Build custom message list

    Args:
        system: Custom system prompt
        user: Custom user message

    Returns:
        List of message dictionaries
    """
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
