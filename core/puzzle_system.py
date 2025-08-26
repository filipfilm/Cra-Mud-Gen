"""
Puzzle System for Cra-mud-gen
Implements interactive puzzles that block progression
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import re

class PuzzleType(Enum):
    CONSTELLATION = "constellation"    # Arrange celestial patterns
    CRYSTAL_ORDER = "crystal_order"    # Arrange crystals in correct sequence
    MUSICAL_NOTES = "musical_notes"    # Play correct musical sequence
    RIDDLE = "riddle"                  # Answer a riddle
    COMBINATION = "combination"        # Enter correct combination
    PATTERN_MATCHING = "pattern"       # Match visual patterns

class PuzzleStatus(Enum):
    INACTIVE = "inactive"      # Puzzle not encountered yet
    ACTIVE = "active"         # Currently solvable
    SOLVED = "solved"         # Successfully completed
    FAILED = "failed"         # Failed (if applicable)

@dataclass
class PuzzleSolution:
    """Represents a puzzle solution"""
    keywords: List[str] = field(default_factory=list)  # Keywords that solve it
    exact_phrase: Optional[str] = None                  # Exact phrase needed
    pattern: Optional[str] = None                       # Regex pattern to match
    case_sensitive: bool = False

@dataclass
class Puzzle:
    """Individual puzzle definition"""
    id: str
    name: str
    description: str
    puzzle_type: PuzzleType
    location: str                           # Room where puzzle appears
    blocking_directions: List[str] = field(default_factory=list)  # Directions blocked until solved
    hints: List[str] = field(default_factory=list)
    solution: PuzzleSolution = field(default_factory=PuzzleSolution)
    status: PuzzleStatus = PuzzleStatus.INACTIVE
    attempts: int = 0
    max_attempts: int = 0                   # 0 = unlimited
    rewards: Dict[str, Any] = field(default_factory=dict)
    
    def is_blocking_direction(self, direction: str) -> bool:
        """Check if this puzzle blocks a specific direction"""
        return direction.lower() in [d.lower() for d in self.blocking_directions]
    
    def check_solution(self, user_input: str) -> bool:
        """Check if user input solves the puzzle"""
        self.attempts += 1
        
        # Check exact phrase match
        if self.solution.exact_phrase:
            if self.solution.case_sensitive:
                return user_input.strip() == self.solution.exact_phrase
            else:
                return user_input.strip().lower() == self.solution.exact_phrase.lower()
        
        # Check pattern match
        if self.solution.pattern:
            flags = 0 if self.solution.case_sensitive else re.IGNORECASE
            return bool(re.search(self.solution.pattern, user_input, flags))
        
        # Check keywords
        if self.solution.keywords:
            input_lower = user_input.lower() if not self.solution.case_sensitive else user_input
            for keyword in self.solution.keywords:
                check_word = keyword if self.solution.case_sensitive else keyword.lower()
                if check_word in input_lower:
                    return True
        
        return False
    
    def get_attempts_left(self) -> Optional[int]:
        """Get remaining attempts, or None if unlimited"""
        if self.max_attempts == 0:
            return None
        return max(0, self.max_attempts - self.attempts)
    
    def is_failed(self) -> bool:
        """Check if puzzle has failed due to too many attempts"""
        return (self.max_attempts > 0 and 
                self.attempts >= self.max_attempts and 
                self.status != PuzzleStatus.SOLVED)

class PuzzleSystem:
    """Manages all puzzles in the game"""
    
    def __init__(self, llm_interface=None):
        self.puzzles: Dict[str, Puzzle] = {}
        self.active_puzzles: Dict[str, str] = {}  # location -> puzzle_id mapping
        self.llm = llm_interface
        
    def add_puzzle(self, puzzle: Puzzle):
        """Add a puzzle to the system"""
        self.puzzles[puzzle.id] = puzzle
        
    def activate_puzzle(self, puzzle_id: str) -> bool:
        """Activate a puzzle at its designated location"""
        if puzzle_id in self.puzzles:
            puzzle = self.puzzles[puzzle_id]
            puzzle.status = PuzzleStatus.ACTIVE
            self.active_puzzles[puzzle.location] = puzzle_id
            return True
        return False
    
    def get_puzzle_at_location(self, location: str) -> Optional[Puzzle]:
        """Get active puzzle at a specific location"""
        if location in self.active_puzzles:
            puzzle_id = self.active_puzzles[location]
            return self.puzzles.get(puzzle_id)
        return None
    
    def is_direction_blocked(self, location: str, direction: str) -> Tuple[bool, Optional[Puzzle]]:
        """Check if a direction is blocked by a puzzle"""
        puzzle = self.get_puzzle_at_location(location)
        if puzzle and puzzle.status == PuzzleStatus.ACTIVE:
            if puzzle.is_blocking_direction(direction):
                return True, puzzle
        return False, None
    
    def attempt_puzzle(self, location: str, user_input: str) -> Dict[str, Any]:
        """Attempt to solve a puzzle"""
        puzzle = self.get_puzzle_at_location(location)
        if not puzzle or puzzle.status != PuzzleStatus.ACTIVE:
            return {"success": False, "message": "No active puzzle here."}
        
        # Check if puzzle has already failed
        if puzzle.is_failed():
            return {"success": False, "message": "This puzzle can no longer be attempted."}
        
        # Try to solve
        if puzzle.check_solution(user_input):
            puzzle.status = PuzzleStatus.SOLVED
            del self.active_puzzles[location]  # Remove from active puzzles
            
            result = {
                "success": True,
                "message": f"🎉 Puzzle solved: {puzzle.name}!",
                "puzzle": puzzle,
                "rewards": puzzle.rewards
            }
            
            return result
        else:
            # Failed attempt
            attempts_left = puzzle.get_attempts_left()
            if attempts_left is not None and attempts_left == 0:
                puzzle.status = PuzzleStatus.FAILED
                return {
                    "success": False,
                    "message": f"❌ Incorrect! You've run out of attempts for {puzzle.name}.",
                    "puzzle": puzzle,
                    "failed": True
                }
            else:
                message = f"❌ That's not quite right."
                if attempts_left is not None:
                    message += f" {attempts_left} attempts remaining."
                
                # Maybe give a hint after a few failed attempts
                if puzzle.attempts >= 2 and puzzle.hints:
                    hint_index = min(len(puzzle.hints) - 1, puzzle.attempts - 2)
                    message += f"\n💡 Hint: {puzzle.hints[hint_index]}"
                
                return {
                    "success": False,
                    "message": message,
                    "puzzle": puzzle
                }
    
    def create_story_puzzles(self, story_beats: List[str], theme: str = "fantasy") -> List[Puzzle]:
        """Create puzzles based on story beats"""
        puzzles = []
        
        for i, beat in enumerate(story_beats):
            puzzle = self._parse_story_beat_to_puzzle(beat, i, theme)
            if puzzle:
                puzzles.append(puzzle)
                self.add_puzzle(puzzle)
        
        return puzzles
    
    def _parse_story_beat_to_puzzle(self, beat: str, index: int, theme: str) -> Optional[Puzzle]:
        """Convert a story beat into an LLM-generated puzzle"""
        if not self.llm:
            return self._create_fallback_puzzle(beat, index, theme)
        
        try:
            return self._generate_dynamic_puzzle(beat, index, theme)
        except Exception as e:
            print(f"Failed to generate dynamic puzzle: {e}")
            return self._create_fallback_puzzle(beat, index, theme)
    
    def _generate_dynamic_puzzle(self, beat: str, index: int, theme: str) -> Optional[Puzzle]:
        """Generate a dynamic puzzle using LLM based on story beat context"""
        
        # Create a comprehensive prompt for puzzle generation
        prompt = f"""Create a creative, challenging puzzle for a {theme} adventure game based on this story element:

STORY CONTEXT: "{beat}"

Generate a puzzle that fits this context. The puzzle should be:
1. Thematically appropriate for {theme} setting
2. Related to the story beat above
3. Intellectually challenging but solvable
4. Require knowledge, riddles, word puzzles, or logical sequences

PUZZLE TYPES TO CHOOSE FROM:
- RIDDLE: A clever riddle with wordplay or logic
- KNOWLEDGE: Questions about mythology, history, nature, or lore
- SEQUENCE: Number patterns, word sequences, or logical progressions  
- WORD_PUZZLE: Anagrams, word associations, or linguistic challenges
- LOGIC: Deduction puzzles or reasoning challenges

Provide your response in this EXACT format:

PUZZLE_TYPE: [Choose one type from above]
NAME: [Creative puzzle name]
DESCRIPTION: [Atmospheric description of what the player sees - 2-3 sentences]
QUESTION: [The actual puzzle question or challenge]
ANSWER: [The correct answer - single word or short phrase]
HINT1: [First helpful hint]
HINT2: [Second helpful hint]  
HINT3: [Third helpful hint if needed]
DIFFICULTY: [EASY/MEDIUM/HARD]

Make it engaging and immersive!"""

        try:
            # Get LLM response
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_response(prompt)
            else:
                response = self.llm.generate_response(prompt)
                
            # Parse the response into a puzzle
            return self._parse_llm_puzzle_response(response, beat, index, theme)
            
        except Exception as e:
            print(f"Error generating puzzle with LLM: {e}")
            return None
    
    def _parse_llm_puzzle_response(self, response: str, beat: str, index: int, theme: str) -> Optional[Puzzle]:
        """Parse LLM response into a Puzzle object"""
        try:
            lines = response.strip().split('\n')
            puzzle_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key in ['PUZZLE_TYPE', 'NAME', 'DESCRIPTION', 'QUESTION', 'ANSWER', 'HINT1', 'HINT2', 'HINT3', 'DIFFICULTY']:
                        puzzle_data[key] = value
            
            # Validate required fields
            required_fields = ['NAME', 'DESCRIPTION', 'QUESTION', 'ANSWER']
            if not all(field in puzzle_data for field in required_fields):
                print(f"Missing required puzzle fields: {required_fields}")
                return None
            
            # Determine puzzle type
            puzzle_type_map = {
                'RIDDLE': PuzzleType.RIDDLE,
                'KNOWLEDGE': PuzzleType.RIDDLE,  # Use riddle type for knowledge questions
                'SEQUENCE': PuzzleType.PATTERN_MATCHING,
                'WORD_PUZZLE': PuzzleType.RIDDLE,
                'LOGIC': PuzzleType.RIDDLE
            }
            
            puzzle_type = puzzle_type_map.get(
                puzzle_data.get('PUZZLE_TYPE', 'RIDDLE'), 
                PuzzleType.RIDDLE
            )
            
            # Build description with question
            full_description = puzzle_data['DESCRIPTION']
            if puzzle_data.get('QUESTION'):
                full_description += f"\n\n{puzzle_data['QUESTION']}"
            
            # Collect hints
            hints = []
            for hint_key in ['HINT1', 'HINT2', 'HINT3']:
                if hint_key in puzzle_data and puzzle_data[hint_key]:
                    hints.append(puzzle_data[hint_key])
            
            # Determine max attempts based on difficulty
            difficulty = puzzle_data.get('DIFFICULTY', 'MEDIUM').upper()
            max_attempts = {'EASY': 5, 'MEDIUM': 3, 'HARD': 2}.get(difficulty, 3)
            
            # Determine location based on index
            locations = [
                f"north_{index + 2}", f"east_{index + 1}", f"chamber_{index}", 
                f"west_{index + 1}", f"south_{index + 2}", f"up_{index + 1}"
            ]
            location = locations[index % len(locations)]
            
            # Create multiple possible answers (variations of the main answer)
            main_answer = puzzle_data['ANSWER'].lower().strip()
            answer_keywords = [main_answer]
            
            # Add common variations
            if ' ' in main_answer:
                # Add without spaces
                answer_keywords.append(main_answer.replace(' ', ''))
                # Add individual words
                answer_keywords.extend(main_answer.split())
            
            # Add plural/singular variations
            if main_answer.endswith('s'):
                answer_keywords.append(main_answer[:-1])
            else:
                answer_keywords.append(main_answer + 's')
            
            # Create puzzle
            puzzle = Puzzle(
                id=f"llm_puzzle_{index}",
                name=puzzle_data['NAME'],
                description=full_description,
                puzzle_type=puzzle_type,
                location=location,
                blocking_directions=["north", "east", "west"] if index % 2 == 0 else ["south", "up"],
                hints=hints,
                solution=PuzzleSolution(
                    keywords=answer_keywords,
                    case_sensitive=False
                ),
                max_attempts=max_attempts,
                rewards={
                    "experience": 30 + (index * 20),
                    "gold": 50 + (index * 25),
                    "items": [f"puzzle_reward_{index}", "wisdom_token"]
                }
            )
            
            return puzzle
            
        except Exception as e:
            print(f"Error parsing LLM puzzle response: {e}")
            return None
    
    def _create_fallback_puzzle(self, beat: str, index: int, theme: str) -> Puzzle:
        """Create a simple fallback puzzle when LLM is unavailable"""
        riddles = [
            {
                "question": "I have keys but no locks. I have space but no room. You can enter but not go inside. What am I?",
                "answer": "keyboard",
                "hints": ["I'm used for typing", "I have many buttons", "Found near computers"]
            },
            {
                "question": "I speak without a mouth and hear without ears. I have no body, but come alive with wind. What am I?",
                "answer": "echo",
                "hints": ["I repeat what you say", "I'm found in caves and mountains", "Sound bounces to create me"]
            },
            {
                "question": "The more you take, the more you leave behind. What am I?",
                "answer": "footsteps",
                "hints": ["I'm made when walking", "I show where you've been", "Animals make them too"]
            }
        ]
        
        riddle = riddles[index % len(riddles)]
        location = f"riddle_chamber_{index}"
        
        return Puzzle(
            id=f"fallback_puzzle_{index}",
            name="Ancient Riddle",
            description=f"Ancient runes glow on the wall, forming words: \n\n'{riddle['question']}'",
            puzzle_type=PuzzleType.RIDDLE,
            location=location,
            blocking_directions=["north"],
            hints=riddle["hints"],
            solution=PuzzleSolution(keywords=[riddle["answer"]], case_sensitive=False),
            max_attempts=3,
            rewards={"experience": 25, "items": ["ancient_token"]}
        )
    
    def _create_constellation_puzzle(self, index: int) -> Puzzle:
        """Create a constellation puzzle"""
        constellations = ["orion", "ursa major", "cassiopeia", "draco", "lyra", "cygnus"]
        correct_constellation = random.choice(constellations)
        
        return Puzzle(
            id=f"constellation_puzzle_{index}",
            name="Celestial Gateway",
            description=f"""Before you lies an ancient stone archway covered in glowing celestial symbols. 
The constellations carved into the stone seem to shift and change before your eyes. 
Above the archway, ancient text reads: "Speak the name of the constellation that guards the northern sky, 
the great hunter who stands eternal watch."

The symbols pulse with starlight, waiting for your answer.""",
            puzzle_type=PuzzleType.CONSTELLATION,
            location=f"north_{index + 3}",  # Place a few rooms north
            blocking_directions=["north", "east"],
            hints=[
                "Look for the constellation known for its three bright stars in a row - the belt.",
                "This hunter carries a bow and is visible in winter skies.",
                "The constellation's name comes from Greek mythology - a great hunter."
            ],
            solution=PuzzleSolution(keywords=["orion"], case_sensitive=False),
            rewards={"experience": 50, "items": ["starlight_key"]}
        )
    
    def _create_crystal_puzzle(self, index: int) -> Puzzle:
        """Create a crystal arrangement puzzle"""
        return Puzzle(
            id=f"crystal_puzzle_{index}",
            name="Crystal Resonance Chamber",
            description="""Five luminescent crystals are scattered around this circular chamber, 
each humming with a different harmonic frequency. Ancient runes on the floor show they must be 
arranged in a specific order to unlock the way forward.

The crystals are colored: Red, Blue, Green, Yellow, and Purple.
Faded inscriptions suggest: "From fire's birth to void's embrace, arrange the spectrum of space."

What order will you arrange them in?""",
            puzzle_type=PuzzleType.CRYSTAL_ORDER,
            location=f"chamber_{index + 2}",
            blocking_directions=["west", "up"],
            hints=[
                "Think about the visible light spectrum or rainbow order.",
                "Red has the longest wavelength, violet the shortest.",
                "Fire burns red, space appears violet in the deepest void."
            ],
            solution=PuzzleSolution(
                keywords=["red blue green yellow purple", "red orange yellow green blue purple"],
                pattern=r"red.*blue.*green.*yellow.*purple|red.*yellow.*green.*blue.*purple",
                case_sensitive=False
            ),
            rewards={"experience": 75, "items": ["crystal_lens"]}
        )
    
    def _create_musical_puzzle(self, index: int) -> Puzzle:
        """Create a musical sequence puzzle"""
        return Puzzle(
            id=f"musical_puzzle_{index}",
            name="Harmonic Gateway",
            description="""Wind chimes of various sizes hang from the ceiling, each producing different tones.
As you listen carefully, you hear a faint melody carried on the air - a sequence that seems to 
repeat: "Do, Re, Mi, Fa, Sol..."

A plaque reads: "Complete the ancient scale to unlock the chamber's heart."

What comes after Sol in the traditional musical scale?""",
            puzzle_type=PuzzleType.MUSICAL_NOTES,
            location=f"music_chamber_{index + 1}",
            blocking_directions=["east"],
            hints=[
                "This is the traditional do-re-mi scale.",
                "After Sol comes the sixth note of the major scale.",
                "Think of 'The Sound of Music' - what comes after Sol?"
            ],
            solution=PuzzleSolution(keywords=["la", "lah"], case_sensitive=False),
            max_attempts=3,
            rewards={"experience": 40, "items": ["tuning_fork"]}
        )
    
    def _create_alignment_puzzle(self, index: int) -> Puzzle:
        """Create a celestial alignment puzzle"""
        return Puzzle(
            id=f"alignment_puzzle_{index}",
            name="Starlight Navigation",
            description="""An ancient astrolabe sits atop a pedestal, its intricate brass rings 
gleaming in the starlight filtering through a crystal dome above. The device shows the current 
night sky, but something is misaligned.

You notice that the constellation positions don't match the actual stars visible above. 
The North Star seems displaced. Ancient text reads: "When the eternal guide finds its true place, 
the path shall be revealed."

How do you align the astrolabe correctly?""",
            puzzle_type=PuzzleType.PATTERN_MATCHING,
            location=f"observatory_{index}",
            blocking_directions=["up"],
            hints=[
                "The North Star, or Polaris, should be aligned with true north.",
                "Look for the bright star that doesn't seem to move with the others.",
                "Adjust the astrolabe so the North Star is at the top center."
            ],
            solution=PuzzleSolution(
                keywords=["north", "polaris", "align north", "center north", "true north"],
                case_sensitive=False
            ),
            rewards={"experience": 100, "items": ["star_map", "celestial_orb"]}
        )