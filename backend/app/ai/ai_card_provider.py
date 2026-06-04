from pydantic import BaseModel, ConfigDict
from openai import OpenAI
from openai import APIError, APITimeoutError, RateLimitError

from backend.app.ai.prompt_card_generation import (
    build_card_generation_system_prompt,
    build_card_generation_user_prompt,
)
from backend.app.ai.prompt_card_revision import (
    build_card_revision_system_prompt,
    build_card_revision_user_prompt,
)
from coreengine.ai_card_factory.provider import GeneratedCardDraft


class OpenAICardDraftItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note_type_id: int
    fields: list[str]
    tags: list[str]
    hint: str
    reason: str


class OpenAICardDraftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drafts: list[OpenAICardDraftItem]


class OpenAICardDraftProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
    ):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")

        self.__client = OpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
        )
        self.__model = model

    def generate_drafts(
        self,
        source_text: str,
        user_prompt: str,
        note_type_id: int | None,
        max_cards: int,
        language: str,
    ) -> list[GeneratedCardDraft]:
        try:
            response = self.__client.responses.parse(
                model=self.__model,
                input=[
                    {
                        "role": "system",
                        "content": build_card_generation_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_card_generation_user_prompt(
                            source_text=source_text,
                            user_prompt=user_prompt,
                            note_type_id=note_type_id,
                            max_cards=max_cards,
                            language=language,
                        ),
                    },
                ],
                text_format=OpenAICardDraftResponse,
            )

            parsed = response.output_parsed

            if parsed is None:
                raise ValueError("OpenAI returned no parsed card draft response")

            drafts = self.__to_generated_drafts(parsed)

            if len(drafts) > max_cards:
                drafts = drafts[:max_cards]

            return drafts

        except RateLimitError as e:
            raise ValueError("OpenAI rate limit exceeded. Try again later.") from e
        except APITimeoutError as e:
            raise ValueError("OpenAI request timed out. Try again later.") from e
        except APIError as e:
            raise ValueError(f"OpenAI API error: {e}") from e

    def revise_drafts(
        self,
        current_drafts: list[GeneratedCardDraft],
        user_instruction: str,
        language: str,
    ) -> list[GeneratedCardDraft]:
        try:
            response = self.__client.responses.parse(
                model=self.__model,
                input=[
                    {
                        "role": "system",
                        "content": build_card_revision_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": build_card_revision_user_prompt(
                            current_drafts=current_drafts,
                            user_instruction=user_instruction,
                            language=language,
                        ),
                    },
                ],
                text_format=OpenAICardDraftResponse,
            )

            parsed = response.output_parsed

            if parsed is None:
                raise ValueError("OpenAI returned no parsed revised card draft response")

            drafts = self.__to_generated_drafts(parsed)

            if len(drafts) != len(current_drafts):
                raise ValueError("OpenAI revised draft count does not match current draft count")

            return drafts

        except RateLimitError as e:
            raise ValueError("OpenAI rate limit exceeded. Try again later.") from e
        except APITimeoutError as e:
            raise ValueError("OpenAI request timed out. Try again later.") from e
        except APIError as e:
            raise ValueError(f"OpenAI API error: {e}") from e

    def __to_generated_drafts(
        self,
        parsed: OpenAICardDraftResponse,
    ) -> list[GeneratedCardDraft]:
        return [
            GeneratedCardDraft(
                note_type_id=item.note_type_id,
                fields=item.fields,
                tags=item.tags,
                hint=item.hint,
                reason=item.reason,
            )
            for item in parsed.drafts
        ]