import os
from langchain_openai import ChatOpenAI

class OpenAIChatModel:
    def __init__(self, model_name, temperature):
        self.api_key = os.environ("OPENAI_API_KEY")
        self.model_name = model_name
        self.temperature = temperature

    def _get_llm(self,):
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
        )

        return self.llm
    
    def _create_messages(self, system_prompt, human_prompt):
        return [
            (
                "system",
                system_prompt
            ),
            (
                "human",
                human_prompt
            )
        ]

    def invoke(self, system_prompt, human_prompt):
        if not self.llm:
            self._get_llm()

        return llm.invoke(self._create_messages(system_prompt, human_prompt))
    