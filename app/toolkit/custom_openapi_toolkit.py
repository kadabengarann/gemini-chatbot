from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities.requests import RequestsWrapper
from langchain_community.utilities.requests import TextRequestsWrapper
from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits.json.prompt import JSON_SUFFIX
from langchain_community.agent_toolkits.json.base import create_json_agent
from langchain_community.agent_toolkits.json.toolkit import JsonToolkit

from typing import Any, List

from ..toolkit import prompt

class CustomOpenAPIToolkit(OpenAPIToolkit):
    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        json_spec: JsonSpec,
        requests_wrapper: TextRequestsWrapper,
        allow_dangerous_requests: bool = False,
        prefix: str = prompt.JSON_PREFIX,
        suffix: str = JSON_SUFFIX,
        max_iterations: int = 15,  
        handle_parsing_errors: bool = True,
        **kwargs: Any,
    ) -> OpenAPIToolkit:
        """Create json agent from llm, then initialize."""
        json_agent = create_json_agent(
            llm, 
            JsonToolkit(spec=json_spec), 
            prefix=prefix,
            suffix=suffix,
            agent_executor_kwargs={
                "max_iterations": max_iterations,
                "handle_parsing_errors": handle_parsing_errors,
            },
            **kwargs)
        return cls(
            json_agent=json_agent,
            requests_wrapper=requests_wrapper,
            allow_dangerous_requests=allow_dangerous_requests,
        )
