# app/input_collector.py

import os
import json
import re
from typing import Dict, List, Optional, Tuple

class InputCollector:
    def __init__(self, openai_client=None):
        """Initialize the input collector with agent configurations."""
        self.config_dir = os.path.join(os.path.dirname(__file__), 'agent_configs')
        self.agent_questions = self._load_agent_questions()
        self.openai_client = openai_client
        
    def _load_agent_questions(self) -> Dict:
        """Load questions for each agent from their respective files."""
        questions = {}
        
        # Load compensation questions
        comp_file = os.path.join(self.config_dir, 'compensation_questions.txt')
        questions['compensation'] = self._parse_questions_file(comp_file)
        
        # Load policy questions
        policy_file = os.path.join(self.config_dir, 'policy_questions.txt')
        questions['policy'] = self._parse_questions_file(policy_file)
        
        return questions
    
    def _parse_questions_file(self, file_path: str) -> List[Dict]:
        """Parse a questions file and extract structured question data."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            questions = []
            # Split by numbered questions (1., 2., etc.)
            question_blocks = re.split(r'\n\d+\.\s+\*\*', content)
            
            for i, block in enumerate(question_blocks[1:], 1):  # Skip first empty block
                lines = block.strip().split('\n')
                if not lines:
                    continue
                    
                # Extract question title
                title_line = lines[0]
                title = title_line.split('**')[0].strip()
                
                # Extract question text
                question_text = ""
                options = []
                format_info = ""
                
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('- Question:'):
                        question_text = line.replace('- Question:', '').strip().strip('"')
                    elif line.startswith('- Options:'):
                        options_text = line.replace('- Options:', '').strip()
                        options = [opt.strip() for opt in options_text.split(',')]
                    elif line.startswith('- Format:'):
                        format_info = line.replace('- Format:', '').strip()
                    elif line.startswith('- Examples:'):
                        format_info = line.replace('- Examples:', '').strip()
                
                questions.append({
                    'id': i,
                    'title': title,
                    'question': question_text,
                    'options': options,
                    'format': format_info
                })
            
            return questions
            
        except Exception as e:
            print(f"Error parsing questions file {file_path}: {e}")
            return []
    
    def get_intro_message(self) -> str:
        """Get the intro/welcome message."""
        try:
            intro_file = os.path.join(self.config_dir, 'intro_message.txt')
            with open(intro_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading intro message: {e}")
            return "Welcome to Global IQ! How can I help you with your mobility needs?"
    
    def get_both_choice_message(self) -> str:
        """Get the message for when both policy and compensation are needed."""
        try:
            both_file = os.path.join(self.config_dir, 'both_choice_message.txt')
            with open(both_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading both choice message: {e}")
            return "Would you like to start with policy analysis or compensation calculation?"
    
    def get_confirmation_message(self, agent_type: str) -> str:
        """Get confirmation message for a specific agent type."""
        try:
            conf_file = os.path.join(self.config_dir, 'confirmation_messages.txt')
            with open(conf_file, 'r') as f:
                content = f.read()
            
            # Extract the relevant section based on agent type
            if agent_type == "compensation":
                # Find the compensation confirmation section
                start = content.find("## Compensation Confirmation")
                end = content.find("## Policy Confirmation")
                if start != -1 and end != -1:
                    return content[start:end].replace("## Compensation Confirmation\n", "").strip()
            elif agent_type == "policy":
                # Find the policy confirmation section
                start = content.find("## Policy Confirmation")
                end = content.find("## General Help")
                if start != -1 and end != -1:
                    return content[start:end].replace("## Policy Confirmation\n", "").strip()
            
            # Fallback messages
            if agent_type == "compensation":
                return "I detected you might need compensation analysis. Would you like me to start the questionnaire? (Reply 'Yes' to continue or 'No' if this isn't what you need)"
            else:
                return "I detected you might need policy analysis. Would you like me to start the questionnaire? (Reply 'Yes' to continue or 'No' if this isn't what you need)"
                
        except Exception as e:
            print(f"Error loading confirmation message: {e}")
            return f"Would you like me to start the {agent_type} analysis? Reply 'Yes' to continue."
    
    def get_general_help_message(self) -> str:
        """Get the general help message."""
        try:
            conf_file = os.path.join(self.config_dir, 'confirmation_messages.txt')
            with open(conf_file, 'r') as f:
                content = f.read()
            
            # Extract the general help section
            start = content.find("## General Help")
            if start != -1:
                return content[start:].replace("## General Help\n", "").strip()
            
            return "I'm Global IQ, your AI mobility assistant. I can help with compensation calculations and policy analysis. What can I help you with?"
                
        except Exception as e:
            print(f"Error loading general help message: {e}")
            return "I'm Global IQ, your AI mobility assistant. What can I help you with today?"
    
    async def ai_spell_check_and_correct(self, user_input: str, question_title: str) -> tuple:
        """Use GenAI to check and correct spelling/formatting errors in user input."""
        if not self.openai_client:
            return user_input.strip(), []
        
        try:
            prompt = f"""You are a helpful assistant that corrects spelling errors and improves formatting for global mobility data.

Question context: {question_title}
User input: "{user_input}"

Tasks:
1. Correct any spelling errors
2. Standardize location names (e.g., "londn" → "London, UK")
3. Format currencies properly (e.g., "50k euros" → "50,000 EUR")
4. Fix common typos and formatting issues
5. Keep the original meaning intact

Respond in this exact format:
CORRECTED: [corrected text]
SUGGESTIONS: [list any changes made, or "None" if no changes]

Example:
CORRECTED: London, UK
SUGGESTIONS: Fixed spelling: "londn" → "London", added country code"""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Use faster, cheaper model for spell checking
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the response
            corrected = user_input.strip()
            suggestions = []
            
            lines = result.split('\n')
            for line in lines:
                if line.startswith('CORRECTED:'):
                    corrected = line.replace('CORRECTED:', '').strip()
                elif line.startswith('SUGGESTIONS:'):
                    suggestion_text = line.replace('SUGGESTIONS:', '').strip()
                    if suggestion_text and suggestion_text.lower() != 'none':
                        suggestions.append(suggestion_text)
            
            return corrected, suggestions
            
        except Exception as e:
            print(f"Error in AI spell check: {e}")
            return user_input.strip(), []
    
    def start_collection(self, agent_type: str, user_session: Dict) -> Tuple[str, Dict]:
        """
        Start input collection for a specific agent type.
        
        Args:
            agent_type: 'compensation' or 'policy'
            user_session: Current user session data
            
        Returns:
            Tuple of (next_question, updated_session)
        """
        if agent_type not in self.agent_questions:
            return "Sorry, I don't have questions configured for this agent type.", user_session
        
        # Initialize collection state
        collection_key = f"{agent_type}_collection"
        if collection_key not in user_session:
            user_session[collection_key] = {
                'current_question': 0,
                'answers': {},
                'completed': False
            }
        
        return self._get_next_question(agent_type, user_session)
    
    def process_answer(self, agent_type: str, user_input: str, user_session: Dict) -> Tuple[str, Dict, bool]:
        """
        Process a user's answer and return the next question or completion status.
        
        Args:
            agent_type: 'compensation' or 'policy'
            user_input: User's answer
            user_session: Current user session data
            
        Returns:
            Tuple of (response_message, updated_session, is_completed)
        """
        collection_key = f"{agent_type}_collection"
        
        if collection_key not in user_session:
            return self.start_collection(agent_type, user_session)
        
        collection_state = user_session[collection_key]
        
        # Check if we're awaiting confirmation
        if collection_state.get('awaiting_confirmation', False):
            return self._handle_confirmation_response(agent_type, user_input, user_session)
        
        current_q_index = collection_state['current_question']
        questions = self.agent_questions[agent_type]
        
        if current_q_index >= len(questions):
            return "Collection already completed!", user_session, True
        
        # Store the answer
        current_question = questions[current_q_index]
        collection_state['answers'][current_question['title']] = user_input.strip()
        
        # Move to next question
        collection_state['current_question'] += 1
        
        # Check if we're done with questions
        if collection_state['current_question'] >= len(questions):
            collection_state['awaiting_confirmation'] = True
            return self._generate_confirmation_summary(agent_type, collection_state['answers']), user_session, False
        
        # Get next question
        next_question, updated_session = self._get_next_question(agent_type, user_session)
        return next_question, updated_session, False
    
    def _get_next_question(self, agent_type: str, user_session: Dict) -> Tuple[str, Dict]:
        """Get the next question for the user."""
        collection_key = f"{agent_type}_collection"
        collection_state = user_session[collection_key]
        current_q_index = collection_state['current_question']
        questions = self.agent_questions[agent_type]
        
        if current_q_index >= len(questions):
            return "All questions completed!", user_session
        
        question = questions[current_q_index]
        
        # Format the question
        question_text = f"**{question['title']}**\n\n{question['question']}"
        
        if question['options']:
            question_text += f"\n\n**Options:** {', '.join(question['options'])}"
        
        if question['format']:
            question_text += f"\n\n*Format: {question['format']}*"
        
        # Add progress indicator
        progress = f"\n\n📊 Question {current_q_index + 1} of {len(questions)}"
        question_text += progress
        
        return question_text, user_session
    
    def _generate_confirmation_summary(self, agent_type: str, answers: Dict) -> str:
        """Generate a confirmation summary asking user to verify their data."""
        agent_name = "Compensation Calculator" if agent_type == "compensation" else "Policy Analyzer"
        
        message = f"📋 **Final Confirmation - {agent_name}**\n\n"
        message += "Please review the information you've provided:\n\n"
        
        for key, value in answers.items():
            message += f"• **{key}:** {value}\n"
        
        message += "\n❓ **Is all this information correct?**\n\n"
        message += "• Type **'yes'** or **'confirm'** to proceed with the analysis\n"
        message += "• Type **'no'** or **'edit'** if you need to make changes\n"
        
        return message
    
    def _generate_completion_message(self, agent_type: str, answers: Dict) -> str:
        """Generate a completion message after confirmation."""
        agent_name = "Compensation Calculator" if agent_type == "compensation" else "Policy Analyzer"
        
        message = f"✅ **{agent_name} - Processing Confirmed!**\n\n"
        message += f"🔄 Now processing your data through our {agent_name} AI engine...\n\n"
        message += f"*This may take a few moments while we run the calculations and analysis.*"
        
        return message
    
    def _handle_confirmation_response(self, agent_type: str, user_input: str, user_session: Dict) -> Tuple[str, Dict, bool]:
        """Handle user's confirmation response."""
        collection_key = f"{agent_type}_collection"
        collection_state = user_session[collection_key]
        user_response = user_input.lower().strip()
        
        # Check for confirmation (yes/confirm)
        if user_response in ['yes', 'y', 'confirm', 'confirmed', 'correct', 'ok', 'okay']:
            collection_state['completed'] = True
            collection_state['awaiting_confirmation'] = False
            completion_message = self._generate_completion_message(agent_type, collection_state['answers'])
            return completion_message, user_session, True
        
        # Check for rejection (no/edit)
        elif user_response in ['no', 'n', 'edit', 'change', 'incorrect', 'wrong']:
            # Reset to allow editing - go back to first question
            collection_state['current_question'] = 0
            collection_state['awaiting_confirmation'] = False
            # Keep the existing answers so user can see them
            
            edit_message = f"📝 **No problem! Let's edit your information.**\n\n"
            edit_message += f"I'll ask you the questions again. Your previous answers will be shown, and you can either:\n"
            edit_message += f"• Keep the same answer by pressing Enter\n"
            edit_message += f"• Type a new answer to replace it\n\n"
            edit_message += f"Let's start over:\n\n"
            
            # Get the first question again
            next_question, updated_session = self._get_next_question(agent_type, user_session)
            return edit_message + next_question, updated_session, False
        
        # Invalid response
        else:
            invalid_message = f"❌ **Please respond with:**\n\n"
            invalid_message += f"• **'yes'** or **'confirm'** to proceed\n"
            invalid_message += f"• **'no'** or **'edit'** to make changes\n\n"
            invalid_message += f"Your response: '{user_input}' was not recognized."
            return invalid_message, user_session, False
    
    def get_collected_data(self, agent_type: str, user_session: Dict) -> Optional[Dict]:
        """Get the collected data for an agent type."""
        collection_key = f"{agent_type}_collection"
        if collection_key in user_session and user_session[collection_key].get('completed'):
            return user_session[collection_key]['answers']
        return None
    
    def is_collection_in_progress(self, agent_type: str, user_session: Dict) -> bool:
        """Check if collection is currently in progress for an agent type."""
        collection_key = f"{agent_type}_collection"
        return (collection_key in user_session and 
                not user_session[collection_key].get('completed', False))
