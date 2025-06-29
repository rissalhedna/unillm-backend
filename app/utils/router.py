import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from app.utils.storage_utils import query_qdrant
from constants import CENTRAL_LLM_MODEL
from fastapi import HTTPException


class QueryClassification(BaseModel):
    is_germany_related: bool = Field(
        description="Whether the query is related to studying/living/working in Germany"
    )


def get_latest_user_message(messages: List[Dict[str, Any]]) -> str:
    """Extract the latest user message from the messages array"""
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")
    return ""


class CentralController:
    def __init__(
        self,
        model_name: str = CENTRAL_LLM_MODEL,
        temperature: float = 0,
    ):
        self.client = AsyncOpenAI()
        self.model_name = model_name
        self.temperature = temperature

    def _create_classifier_prompt(self, query: str) -> str:
        return f"""You are a query classifier that determines if questions are related to studying, living, or working in Germany.

Rules:
- Specific questions about German culture, language, or life in Germany are relevant
- General greetings or small talk are not relevant.
- General questions about Germany are not relevant.
- Questions that don't specifically mention Germany but imply it (like "How do I get a student visa?") should be carefully evaluated
- Simple questions that don't require specific German context are not relevant
- If the user's question is not related to Germany, return a confidence score of 0.

Examples:
- "What is the weather in Berlin?" is irrelevant
- "What is the weather in Germany?" is irrelevant
- "How do I get a student visa?" is relevant
- "How do I get a student job?" is relevant

You must respond with a valid JSON object in this exact format:
{{
    "is_germany_related": boolean
}}

User query: {query}

Respond with only the JSON:"""

    async def classify_query(self, query: str) -> QueryClassification:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a precise query classifier. Respond only with valid JSON."},
                    {"role": "user", "content": self._create_classifier_prompt(query)}
                ],
                temperature=self.temperature,
                max_tokens=200
            )
            
            json_str = response.choices[0].message.content.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(json_str)
            return QueryClassification(**data)
            
        except Exception as e:
            print(f"Classification error: {e}")
            return QueryClassification(is_germany_related=False)

    async def process_query(self, client, messages: List[Dict[str, Any]]) -> dict:
        query = get_latest_user_message(messages)
        if not query:
            raise HTTPException(status_code=400, detail="No user message found in messages")
            
        classification = await self.classify_query(query)

        if classification.is_germany_related:
            return await self._handle_germany_query(client, messages)

        return await self._handle_general_query(messages)

    async def _handle_germany_query(self, client, messages: List[Dict[str, Any]]) -> dict:
        try:
            query = get_latest_user_message(messages)
            qdrant_response = query_qdrant(
                client=client, collection_name="study-in-germany", query=query
            )
            
            if isinstance(qdrant_response, dict) and "error" in qdrant_response:
                raise HTTPException(
                    status_code=500,
                    detail=f"Database query failed: {qdrant_response['error']}"
                )
            
            context = qdrant_response.get("context", "No context available")
            system_prompt = f"""You are a knowledgeable educational advisor specializing in German higher education and life in Germany.
Based on the provided context, provide a detailed and well-structured answer.

Guidelines:
- Focus on practical information
- Include specific requirements and processes
- Break down complex procedures into clear steps
- If information is time-sensitive, mention that details may change
- If the answer cannot be fully derived from the context, mention that

Context:
{context}"""

            openai_messages = [{"role": "system", "content": system_prompt}]
            
            for msg in messages:
                if msg.get("role") in ["user", "assistant"]:
                    openai_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=self.temperature,
                stream=True
            )

            return {
                "answer": response,
                "sources": qdrant_response.get("sources", []),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def _handle_general_query(self, messages: List[Dict[str, Any]]) -> dict:
        openai_messages = [{"role": "system", "content": "You are a helpful assistant. Provide concise and direct responses."}]
        
        for msg in messages:
            if msg.get("role") in ["user", "assistant"]:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=openai_messages,
            temperature=self.temperature,
            stream=True
        )

        return {
            "answer": response,
            "sources": []
        }
