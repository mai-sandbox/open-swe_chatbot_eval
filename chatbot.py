"""
Multi-Agent Management Chat Interface

This module provides a command-line interface for interacting with the multi-agent
management system. It imports and runs the compiled graph from agent.py, supporting
commands to start agents, check status, cancel runs, and engage in natural
conversation about agent progress.
"""

import asyncio
import sys
from typing import Optional
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from agent import app, create_initial_state, SupervisorState

load_dotenv()

class MultiAgentChatInterface:
    """Command-line interface for the multi-agent management system"""
    
    def __init__(self):
        self.state: Optional[SupervisorState] = None
        self.session_active = True
        
    def display_welcome(self):
        """Display welcome message and available commands"""
        print("🤖 Multi-Agent Management System")
        print("=" * 50)
        print("Welcome to the Multi-Agent Supervisor!")
        print("\nI can help you manage and monitor background agents.")
        print("\n📋 What I can do:")
        print("• Start remote agents for specific tasks")
        print("• Monitor agent progress and status")
        print("• Cancel running agent tasks")
        print("• Provide real-time updates on agent activities")
        print("• Answer questions about agent capabilities")
        print("\n🔧 Available Agents:")
        print("• Research Agent - Data gathering and analysis")
        print("• Analysis Agent - Pattern recognition and insights")
        print("• Task Agent - Workflow execution and operations")
        print("\n💡 Example commands:")
        print("• 'Start a research agent to analyze market trends'")
        print("• 'Check the status of all running agents'")
        print("• 'Cancel the last research task'")
        print("• 'List all active agents'")
        print("\nType 'help' for more commands or 'quit' to exit.")
        print("-" * 50)
    
    def display_help(self):
        """Display help information"""
        print("\n📖 Help - Multi-Agent Management Commands")
        print("=" * 50)
        print("\n🚀 Starting Agents:")
        print("• 'Start [agent] to [task]' - Start a specific agent")
        print("• 'Run analysis on [topic]' - Start analysis agent")
        print("• 'Research [topic]' - Start research agent")
        print("• 'Execute [task]' - Start task agent")
        print("\n📊 Monitoring & Status:")
        print("• 'Status' or 'Check status' - View all agent status")
        print("• 'List agents' or 'Show active' - List running agents")
        print("• 'Progress on [run_id]' - Check specific run progress")
        print("• 'Results for [run_id]' - Get completed run results")
        print("\n🛑 Control Commands:")
        print("• 'Cancel [run_id]' - Cancel specific run")
        print("• 'Stop all' - Cancel all running agents")
        print("• 'Pause [run_id]' - Pause specific run")
        print("\n🔧 System Commands:")
        print("• 'help' - Show this help message")
        print("• 'clear' - Clear conversation history")
        print("• 'quit' or 'exit' - Exit the system")
        print("\n💬 Natural Language:")
        print("You can also ask questions in natural language!")
        print("Example: 'How are my agents doing?' or 'What can you help me with?'")
        print("-" * 50)
    
    def process_special_commands(self, user_input: str) -> bool:
        """Process special system commands. Returns True if command was handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit', 'q']:
            print("\n👋 Shutting down Multi-Agent Management System...")
            print("All active agents will continue running in the background.")
            print("Thank you for using the Multi-Agent Supervisor!")
            self.session_active = False
            return True
            
        elif command in ['help', 'h', '?']:
            self.display_help()
            return True
            
        elif command in ['clear', 'cls']:
            # Clear conversation history but keep agent state
            if self.state:
                self.state["messages"] = []
            print("\n🧹 Conversation history cleared.")
            print("Agent configurations and active runs preserved.")
            return True
            
        elif command in ['status', 'list', 'show']:
            # Quick status check
            print("\n📊 Quick Status Check:")
            print("Use natural language like 'What agents are running?' for detailed status.")
            return False  # Let the agent handle the detailed response
            
        return False
    
    async def run_conversation(self):
        """Main conversation loop"""
        self.display_welcome()
        self.state = create_initial_state()
        
        while self.session_active:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self.process_special_commands(user_input):
                    continue
                
                # Add user message to state
                self.state["messages"].append(HumanMessage(content=user_input))
                
                # Show thinking indicator
                print("🤔 Supervisor thinking...")
                
                # Run the multi-agent supervisor
                try:
                    result_state = await app.ainvoke(self.state)
                    self.state = result_state
                    
                    # Display the supervisor's response
                    if result_state["messages"]:
                        latest_message = result_state["messages"][-1]
                        if isinstance(latest_message, AIMessage):
                            print(f"\n🤖 Supervisor: {latest_message.content}")
                        
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    print("The supervisor encountered an issue. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user.")
                print("Type 'quit' to exit properly or continue chatting.")
                continue
                
            except EOFError:
                print("\n\n👋 Session ended.")
                break
                
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                print("Please try again or type 'quit' to exit.")
    
    def run(self):
        """Run the chat interface"""
        try:
            asyncio.run(self.run_conversation())
        except KeyboardInterrupt:
            print("\n\n👋 Multi-Agent Management System shutdown complete.")
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            print("Please check your configuration and try again.")
            sys.exit(1)

def main():
    """Main entry point for the multi-agent chat interface"""
    interface = MultiAgentChatInterface()
    interface.run()

if __name__ == "__main__":
    main()




