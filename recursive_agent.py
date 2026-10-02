#!/usr/bin/env python3
"""
Recursive LLM Agent using DeepSeek API with Tool Calling
This agent can call external tools (like web search) to gather information
and reason about the results before responding.
"""

import os
import json
import re
import requests
from openai import OpenAI
from typing import Optional, Dict, Any

# Read API key from the environment (never hard-code secrets).
# Set it first, e.g.  export DEEPSEEK_API_KEY="sk-..."  (see .env.example)
def load_api_key() -> str:
    """Load the DeepSeek API key from the DEEPSEEK_API_KEY environment variable."""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not set. Export it or copy .env.example to .env. "
            "See the README for setup."
        )
    return key

# Initialize the DeepSeek client
api_key = load_api_key()
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


# ===== TOOL IMPLEMENTATIONS =====

class ToolExecutor:
    """Handles execution of various tools"""
    
    # Sample data for fallback mode
    SAMPLE_DATA = {
        "renewable energy": [
            "1. Renewable energy reaches new record: Global renewable capacity grew by 50% in 2023, adding 510 GW, with solar accounting for 75%. URL: https://example.com/renewable-growth",
            "2. Solar dominance continues: Solar PV is the fastest-growing renewable technology with costs declining 89% since 2010. URL: https://example.com/solar-trends",
            "3. Wind energy expansion: Offshore wind is gaining momentum, particularly in Europe and China. URL: https://example.com/wind-development"
        ],
        "renewable energy adoption trends": [
            "1. China leads expansion: China added 60% of new renewable capacity in 2023, more solar than world added in 2022. URL: https://example.com/china-renewable",
            "2. Energy security drives growth: Post-Ukraine war energy security concerns accelerating European renewable adoption. URL: https://example.com/energy-security",
            "3. IRA impact: US Inflation Reduction Act driving rapid solar and wind expansion. URL: https://example.com/ira-effect"
        ],
        "energy": [
            "1. Global energy transition accelerates: Renewables projected to be largest electricity source by 2025. URL: https://example.com/energy-transition",
            "2. Battery storage deployment: Storage capacity expected to increase sixfold by 2030. URL: https://example.com/storage-growth",
            "3. Grid modernization: Investment in smart grids critical for renewable integration. URL: https://example.com/grid-modernization"
        ]
    }
    
    @staticmethod
    def web_search(query: str, num_results: int = 3) -> str:
        """
        Perform a web search using multiple methods with fallback to sample data
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Formatted search results
        """
        try:
            print(f"  🔍 Executing web search: '{query}'")
            
            # Headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
            }
            
            # Try multiple endpoints
            endpoints = [
                f"https://api.duckduckgo.com/?q={query}&format=json",
                f"https://duckduckgo.com/api?q={query}&format=json",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        
                        # Try to extract results from different possible formats
                        if 'Results' in data and data['Results']:
                            for i, result in enumerate(data['Results'][:num_results]):
                                text = result.get('Text', result.get('Title', 'No text'))
                                url = result.get('FirstURL', result.get('URL', 'N/A'))
                                results.append(f"{i+1}. {text}\n   URL: {url}")
                        
                        if results:
                            return "Web Search Results:\n" + "\n".join(results)
                
                except Exception as e:
                    continue
            
            # Fallback: Use sample data based on query keywords
            print(f"  ℹ️  Real search unavailable, using sample data")
            matched_data = None
            
            for key in ToolExecutor.SAMPLE_DATA:
                if key.lower() in query.lower() or any(word in query.lower() for word in key.split()):
                    matched_data = ToolExecutor.SAMPLE_DATA[key]
                    break
            
            if not matched_data:
                matched_data = ToolExecutor.SAMPLE_DATA["energy"]
            
            return "Web Search Results (Sample Data):\n" + "\n".join(matched_data[:num_results])
                
        except Exception as e:
            return f"Search error: {str(e)}"
    
    @staticmethod
    def calculate(expression: str) -> str:
        """
        Evaluate a mathematical expression
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Result of calculation
        """
        try:
            print(f"  🧮 Calculating: {expression}")
            result = eval(expression)
            return f"Calculation result: {expression} = {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    @staticmethod
    def get_current_info() -> str:
        """Get current system information"""
        try:
            print(f"  ℹ️  Fetching system information")
            return f"Current date/time: {os.popen('date').read().strip()}\nSystem info available."
        except:
            return "Unable to fetch system information"
    
    @staticmethod
    def execute(tool_name: str, **kwargs) -> str:
        """
        Execute a tool by name
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool output
        """
        tools = {
            'web_search': ToolExecutor.web_search,
            'calculate': ToolExecutor.calculate,
            'get_info': ToolExecutor.get_current_info,
        }
        
        if tool_name in tools:
            return tools[tool_name](**kwargs)
        else:
            return f"Unknown tool: {tool_name}. Available tools: {', '.join(tools.keys())}"

class RecursiveAgent:
    def __init__(self, max_depth: int = 5, model: str = "deepseek-chat"):
        """
        Initialize the tool-using agent.
        
        Args:
            max_depth: Maximum recursion depth to prevent infinite loops
            model: The model to use (default: deepseek-chat)
        """
        self.max_depth = max_depth
        self.model = model
        self.call_count = 0
        self.tool_call_count = 0
        self.conversation_history = []

    def call_api(self, messages: list) -> str:
        """Call the DeepSeek API and return the response."""
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            temperature=0.7,
        )
        return response.choices[0].message.content

    def execute(self, task: str, depth: int = 0, parent_context: str = "") -> str:
        """
        Execute a task and use tools as needed.
        
        Args:
            task: The main task to execute
            depth: Current recursion depth
            parent_context: Context from parent calls
            
        Returns:
            The final result or response
        """
        self.call_count += 1
        indent = "  " * depth
        
        print(f"\n{indent}[Level {depth}] Agent Call #{self.call_count}: {task[:50]}...")

        # Check recursion depth limit
        if depth >= self.max_depth:
            print(f"{indent}⚠️  Max depth ({self.max_depth}) reached. Stopping recursion.")
            return f"Task completed at max depth."

        # Build the system prompt that encourages tool usage
        system_prompt = """You are a helpful, intelligent assistant that can use external tools to gather information.

Available tools:
- web_search: Search the web for current information. Use when you need to look up facts, news, or current data.
- calculate: Perform mathematical calculations
- get_info: Get system information

When you need to use a tool, include a JSON block like this in your response:

[TOOL_CALL]
{
  "tool": "tool_name",
  "reasoning": "Why you're calling this tool",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
[/TOOL_CALL]

IMPORTANT:
- Only use tools when absolutely necessary for completing the task
- If a tool returns no results or errors, try different search terms once, then provide your best answer without tools
- Avoid using tools multiple times for similar queries - this wastes resources
- After getting tool results, synthesize them into a comprehensive answer
- Don't keep trying different tool calls if tools aren't working - just provide your best response

Be concise and efficient in your responses."""

        # Build messages with context
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        if parent_context:
            messages.append({
                "role": "user",
                "content": f"Context from previous work:\n{parent_context}\n\nNow, please handle this task: {task}"
            })
        else:
            messages.append({"role": "user", "content": task})

        # Call the API
        response = self.call_api(messages)
        
        print(f"{indent}📤 Response: {response[:100]}..." if len(response) > 100 else f"{indent}📤 Response: {response}")

        # Parse the response to check for tool calls
        tool_call_info = self._extract_tool_call(response)
        
        if tool_call_info:
            tool_name = tool_call_info.get('tool')
            reasoning = tool_call_info.get('reasoning', 'No reasoning provided')
            parameters = tool_call_info.get('parameters', {})
            
            print(f"{indent}🔧 Tool Call ({tool_name}): {reasoning}")
            
            # Execute the tool
            tool_result = ToolExecutor.execute(tool_name, **parameters)
            self.tool_call_count += 1
            
            print(f"{indent}📊 Tool Result: {tool_result[:80]}..." if len(tool_result) > 80 else f"{indent}📊 Tool Result: {tool_result}")
            
            # Check if tool returned no results
            if "No results found" in tool_result or "error" in tool_result.lower():
                # If tool failed, don't recurse - just return what we have
                print(f"{indent}ℹ️  Tool returned no results. Finalizing response.")
                final_result = f"{response}\n\n[Tool Used: {tool_name}]\n{tool_result}\n\n[Note: Tool returned no additional data, providing best available information.]"
                return final_result
            
            # Only recurse if we got meaningful results and haven't recursed too much
            if depth < self.max_depth - 1:
                continuation_task = f"Based on the tool output below, provide a comprehensive answer to the original task. Tool result:\n{tool_result}"
                continuation_result = self.execute(continuation_task, depth + 1, f"{response}\n\n[Tool Output]:\n{tool_result}")
                
                # Combine results
                final_result = f"{response}\n\n[Tool Used: {tool_name}]\n{tool_result}\n\n[Final Answer]:\n{continuation_result}"
                return final_result
            else:
                # At depth limit, just return what we have
                final_result = f"{response}\n\n[Tool Used: {tool_name}]\n{tool_result}"
                return final_result
        else:
            print(f"{indent}✅ Task completed (no tools needed)")
            return response

    def _extract_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract tool call information from the response if present.
        Looks for [TOOL_CALL] JSON blocks.
        """
        pattern = r'\[TOOL_CALL\](.*?)\[/TOOL_CALL\]'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1).strip()
                tool_data = json.loads(json_str)
                if "tool" in tool_data:
                    return tool_data
            except json.JSONDecodeError:
                print("⚠️  Could not parse tool call JSON")
        
        return None

    def reset(self):
        """Reset the agent state for a new session."""
        self.call_count = 0
        self.tool_call_count = 0
        self.conversation_history = []


def main():
    """Main function demonstrating the tool-using agent."""
    
    # Example usage
    print("🤖 Tool-Using LLM Agent Started\n")
    print("=" * 60)
    
    agent = RecursiveAgent(max_depth=3)
    
    # Example task that might benefit from web search
    main_task = """
    What are the latest developments in AI and machine learning?
    Search for current information and provide an analysis.
    """
    
    result = agent.execute(main_task)
    
    print("\n" + "=" * 60)
    print(f"\n📊 Final Result:\n{result}")
    print(f"\n📈 Stats:")
    print(f"   - API calls made: {agent.call_count}")
    print(f"   - Tools used: {agent.tool_call_count}")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Set the DEEPSEEK_API_KEY environment variable (see .env.example)")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
