from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class QueryClassification(BaseModel):
    is_germany_related: bool = Field(description="Whether the query is related to studying/living/working in Germany")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation for the classification")

class CentralController:
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.output_parser = PydanticOutputParser(pydantic_object=QueryClassification)
        
        system_prompt = """You are a query classifier that determines if questions are related to studying, living, or working in Germany.
        
        Rules:
        - Specific questions about German culture, language, or life in Germany are relevant
        - General greetings or small talk are not relevant.
        - General questions about Germany are not relevant.
        - Questions that don't specifically mention Germany but imply it (like "How do I get a student visa?") should be carefully evaluated
        - Simple questions that don't require specific German context are not relevant
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

    async def process_query(self, client, query: str, query_qdrant) -> dict:
        classification = await self.classify_query(query)
        
        if classification.is_germany_related and classification.confidence_score > 0.7:
            qdrant_response = query_qdrant(client = client, collection_name = "study-in-germany", query = query)
            
            if isinstance(qdrant_response, dict) and "error" in qdrant_response:
                return {
                    "answer": f"Database query failed: {qdrant_response['error']}",
                    "sources": []
                }
            
            return qdrant_response
        
        chat_response = await self.llm.ainvoke([
            {"role": "system", "content": "You are a helpful assistant. Provide concise and direct responses."},
            {"role": "user", "content": query}
        ])
        
        return {
            "answer": chat_response.content,
            "sources": []
        }
        
