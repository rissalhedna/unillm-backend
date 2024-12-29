from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from app.utils.storage_utils import query_qdrant
from constants import CENTRAL_LLM_MODEL, CONFIDENCE_SCORE_THRESHOLD
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import HTTPException


class QueryClassification(BaseModel):
    is_germany_related: bool = Field(
        description="Whether the query is related to studying/living/working in Germany"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation for the classification")


class CentralController:
    def __init__(
        self,
        model_type: str = "openai",
        huggingface_model_name: Optional[str] = None,
        model_name: str = CENTRAL_LLM_MODEL,
        temperature: float = 0,
    ):
        if model_type == "openai":
            self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        elif model_type == "huggingface" and huggingface_model_name:
            self.tokenizer = AutoTokenizer.from_pretrained(huggingface_model_name)
            self.llm = AutoModelForCausalLM.from_pretrained(huggingface_model_name)
        else:
            raise ValueError("Invalid model type or missing Hugging Face model name")

        self.output_parser = PydanticOutputParser(pydantic_object=QueryClassification)
        self.classifier_prompt = self._create_classifier_prompt()

    def _create_classifier_prompt(self):
        system_prompt = """You are a query classifier that determines if questions are related to studying, living, or working in Germany.

        Rules:
        - Specific questions about German culture, language, or life in Germany are relevant
        - General greetings or small talk are not relevant.
        - General questions about Germany are not relevant.
        - Questions that don't specifically mention Germany but imply it (like "How do I get a student visa?") should be carefully evaluated
        - Simple questions that don't require specific German context are not relevant
        - If the user's question requires context from the chat history to be fully understood, rewrite it as a self-contained query.
        - If the user's question is not related to Germany, return a confidence score of 0.
        Exemples:
        - "What is the weather in Berlin?" is irrelevant
        - "What is the weather in Germany?" is irrelevant
        - "How do I get a student visa?" is relevant
        - "What is the weather in Germany?" is irrelevant
        - "How do I get a student job?" is relevant

        {format_instructions}

        You must respond with a valid JSON object matching the specified format."""

        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Let's think step by step. Here is the user's query: {query}",
                ),
            ]
        ).partial(format_instructions=self.output_parser.get_format_instructions())

    async def classify_query(self, query: str) -> QueryClassification:
        if isinstance(self.llm, ChatOpenAI):
            formatted_prompt = self.classifier_prompt.format_messages(query=query)
            response = await self.llm.ainvoke(formatted_prompt)
        else:
            inputs = self.tokenizer(query, return_tensors="pt")
            outputs = self.llm.generate(**inputs)
            response_content = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = type('Response', (object,), {'content': response_content})()

        try:
            return self.output_parser.parse(response.content)
        except Exception as e:
            return QueryClassification(
                is_germany_related=False,
                confidence_score=1.0,
                reasoning="Failed to parse LLM response, treating as non-Germany related query",
            )

    async def process_query(self, client, messages: list) -> dict:
        latest_query = self._get_latest_user_message(messages)
        if not latest_query:
            return {"answer": "No user query found in messages", "sources": []}

        classification = await self.classify_query(latest_query)

        if (
            classification.is_germany_related
            and classification.confidence_score > CONFIDENCE_SCORE_THRESHOLD
        ):
            return await self._handle_germany_related_query(
                client, latest_query, query_qdrant
            )

        return await self._handle_non_germany_related_query(messages, latest_query)

    def _get_latest_user_message(self, messages: list) -> Optional[str]:
        return next(
            (msg["content"] for msg in reversed(messages) if msg["role"] == "user"),
            None,
        )

    async def _handle_germany_related_query(
        self, client, latest_query, query_qdrant
    ) -> dict:
        try:
            qdrant_response = query_qdrant(
                client=client, collection_name="study-in-germany", query=latest_query
            )
            
            if isinstance(qdrant_response, dict) and "error" in qdrant_response:
                raise HTTPException(
                    status_code=500,
                    detail=f"Database query failed: {qdrant_response['error']}"
                )
            
            context_prompt = self._create_context_prompt(
                qdrant_response.get("context", "No context available")
            )
            chat_response = await self.llm.ainvoke(
                [context_prompt, ChatMessage(role="user", content=latest_query)]
            )

            return {
                "answer": chat_response.content,
                "sources": qdrant_response.get("sources", []),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def _create_context_prompt(self, context: str) -> ChatMessage:
        return ChatMessage(
            role="system",
            content=f"""You are a knowledgeable educational advisor specializing in German higher education and life in Germany.
            Based on the provided context, provide a detailed and well-structured answer.

            Guidelines:
            - Focus on practical information
            - Include specific requirements and processes
            - Break down complex procedures into clear steps
            - If information is time-sensitive, mention that details may change
            - If the answer cannot be fully derived from the context, mention that

            Context:
            {context}
            """,
        )

    async def _handle_non_germany_related_query(
        self, messages: list, latest_query: str
    ) -> dict:
        chat_messages = [
            ChatMessage(
                role="system",
                content="""You are a helpful assistant. Provide concise and direct responses.
        If the user's question requires context from the chat history, use it to provide a more accurate response.""",
            )
        ]

        chat_messages.extend(
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in messages[:-1]
        )
        chat_messages.append(ChatMessage(role="user", content=latest_query))

        chat_response = await self.llm.ainvoke(chat_messages)

        return {"answer": chat_response.content, "sources": []}
