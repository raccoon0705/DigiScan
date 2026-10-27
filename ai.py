"""
AI Module for DigiScan Legal AI.

Encapsulates cloud LLM API integration using Google GenAI SDK.
Ensures single-LLM architecture (Gemini Flash class), token efficiency,
defensive system prompting, and clean error handling.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

from prompts import (
    build_system_prompt,
    build_structured_analysis_prompt,
    build_comprehensive_analysis_prompt,
    build_custom_prompt,
    build_chat_prompt,
    LEGAL_DISCLAIMER_TEXT,
)

# Load environment variables from .env file
load_dotenv()

# Default Gemini Flash class model prioritizing accuracy, sub-10s speed, and availability
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3-flash-preview"]


def get_api_key(override_key: Optional[str] = None) -> Optional[str]:
    """
    Retrieves the Gemini API key from explicit override or environment variable.
    """
    if override_key is not None:
        return override_key.strip() or None
    return os.getenv("GEMINI_API_KEY", "").strip() or None


def is_api_configured(override_key: Optional[str] = None) -> bool:
    """Checks if a valid API key is present."""
    key = get_api_key(override_key)
    return bool(key and len(key) > 5)


def get_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Initializes and returns the Google GenAI client instance with 60s timeout and fast retries.
    Raises ValueError if API key is missing.
    """
    resolved_key = get_api_key(api_key)
    if not resolved_key:
        raise ValueError(
            "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env "
            "file or enter it in the application sidebar."
        )
    http_opts = types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=2, initial_delay=0.5, max_delay=2.0)
    )
    return genai.Client(api_key=resolved_key, http_options=http_opts)


def _call_model(
    contents: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.2,
    response_mime_type: Optional[str] = None,
    max_output_tokens: int = 3000,
    thinking_budget: Optional[int] = 250,
    system_instruction: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Internal helper to call the Gemini Flash LLM with system instructions, fast thinking config, and fallback handling.
    """
    target_model = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    
    try:
        client = get_client(api_key)
        active_sys_inst = system_instruction or build_system_prompt()

        cfg_params = {
            "system_instruction": active_sys_inst,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }
        if response_mime_type:
            cfg_params["response_mime_type"] = response_mime_type
        if thinking_budget is not None:
            try:
                cfg_params["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
            except Exception:
                pass

        config = types.GenerateContentConfig(**cfg_params)

        response = client.models.generate_content(
            model=target_model,
            contents=contents,
            config=config,
        )

        output_text = response.text or ""
        if not output_text.strip():
            output_text = "The model returned an empty response. Please verify the document content."

        return {
            "success": True,
            "content": output_text.strip(),
            "model_used": target_model,
            "error": None
        }

    except APIError as api_err:
        err_msg = str(api_err)
        # Attempt fallback to alternative Flash models if current model encounters 404, 503, or 429
        if any(err_token in err_msg.lower() for err_token in ["404", "not found", "503", "unavailable", "429", "resource_exhausted", "quota"]):
            for alt_model in FALLBACK_MODELS:
                if alt_model == target_model:
                    continue
                try:
                    client = get_client(api_key)
                    fallback_cfg_params = {
                        "system_instruction": active_sys_inst,
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    }
                    if response_mime_type:
                        fallback_cfg_params["response_mime_type"] = response_mime_type
                    if thinking_budget is not None:
                        try:
                            fallback_cfg_params["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
                        except Exception:
                            pass

                    fallback_resp = client.models.generate_content(
                        model=alt_model,
                        contents=contents,
                        config=types.GenerateContentConfig(**fallback_cfg_params),
                    )
                    return {
                        "success": True,
                        "content": (fallback_resp.text or "").strip(),
                        "model_used": alt_model,
                        "error": None
                    }
                except Exception:
                    continue

        # User-friendly explanation of API error
        if "API_KEY_INVALID" in err_msg or "invalid api key" in err_msg.lower():
            friendly_err = "Invalid API Key: Please verify that your Gemini API key is valid and has active permissions."
        elif "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower() or "429" in err_msg:
            friendly_err = "API Rate Limit or Quota Exceeded: Please wait a moment before retrying, or check your Gemini API quota."
        else:
            friendly_err = f"Gemini API Error: {err_msg}"

        return {
            "success": False,
            "content": "",
            "model_used": target_model,
            "error": friendly_err
        }

    except ValueError as val_err:
        return {
            "success": False,
            "content": "",
            "model_used": target_model,
            "error": str(val_err)
        }

    except Exception as exc:
        return {
            "success": False,
            "content": "",
            "model_used": target_model,
            "error": f"Unexpected error communicating with LLM API: {str(exc)}"
        }


def analyze_document(
    document_text: str,
    custom_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs legal document analysis.
    If custom_prompt is provided, focuses on user request;
    otherwise generates a comprehensive structured legal analysis.
    
    Args:
        document_text: Extracted text from document
        custom_prompt: Optional user-defined prompt (e.g. "Identify payment clauses")
        api_key: Optional API key override
        model_name: Model identifier
        
    Returns:
        dict: Result metadata and analyzed content
    """
    clean_text = (document_text or "").strip()
    if not clean_text:
        return {
            "success": False,
            "content": "",
            "model_used": "",
            "error": "The document text is empty. Please upload or paste a legal document first."
        }

    # Build prompt based on whether user supplied a custom prompt
    if custom_prompt and custom_prompt.strip():
        payload = build_custom_prompt(clean_text, custom_prompt.strip())
    else:
        payload = build_comprehensive_analysis_prompt(clean_text)

    return _call_model(
        contents=payload,
        api_key=api_key,
        model_name=model_name,
        temperature=0.2
    )


def chat_with_document(
    document_text: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Conducts conversational Q&A grounded in the loaded document and session history.
    
    Args:
        document_text: Extracted document text
        chat_history: List of prior messages [{"role": "user"|"assistant", "content": "..."}]
        user_message: Latest user question
        api_key: Optional API key
        model_name: Model identifier
        
    Returns:
        dict: Result containing assistant reply
    """
    clean_text = (document_text or "").strip()
    clean_query = (user_message or "").strip()

    if not clean_text:
        return {
            "success": False,
            "content": "",
            "model_used": "",
            "error": "No document is currently loaded. Please upload or paste a document before asking questions."
        }

    if not clean_query:
        return {
            "success": False,
            "content": "",
            "model_used": "",
            "error": "Question cannot be empty. Please enter a question about the document."
        }

    payload = build_chat_prompt(clean_text, chat_history, clean_query)

    return _call_model(
        contents=payload,
        api_key=api_key,
        model_name=model_name,
        temperature=0.2
    )


def analyze_document_structured(
    document_text: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs legal contract analysis and returns structured dashboard data
    (Plain-English summary points, categorized risky clauses, excerpts, suggested questions).
    """
    clean_text = (document_text or "").strip()
    if not clean_text:
        return {
            "success": False,
            "data": {},
            "raw": "",
            "error": "The document text is empty."
        }

    payload = build_structured_analysis_prompt(clean_text)
    lean_sys_inst = (
        "You are DigiScan Legal AI. Objectively analyze legal risks grounded strictly "
        "in the document text. Output JSON only."
    )
    raw_res = _call_model(
        contents=payload,
        api_key=api_key,
        model_name=model_name,
        temperature=0.1,
        response_mime_type="application/json",
        max_output_tokens=3000,
        thinking_budget=250,
        system_instruction=lean_sys_inst,
    )

    if not raw_res["success"]:
        return {
            "success": False,
            "data": {},
            "raw": "",
            "error": raw_res.get("error", "Failed to analyze document.")
        }

    content_str = raw_res["content"].strip()
    
    # Strip markdown code blocks if the model wrapped output in ```json ... ```
    if content_str.startswith("```"):
        content_str = re.sub(r"^```(?:json)?\s*", "", content_str)
        content_str = re.sub(r"\s*```$", "", content_str)

    # Attempt JSON parsing
    try:
        parsed = json.loads(content_str)
    except Exception:
        # Fallback: regex search for JSON object
        json_match = re.search(r"\{.*\}", content_str, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
            except Exception:
                parsed = {}
        else:
            parsed = {}

    # Validate or create safe defaults if keys missing
    if not isinstance(parsed, dict):
        parsed = {}

    if "summary_points" not in parsed or not isinstance(parsed["summary_points"], list):
        parsed["summary_points"] = [
            {"text": "General commercial agreement specifying mutual duties and terms.", "indicator": "blue"}
        ]

    if "clauses" not in parsed or not isinstance(parsed["clauses"], list):
        parsed["clauses"] = []

    if "suggested_questions" not in parsed or not isinstance(parsed["suggested_questions"], list):
        parsed["suggested_questions"] = [
            "What is the cancellation policy?",
            "What happens to my data after termination?",
            "What is the maximum liability cap?",
            "Where and how are legal disputes resolved?"
        ]

    return {
        "success": True,
        "data": parsed,
        "raw": content_str,
        "model_used": raw_res.get("model_used", ""),
        "error": None
    }

