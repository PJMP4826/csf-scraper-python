"""Prompts canónicos usados por los lectores de imagen basados en LLM."""

from csf_scraper.image_readers.adapters.llms.prompts.llm_image_reader_prompt import (
    CSF_PROMPT,
    RETRY_PROMPT,
)

__all__ = ["CSF_PROMPT", "RETRY_PROMPT"]
