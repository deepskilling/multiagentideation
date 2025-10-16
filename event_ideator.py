"""
Event Ideation Tool - Uses the Multi-Agent System for Event Planning
"""
import sys
import json
from agents.base_agent import BaseAgent
from config import config


class EventIdeatorAgent(BaseAgent):
    """Specialized agent for generating event concepts and agendas"""
    
    def __init__(self):
        super().__init__(
            name="Event Ideator",
            model=config.GENERATOR_MODEL,
            role_description="You are an expert event strategist and facilitator who creates innovative, engaging event formats and agendas."
        )
    
    def execute(self, input_data):
        """Execute the agent's primary function"""
        if isinstance(input_data, dict):
            event_type = input_data.get("event_type", "Corporate Event")
            num_concepts = input_data.get("num_concepts", 5)
            return self.generate_event_concepts(event_type, num_concepts)
        return self.generate_event_concepts(str(input_data), 5)
    
    def generate_event_concepts(self, event_type: str, num_concepts: int = 5):
        """Generate innovative event format concepts"""
        
        prompt = f"""Generate {num_concepts} innovative event format concepts for a "{event_type}" event.

For each event format concept, provide:

1. **Format Name**: Creative, memorable name for this event format
2. **Challenge Solved**: What specific team/organizational challenge does this format address?
3. **Best For**: Which teams, roles, or situations benefit most?
4. **Key Activities**: List 5-7 specific sessions/activities with estimated durations
5. **Unique Approach**: What makes this format different from typical corporate events?
6. **Tools Needed**: Physical and digital tools required
7. **Budget Tier**: Small (< $5K), Medium ($5K-20K), or Large (> $20K)

Create formats that:
- Re-energize and inspire participants
- Drive concrete outcomes and action items
- Balance energy with depth
- Include interactive and collaborative elements
- Work for 25-100 participants
- Can adapt to in-person or hybrid delivery

Output as valid JSON array:
[
  {{
    "format_name": "Name of event format",
    "challenge_solved": "Specific problem this solves",
    "best_for": "Target audience description",
    "key_activities": [
      "Activity 1 - Duration and description",
      "Activity 2 - Duration and description",
      ...
    ],
    "unique_approach": "What makes this special",
    "tools_needed": ["Tool 1", "Tool 2", ...],
    "budget_tier": "Small/Medium/Large"
  }}
]

Generate {num_concepts} diverse, creative event formats now:"""

        self.log_message(f"Generating {num_concepts} event concepts for: {event_type}")
        
        response = self._call_llm(
            prompt=prompt,
            system_message=self.role_description,
            temperature=0.8,  # High creativity
            max_tokens=5000
        )
        
        # Parse response
        concepts = self._parse_concepts(response)
        self.log_message(f"Successfully parsed {len(concepts)} concepts")
        
        return concepts
    
    def _parse_concepts(self, response: str):
        """Parse LLM response into concept objects"""
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            concepts = json.loads(response)
            return concepts
            
        except json.JSONDecodeError as e:
            self.log_message(f"JSON parsing error: {e}")
            self.log_message(f"Response preview: {response[:500]}")
            return []
        except Exception as e:
            self.log_message(f"Unexpected error: {e}")
            return []
    
    def generate_detailed_agenda(self, concept):
        """Generate detailed hour-by-hour agenda for a chosen concept"""
        
        prompt = f"""Create a detailed, hour-by-hour agenda for this event format:

**Event Format**: {concept['format_name']}
**Purpose**: {concept['challenge_solved']}
**Target**: {concept['best_for']}
**Activities Overview**: {', '.join(concept['key_activities'][:3])}

Generate a FULL DAY agenda (8:00 AM - 5:00 PM) with:

1. **Detailed Timeline**: Every 15-30 minute block
2. **Session Details**: For each session include:
   - Time block
   - Session title
   - Objectives (what participants will achieve)
   - Format (presentation, workshop, breakout, etc.)
   - Facilitator notes
   - Materials needed
   - Transition/break notes

3. **Energizers**: Include 2-3 short energizer activities between heavy sessions

4. **Logistics**: Room setup, materials prep, tech requirements

5. **Takeaways**: What participants leave with

Output as JSON:
{{
  "event_title": "Full event title",
  "duration": "Full day (8 hours)",
  "participant_count": "25-50",
  "agenda": [
    {{
      "time": "8:00 AM - 8:30 AM",
      "session_title": "Session name",
      "objectives": ["Objective 1", "Objective 2"],
      "format": "Format description",
      "duration_minutes": 30,
      "facilitator_notes": "Key points for facilitator",
      "materials": ["Material 1", "Material 2"],
      "setup_notes": "Room/tech setup needed"
    }}
  ],
  "overall_flow": "Description of how the day flows",
  "success_metrics": ["How to measure success"],
  "preparation_checklist": ["Item 1", "Item 2"],
  "participant_takeaways": ["Takeaway 1", "Takeaway 2"]
}}

Create a comprehensive, professional agenda now:"""

        response = self._call_llm(
            prompt=prompt,
            system_message=self.role_description,
            temperature=0.7,
            max_tokens=6000
        )
        
        return self._parse_json(response)
    
    def _parse_json(self, response: str):
        """Parse JSON response"""
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            return json.loads(response)
        except Exception as e:
            return {"error": str(e), "raw": response[:500]}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Event Ideation using Multi-Agent System")
    parser.add_argument("--event-type", default="Re-Ignite", help="Type of event (default: Re-Ignite)")
    parser.add_argument("--num-concepts", type=int, default=5, help="Number of concepts to generate")
    parser.add_argument("--generate-agenda", type=int, help="Generate detailed agenda for concept # (1-5)")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(f"🎪 {args.event_type.upper()} EVENT IDEATION")
    print("   Powered by Your Multi-Agent System")
    print("="*80)
    
    agent = EventIdeatorAgent()
    
    # Generate concepts
    print(f"\n⏳ Generating {args.num_concepts} innovative event format concepts...")
    print(f"   Using Claude Sonnet 4.5 via AWS Bedrock\n")
    
    concepts = agent.generate_event_concepts(args.event_type, args.num_concepts)
    
    if not concepts:
        print("❌ Failed to generate concepts. Check logs.")
        return
    
    print(f"✅ Generated {len(concepts)} event format concepts!\n")
    
    # Display concepts
    for idx, concept in enumerate(concepts, 1):
        print(f"\n{'='*80}")
        print(f"CONCEPT #{idx}: {concept.get('format_name', 'Untitled')}")
        print(f"{'='*80}")
        print(f"\n💡 Solves: {concept.get('challenge_solved', 'N/A')}\n")
        print(f"🎯 Best For: {concept.get('best_for', 'N/A')}\n")
        print(f"📋 Key Activities:")
        for activity in concept.get('key_activities', []):
            print(f"   • {activity}")
        print(f"\n✨ Unique: {concept.get('unique_approach', 'N/A')}\n")
        print(f"🛠️  Tools: {', '.join(concept.get('tools_needed', []))}")
        print(f"💰 Budget: {concept.get('budget_tier', 'N/A')}")
    
    # Save concepts
    output_file = 'reports/event_concepts.json'
    with open(output_file, 'w') as f:
        json.dump({
            "event_type": args.event_type,
            "concepts": concepts
        }, f, indent=2)
    
    print(f"\n\n{'='*80}")
    print(f"✅ Concepts saved to: {output_file}")
    print("\n💡 Next: Generate detailed agenda for your favorite concept:")
    print(f"   python event_ideator.py --event-type '{args.event_type}' --generate-agenda 1")
    print("="*80 + "\n")
    
    # Generate detailed agenda if requested
    if args.generate_agenda:
        idx = args.generate_agenda - 1
        if 0 <= idx < len(concepts):
            print(f"\n⏳ Generating detailed agenda for Concept #{args.generate_agenda}...")
            agenda = agent.generate_detailed_agenda(concepts[idx])
            
            agenda_file = f'reports/detailed_agenda_concept{args.generate_agenda}.json'
            with open(agenda_file, 'w') as f:
                json.dump(agenda, f, indent=2)
            
            print(f"✅ Detailed agenda saved to: {agenda_file}\n")


if __name__ == "__main__":
    main()

