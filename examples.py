#!/usr/bin/env python3
"""
Example usage of the tool-using agent with different tasks
"""

import os
from recursive_agent import RecursiveAgent


def example_1_simple_task():
    """Example 1: A simple task that doesn't need tools"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Task (No Tools Needed)")
    print("="*60)
    
    agent = RecursiveAgent(max_depth=2)
    task = "What are the top 3 features of Python?"
    result = agent.execute(task)
    print(f"\nResult:\n{result}")
    print(f"\nTools used: {agent.tool_call_count}")


def example_2_web_search_task():
    """Example 2: A task requiring web search"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Web Search Task")
    print("="*60)
    
    agent = RecursiveAgent(max_depth=3)
    task = """
    What is the current state of renewable energy adoption? 
    Search for recent information and provide an analysis of key trends.
    """
    result = agent.execute(task)
    print(f"\nResult:\n{result}")
    print(f"\nTools used: {agent.tool_call_count}")


def example_3_calculation_task():
    """Example 3: A task requiring calculations"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Calculation Task")
    print("="*60)
    
    agent = RecursiveAgent(max_depth=2)
    task = """
    I need to calculate compound interest for an investment of $10,000 at 5% annual interest for 10 years.
    Can you calculate this and explain the result?
    """
    result = agent.execute(task)
    print(f"\nResult:\n{result}")
    print(f"\nTools used: {agent.tool_call_count}")


def example_4_multi_tool_task():
    """Example 4: A complex task that might use multiple tools"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Multi-Tool Task")
    print("="*60)
    
    agent = RecursiveAgent(max_depth=3)
    task = """
    Research the latest developments in quantum computing and provide a summary.
    Include recent milestones and key players in the field if you can find current information.
    """
    result = agent.execute(task)
    print(f"\nResult:\n{result}")
    print(f"\nTools used: {agent.tool_call_count}")


def interactive_mode():
    """Interactive mode where user can input custom tasks"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nEnter your task (or 'quit' to exit):")
    print("(The agent can use tools like web search to help answer)\n")
    
    agent = RecursiveAgent(max_depth=3)
    
    while True:
        user_task = input("\n🎯 Task: ").strip()
        
        if user_task.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_task:
            continue
        
        result = agent.execute(user_task)
        print(f"\n✅ Result:\n{result}")
        print(f"\n📊 Stats:")
        print(f"   - API calls: {agent.call_count}")
        print(f"   - Tools used: {agent.tool_call_count}")
        
        agent.reset()


if __name__ == "__main__":
    try:
        print("🤖 Tool-Using Agent Examples")
        print("\nChoose an option:")
        print("1. Run Example 1 (Simple Task - No Tools)")
        print("2. Run Example 2 (Web Search Task)")
        print("3. Run Example 3 (Calculation Task)")
        print("4. Run Example 4 (Multi-Tool Task)")
        print("5. Interactive Mode")
        print("6. Run All Examples")
        
        choice = input("\nSelect (1-6): ").strip()
        
        if choice == '1':
            example_1_simple_task()
        elif choice == '2':
            example_2_web_search_task()
        elif choice == '3':
            example_3_calculation_task()
        elif choice == '4':
            example_4_multi_tool_task()
        elif choice == '5':
            interactive_mode()
        elif choice == '6':
            example_1_simple_task()
            example_2_web_search_task()
            example_3_calculation_task()
            example_4_multi_tool_task()
        else:
            print("Invalid choice")
    except FileNotFoundError:
        print("❌ Error: DEEPSEEK_API_KEY is not set")
        print("Set the DEEPSEEK_API_KEY environment variable (see .env.example)")
        exit(1)
