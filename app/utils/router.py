from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_core.messages import ChatMessage

from constants import CENTRAL_LLM_MODEL, CONFIDENCE_SCORE_THRESHOLD

class QueryClassification(BaseModel):
    is_germany_related: bool = Field(description="Whether the query is related to studying/living/working in Germany")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation for the classification")

class CentralController:
    def __init__(self, model_name: str = CENTRAL_LLM_MODEL, temperature: float = 0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.output_parser = PydanticOutputParser(pydantic_object=QueryClassification)
        
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
        
        self.classifier_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Let's think step by step. Here is the user's query: {query}")
        ])
        
        self.classifier_prompt = self.classifier_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions()
        )

    async def classify_query(self, query: str) -> QueryClassification:
        formatted_prompt = self.classifier_prompt.format_messages(query=query)
        response = await self.llm.ainvoke(formatted_prompt)
        
        try:
            return self.output_parser.parse(response.content)
        except Exception as e:
            return QueryClassification(
                is_germany_related=False,
                confidence_score=1.0,
                reasoning="Failed to parse LLM response, treating as non-Germany related query"
            )

    async def process_query(self, client, messages: list, query_qdrant) -> dict:
        # Get the latest user message
        latest_query = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
        if not latest_query:
            return {
                "answer": "No user query found in messages",
                "sources": []
            }

        # First classify the latest query
        classification = await self.classify_query(latest_query)
        
        if classification.is_germany_related and classification.confidence_score > CONFIDENCE_SCORE_THRESHOLD:
            # Get context and sources from Qdrant
            qdrant_response = query_qdrant(
                client=client, 
                collection_name="study-in-germany", 
                query=latest_query
            )
            
            if isinstance(qdrant_response, dict) and "error" in qdrant_response:
                return {
                    "answer": f"Database query failed: {qdrant_response['error']}",
                    "sources": []
                }

            # Create prompt with context
            context_prompt = ChatMessage(
                role="system",
                content="""You are a knowledgeable educational advisor specializing in German higher education and life in Germany.
                Based on the provided context, provide a detailed and well-structured answer.
                
                Guidelines:
                - Focus on practical information
                - Include specific requirements and processes
                - Break down complex procedures into clear steps
                - If information is time-sensitive, mention that details may change
                - If the answer cannot be fully derived from the context, mention that
                
                Context:
                {context}
                """
            )

            # Create messages for LLM
            chat_messages = [
                context_prompt,
                ChatMessage(role="user", content=latest_query)
            ]

            # Format the prompt with context
            chat_messages[0].content = chat_messages[0].content.format(
                context=qdrant_response.get("context", "No context available")
            )

            # Get response from LLM
            chat_response = await self.llm.ainvoke(chat_messages)
            
            return {
                "answer": chat_response.content,
                "sources": qdrant_response.get("sources", [])
            }
        
        # For non-Germany related queries, include chat history
        chat_messages = [
            ChatMessage(role="system", content="""You are a helpful assistant. Provide concise and direct responses.
            If the user's question requires context from the chat history, use it to provide a more accurate response.""")
        ]
        
        # Add chat history
        for msg in messages[:-1]:  # All messages except the latest
            chat_messages.append(ChatMessage(
                role=msg['role'],
                content=msg['content']
            ))
        
        # Add the latest query
        chat_messages.append(ChatMessage(
            role="user",
            content=latest_query
        ))
        
        chat_response = await self.llm.ainvoke(chat_messages)
        
        return {
            "answer": chat_response.content,
            "sources": []
        }
        
