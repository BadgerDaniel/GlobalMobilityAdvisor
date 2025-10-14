# app/enhanced_agent_router.py

import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chains.llm import LLMChain

class EnhancedAgentRouter:
    def __init__(self, api_key: str = None):
        """Initialize the enhanced agent router with sophisticated routing logic."""
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o")
        
        # Define prompt information for each route
        self.prompt_infos = [
            {
                "name": "policy",
                "description": "This route addresses inquiries about corporate global mobility policies, including rules for employee assignments, available benefits structures, policy 'swim lanes', compliance aspects, and overall program guidelines. Use this for questions about how assignments are structured, what company rules apply, or specifics of policy documents.",
                "prompt_template": """Handle policy-related queries: immigration, visas, compliance, regulations, company policies.
        
        {input}"""
            },
            {
                "name": "compensation",
                "description": "This route handles questions related to employee compensation packages for global mobility scenarios. This includes details on salary calculations, cost-of-living adjustments, housing allowances, hardship pay, currency risk impact on pay, inflation effects, and other financial aspects of an employee's relocation package ensuring their financial wellbeing. Use for questions about how much an employee will earn, what their net pay might be, or how compensation is structured.",
                "prompt_template": """Handle compensation-related queries: salary, pay, allowances, cost calculations, financial packages.
        
        {input}"""
            },
            {
                "name": "both_policy_and_compensation",
                "description": "This route is for complex queries that require a combined understanding of both corporate mobility policies and detailed employee compensation structures. Use this for scenarios asking for optimal solutions or comprehensive advice that must weigh policy constraints (like assignment types) against financial and compensation considerations (like overall cost or employee net income). For example, determining the 'cheapest way to send a senior manager' would fit here.",
                "prompt_template": """Handle complex queries needing both policy and compensation expertise.
        
        {input}"""
            },
            {
                "name": "guidance_fallback",
                "description": "This route is for user queries that do not clearly pertain to specific global mobility policies, employee compensation packages, a direct combination of both, or requests for information retrieval from provided documents. Use this when the query is too vague, off-topic, or if the user seems unsure what to ask. This route provides guidance on the system's capabilities.",
                "prompt_template": """Handle general questions about system capabilities and unclear queries.
        
        {input}"""
            }
        ]
        
        # Create destination chains
        self.destination_chains = {}
        for p_info in self.prompt_infos:
            name = p_info["name"]
            prompt_template_str = p_info["prompt_template"]
            prompt = PromptTemplate(template=prompt_template_str, input_variables=["input"])
            chain = LLMChain(llm=self.llm, prompt=prompt)
            self.destination_chains[name] = chain
        
        # Create router prompt
        router_prompt_template_str = MULTI_PROMPT_ROUTER_TEMPLATE.format(
            destinations='\n'.join([f'{p["name"]}: {p["description"]}' for p in self.prompt_infos])
        )
        router_prompt = PromptTemplate(
            template=router_prompt_template_str,
            input_variables=["input"],
            output_parser=RouterOutputParser(),
        )
        
        # Create the LLMRouterChain
        self.router_chain = LLMRouterChain.from_llm(
            self.llm,
            router_prompt,
            output_key="destination_and_inputs"
        )
        
        print(f"Enhanced Agent Router initialized with {len(self.prompt_infos)} routes:")
        print(f"Route names: {[p['name'] for p in self.prompt_infos]}")
    
    def _load_config(self):
        """Load configuration from route_config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'route_config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load route config: {e}")
            return {"route_messages": {}, "routing_keywords": {}}
    
    def _keyword_based_routing(self, user_input: str) -> str:
        """Pre-filter routing based on keywords to improve accuracy"""
        user_input_lower = user_input.lower()
        
        # Check for keyword matches
        keyword_scores = {}
        for route, keywords in self.config.get("routing_keywords", {}).items():
            score = 0
            for keyword in keywords:
                if keyword in user_input_lower:
                    # Give higher weight to longer, more specific keywords
                    if len(keyword.split()) > 1:  # Multi-word keywords
                        score += 3
                    elif len(keyword) > 6:  # Longer single words
                        score += 2
                    else:
                        score += 1
            
            if score > 0:
                keyword_scores[route] = score
        
        # If we have ANY keyword matches, use them (much more aggressive)
        if keyword_scores:
            best_route = max(keyword_scores, key=keyword_scores.get)
            # Lower threshold - even 1 good match should route
            if keyword_scores[best_route] >= 1:
                print(f"Keyword routing: '{user_input}' -> {best_route} (score: {keyword_scores[best_route]})")
                return best_route
        
        return None  # Let LLM router decide
    
    def get_route_display_info(self, route_name: str) -> dict:
        """Get display information for a route from config"""
        route_messages = self.config.get("route_messages", {})
        route_info = route_messages.get(route_name, {})
        
        return {
            "title": route_info.get("title", route_name.replace('_', ' ').title()),
            "description": route_info.get("description", "Processing your request..."),
            "emoji": route_info.get("emoji", "🤖")
        }
    
    def route_query(self, user_input: str) -> dict:
        """
        Route a user query to the appropriate destination.
        
        Args:
            user_input: The user's query string
            
        Returns:
            dict: Contains 'destination', 'next_inputs', and 'route_info'
        """
        try:
            # Simple rule-based routing first for obvious cases
            user_input_lower = user_input.lower().strip()
            
            # Direct keyword matching for single words or obvious cases
            if user_input_lower in ['compensation', 'salary', 'pay', 'money', 'cost', 'compensation calculator']:
                destination = "compensation"
                print(f"Direct routing: '{user_input}' -> compensation")
            elif user_input_lower in ['policy', 'policies', 'visa', 'immigration', 'compliance', 'policy analyzer']:
                destination = "policy"
                print(f"Direct routing: '{user_input}' -> policy")
            elif any(phrase in user_input_lower for phrase in ['who are you', 'what can you do', 'help me', 'what else']):
                destination = "guidance_fallback"
                print(f"Direct routing: '{user_input}' -> guidance_fallback")
            else:
                # Use LLM for more complex queries
                try:
                    routing_result = self.router_chain.invoke({"input": user_input})
                    
                    # Handle different response formats from LangChain
                    if isinstance(routing_result, dict):
                        if "destination_and_inputs" in routing_result:
                            destination_info = routing_result["destination_and_inputs"]
                        else:
                            destination_info = routing_result
                    else:
                        destination_info = {"destination": "guidance_fallback", "next_inputs": {"input": user_input}}
                    
                    destination = destination_info.get("destination", "guidance_fallback")
                    print(f"LLM routing: '{user_input}' -> {destination}")
                    
                except Exception as llm_error:
                    print(f"LLM routing failed: {llm_error}, defaulting to guidance_fallback")
                    destination = "guidance_fallback"
            
            next_inputs = {"input": user_input}
            
            # Get route description for context
            route_info = next((p for p in self.prompt_infos if p["name"] == destination), None)
            
            return {
                "destination": destination,
                "next_inputs": next_inputs,
                "route_info": route_info,
                "success": True,
                "routing_method": "llm"
            }
        except Exception as e:
            print(f"Error in routing: {e}")
            # Fallback to guidance route
            return {
                "destination": "guidance_fallback",
                "next_inputs": {"input": user_input},
                "route_info": self.prompt_infos[-1],  # guidance_fallback info
                "success": False,
                "error": str(e),
                "routing_method": "fallback"
            }
    
    def get_route_response(self, destination: str, inputs: dict) -> str:
        """
        Get response from the specified destination chain.
        
        Args:
            destination: The route destination
            inputs: Input dictionary for the chain
            
        Returns:
            str: Response from the destination chain
        """
        try:
            if destination in self.destination_chains:
                chain = self.destination_chains[destination]
                response = chain.invoke(inputs)
                return response.get("text", "")
            else:
                return f"Error: Unknown destination '{destination}'"
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def process_query(self, user_input: str) -> dict:
        """
        Complete processing: route query and get response.
        
        Returns:
            dict: Contains routing info and final response
        """
        # Route the query
        routing_result = self.route_query(user_input)
        
        # Get response from destination
        response = self.get_route_response(
            routing_result["destination"], 
            routing_result["next_inputs"]
        )
        
        return {
            **routing_result,
            "response": response
        }
