#!/usr/bin/env python3
"""LangChain + Langfuse integration — captures LLM traces.

Prerequisites:
    pip install langfuse langchain langchain-openai langchain-core

Usage:
    # Start Langfuse (in BONUS-llm-native-obs/):
    #   docker compose up -d
    #       # Wait ~30s for Langfuse to initialize
    #
    # Then run this script:
    #   python langfuse-trace.py
    #
    # Open http://localhost:3002 to view traces in Langfuse UI.
    #   Default credentials:  admin@langfuse.com / langfuse123
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from datetime import datetime, timezone

from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler(
    user_id="day23-lab",
    metadata={
        "lab": "Day 23 Observability",
        "date": datetime.now(tz=timezone.utc).isoformat(),
    },
)


def generate_trace() -> str:
    """Run a simple LangChain chain with Langfuse tracing and return trace URL."""
    # Mock LLM — replace with real ChatOpenAI by setting OPENAI_API_KEY env var.
    # With a real key the trace shows token usage, latency, completion, etc.
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY", "mock"),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        timeout=30,
    )

    prompt = (
        "Explain in one sentence why observability matters for AI services."
    )

    print(f"Running LangChain chain with prompt: {prompt}")
    response = llm.invoke(prompt, config={"callbacks": [langfuse_handler]})
    print(f"Response: {response.content}")

    return "http://localhost:3002 (view latest trace in Langfuse UI)"


def cleanup() -> None:
    """Stop and remove Langfuse stack."""
    print("Stopping Langfuse stack...")
    # User runs: docker compose down


if __name__ == "__main__":
    print("=" * 60)
    print("Langfuse Self-Hosted — LangChain LLM Trace Capture")
    print("=" * 60)
    print()
    print("Steps:")
    print("  1. docker compose up -d")
    print("  2. Wait 30s for Langfuse to initialize")
    print("  3. Open http://localhost:3002")
    print("     First-time login: admin@langfuse.com / langfuse123")
    print("  4. python langfuse-trace.py")
    print()
    print("=" * 60)

    trace_url = generate_trace()
    print(f"\nTrace URL: {trace_url}")
    print("Open the URL above to see the LangChain LLM trace in Langfuse.")
