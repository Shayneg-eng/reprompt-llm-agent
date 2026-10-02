# 🤖 Tool-Using LLM Agent with DeepSeek API

An intelligent agent that uses the DeepSeek API and can invoke external tools (like web search) to gather information and reason about the results.

## Features

- 🔧 **Tool Calling**: The agent can call external tools when needed
- 🔍 **Web Search**: Built-in web search capability for current information
- 🧮 **Calculations**: Perform mathematical expressions
- ℹ️ **System Info**: Gather system information
- 🛡️ **Safety Limits**: Built-in max recursion depth to prevent infinite loops
- 📊 **Call Tracking**: Monitor API calls and tool usage
- 💬 **Interactive Mode**: Try custom tasks and see real-time tool execution
- 🔄 **Recursive Reasoning**: After tool execution, reasons about results and continues if needed

## Features

- 🔄 **Recursive Task Execution**: The agent can call itself to handle subtasks
- 🛡️ **Safety Limits**: Built-in max recursion depth to prevent infinite loops
- 📊 **Call Tracking**: Monitor how many API calls are made
- 🎯 **Flexible**: Works with any task that can be broken down into subtasks
- 💬 **Interactive Mode**: Try custom tasks and see real-time recursion

## Installation

### 1. Set up your DeepSeek API Key

First, get your API key from [DeepSeek](https://www.deepseek.com):

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY = 'your-api-key-here'
```

**Windows (CMD):**
```cmd
set DEEPSEEK_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY=your-api-key-here
```

### 2. Install Dependencies

```bash
pip3 install openai
```

## Usage

### Option 1: Run the Main Agent

```bash
python recursive_agent.py
```

This runs the agent with a default complex task that demonstrates recursion.

### Option 2: Run Examples

```bash
python examples.py
```

Choose from:
- Example 1: Simple task (no tools needed)
- Example 2: Web search task
- Example 3: Calculation task
- Example 4: Multi-tool task
- Interactive mode

### Option 3: Use in Your Code

```python
from recursive_agent import RecursiveAgent

# Create an agent
agent = RecursiveAgent(max_depth=3)

# Execute a task
result = agent.execute("Research quantum computing breakthroughs and provide a summary")

print(result)
print(f"API calls: {agent.call_count}")
print(f"Tools used: {agent.tool_call_count}")
```

## Configuration

### RecursiveAgent Parameters

```python
agent = RecursiveAgent(
    max_depth=3,              # Maximum recursion levels (default: 5)
    model="deepseek-chat"     # Model to use (default: deepseek-chat)
)
```

### Agent Stats

After execution, check:
- `agent.call_count` - Total API calls made
- `agent.tool_call_count` - Number of tools used
- `agent.call_count - agent.tool_call_count` - Reasoning steps without tools

## How It Works

1. **Task Submission**: You give the agent a task
2. **LLM Analysis**: The agent analyzes if tools are needed
3. **Tool Calling**: If needed, the agent calls the appropriate tool (e.g., web search) with a JSON block
4. **Tool Execution**: The tool gathers information and returns results
5. **Reasoning**: The agent reasons about the tool output and continues if needed
6. **Result Return**: Final answer combining all gathered information

## Tool Call Format

The agent uses this format to indicate tool usage:

```json
[TOOL_CALL]
{
  "tool": "web_search",
  "reasoning": "Why the tool is being called",
  "parameters": {
    "query": "search query",
    "num_results": 3
  }
}
[/TOOL_CALL]
```

## Available Tools

### 1. Web Search
Search the web for current information
```json
{
  "tool": "web_search",
  "reasoning": "To find current information about [topic]",
  "parameters": {
    "query": "search query",
    "num_results": 3
  }
}
```

### 2. Calculate
Perform mathematical calculations
```json
{
  "tool": "calculate",
  "reasoning": "To compute the value",
  "parameters": {
    "expression": "10 * (1.05 ** 10)"
  }
}
```

### 3. Get Info
Retrieve system information
```json
{
  "tool": "get_info",
  "reasoning": "To get current system information",
  "parameters": {}
}
```

## Example Tasks

### Example 1: Simple Query (No Tools)
```python
task = "What are the top 3 features of Python?"
# Agent answers directly without tools
```

### Example 2: Web Search Task
```python
task = """
What is the current state of renewable energy adoption? 
Search for recent information and provide an analysis of key trends.
"""
# Agent calls web_search tool to gather current information
```

### Example 3: Calculation Task
```python
task = """
Calculate compound interest for $10,000 at 5% annual interest for 10 years
and explain the result.
"""
# Agent calls calculate tool and reasons about the results
```

### Example 4: Multi-tool Task
```python
task = """
Research the latest developments in quantum computing and provide a summary.
Include recent milestones and key players in the field.
"""
# Agent may use web_search to gather current information
```

## Monitoring Agent Execution

The agent prints real-time information:

```
🤖 Tool-Using LLM Agent Started

  [Level 0] Agent Call #1: What is the current state of renewable energy...
  📤 Response: Renewable energy adoption has been accelerating...
  🔧 Tool Call (web_search): To find current statistics on renewable energy adoption
    🔍 Executing web search: 'renewable energy adoption 2024'
  📊 Tool Result: Web Search Results:...
  
    [Level 1] Agent Call #2: Based on the tool result, continue...
    📤 Response: Based on the latest data, renewable energy adoption...
    ✅ Task completed (no tools needed)

✅ Task completed (no tools needed)

📊 Final Result:
...

📈 Stats:
   - API calls made: 2
   - Tools used: 1
```

## Error Handling

- **Missing API Key**: The agent checks for `DEEPSEEK_API_KEY` and exits with a helpful message if not found
- **Max Depth Reached**: Recursion stops gracefully with a notification
- **JSON Parse Errors**: Invalid task JSON is caught and logged

## Tips

1. **Web Search**: Works best for current events, recent news, and factual information
2. **Calculations**: Use Python expressions (e.g., "10 * (1.05 ** 10)" for compound interest)
3. **Tool Selection**: The agent automatically decides if tools are needed
4. **Temperature**: Adjust `temperature` for more/less creative responses (0.0 - 2.0)
5. **Cost Management**: Each API call and tool use costs resources - monitor `agent.call_count` and `agent.tool_call_count`
6. **Max Depth**: Higher values allow more reasoning steps, lower values are faster and cheaper

## Troubleshooting

### "No results found for: [query]"
- The web search might not have good results for that query
- Try a more specific or different query
- Note: Free search APIs have limitations

### Agent not using tools
- Try tasks that explicitly ask for information lookup or calculation
- Some simple tasks don't require tools (the agent is smart about this)
- Adjust the task to hint at needing external information

### Too many API calls
- Reduce `max_depth`
- Ask more specific questions
- Check the `agent.tool_call_count` to see if tools are being used efficiently

## License

This is example code for using the DeepSeek API. See DeepSeek's terms for API usage.
