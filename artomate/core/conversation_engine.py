"""Conversation engine for interactive prompt generation (like n8n workflow)."""

from enum import Enum
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
import json
from loguru import logger

# ============================================================================
# Data Lists (stejně jako v n8n)
# ============================================================================

ANIMALS = [
    "Ant", "Antelope", "Arctic Fox", "Bat", "Bear", "Beaver", "Bee",
    "Beetle", "Betta Fish", "Boar", "Buffalo", "Butterfly", "Camel",
    "Canary", "Cat", "Chameleon", "Cheetah", "Chicken", "Coral Fish",
    "Cow", "Crab", "Crocodile", "Crow", "Deer", "Dog", "Dolphin",
    "Donkey", "Dove", "Dragon", "Dragonfly", "Duck", "Eagle", "Elephant",
    "Fairy", "Flamingo", "Fox", "Frog", "Gazelle", "Giraffe", "Goat",
    "Goldfish", "Gorilla", "Griffin", "Guinea Pig", "Hamster", "Hawk",
    "Hedgehog", "Hippo", "Horse", "Hummingbird", "Hyena", "Iguana",
    "Jellyfish", "Kangaroo", "Koala", "Ladybug", "Lemur", "Leopard",
    "Lion", "Lizard", "Lynx", "Meerkat", "Mermaid", "Monkey", "Moose",
    "Moth", "Octopus", "Orca", "Otter", "Owl", "Panda", "Parrot",
    "Peacock", "Pegasus", "Pelican", "Penguin", "Phoenix", "Pig",
    "Polar Bear", "Puma", "Rabbit", "Raccoon", "Reindeer", "Rhino",
    "Rooster", "Sea Turtle", "Seahorse", "Seal", "Shark", "Sheep",
    "Skunk", "Snake", "Spider", "Spirit Animal", "Squirrel", "Starfish",
    "Stingray", "Swan", "Tiger", "Turtle", "Unicorn", "Walrus", "Whale",
    "Wolf", "Zebra"
]

STYLES = [
    "Realistic", "Watercolor", "Line Art", "Pop Art", "Abstract", "Boho",
    "Cute", "Anime", "Fantasy", "Minimalist", "Geometric", "Japandi",
    "Vintage", "Cyberpunk", "Neon", "Vaporwave", "Art Deco", "Cartoon",
    "Low Poly", "3D Render", "Ink Painting", "Pencil Sketch",
    "Pastel Illustrative", "Botanical", "Retro", "Modern Poster"
]

THEMES = [
    "Christmas", "Valentine", "Halloween", "Easter", "Spring Blossom",
    "Summer Beach", "Fall Harvest", "Winter Snow", "Independence Day",
    "Memorial Day", "Pride Month", "St. Patrick's Day", "Lunar New Year",
    "Thanksgiving", "Horror Spooky", "Forest", "Ocean", "Space", "Desert",
    "Mountain", "Rainy Mood", "Snowy Night", "Aurora", "Japanese Spring",
    "Autumn Leaves", "Baby Nursery", "Wedding", "Cottagecore",
    "Coastal Aesthetic"
]

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


class ConversationStage(Enum):
    """Conversation stages."""
    START = "start"
    ASK_ANIMAL = "ask_animal"
    ASK_STYLE = "ask_style"
    ASK_THEME = "ask_theme"
    ASK_COUNT = "ask_count"
    CONFIRM = "confirm"
    GENERATE = "generate"
    DONE = "done"


@dataclass
class ConversationContext:
    """Context for ongoing conversation."""
    description: Optional[str] = None
    animals: List[str] = field(default_factory=list)
    random_animals: bool = False
    styles: List[str] = field(default_factory=list)
    random_styles: bool = False
    themes: List[str] = field(default_factory=list)
    random_themes: bool = False
    animals_per_image: int = 1
    random_count: bool = False
    image_count: int = 12


@dataclass
class ConversationState:
    """Current state of conversation."""
    stage: ConversationStage
    context: ConversationContext


class ConversationEngine:
    """Engine for interactive conversation with user."""

    def __init__(self):
        """Initialize conversation engine."""
        self.state: Optional[ConversationState] = None

    def start(self) -> tuple[str, ConversationState]:
        """Start new conversation.

        Returns:
            (reply_text, new_state)
        """
        self.state = ConversationState(
            stage=ConversationStage.START,
            context=ConversationContext()
        )

        reply_text = (
            "🔄 Začínáme!\n\n"
            "Napiš krátký popis, o čem mají být obrázky do kalendáře.\n"
            "Např.: cute animals in nature, fantasy creatures, modern pets…"
        )

        logger.info("[CONV] Started new conversation")
        return reply_text, self.state

    def process_input(self, user_input: str) -> tuple[str, ConversationState]:
        """Process user input and move to next stage.

        Args:
            user_input: User's text input

        Returns:
            (reply_text, new_state)
        """
        if not self.state:
            return self.start()

        text_raw = user_input.strip()
        text_lower = text_raw.lower()

        # Check for reset commands
        if text_lower in ["/start", "start", "reset", "test"]:
            logger.info("[CONV] Reset triggered")
            return self.start()

        stage = self.state.stage
        context = self.state.context

        logger.info(f"[CONV] Processing input at stage {stage.value}: {text_raw[:50]}")

        # ========== STAGE: START ==========
        if stage == ConversationStage.START:
            context.description = text_raw
            self.state.stage = ConversationStage.ASK_ANIMAL

            animals_list = ", ".join(f"{i + 1}) {a}" for i, a in enumerate(ANIMALS))
            reply_text = (
                "🐾 Dobře!\n"
                "Vyber *ZVÍŘE/ZVÍŘATA* (nebo napiš **0** nebo **náhodně** pro náhodný výběr):\n\n"
                + animals_list
            )
            logger.info("[CONV] START → ASK_ANIMAL")

        # ========== STAGE: ASK_ANIMAL ==========
        elif stage == ConversationStage.ASK_ANIMAL:
            if text_lower in ["random", "náhodně", "nahodne", "0"]:
                random_count = self._random_int(3, 5)
                context.animals = self._random_sample(ANIMALS, random_count)
                context.random_animals = True
                logger.info(f"[CONV] Random animals: {context.animals}")
            else:
                context.animals = self._parse_selection(text_raw, ANIMALS)
                context.random_animals = False
                logger.info(f"[CONV] Selected animals: {context.animals}")

            self.state.stage = ConversationStage.ASK_STYLE

            styles_list = ", ".join(f"{i + 1}) {s}" for i, s in enumerate(STYLES))
            reply_text = (
                "🎨 Vyber *STYL/STYLY* (nebo napiš **0** pro náhodný výběr):\n\n"
                + styles_list
            )
            logger.info("[CONV] ASK_ANIMAL → ASK_STYLE")

        # ========== STAGE: ASK_STYLE ==========
        elif stage == ConversationStage.ASK_STYLE:
            if text_lower in ["random", "náhodně", "nahodne", "0"]:
                random_count = self._random_int(2, 4)
                context.styles = self._random_sample(STYLES, random_count)
                context.random_styles = True
                logger.info(f"[CONV] Random styles: {context.styles}")
            else:
                context.styles = self._parse_selection(text_raw, STYLES)
                context.random_styles = False
                logger.info(f"[CONV] Selected styles: {context.styles}")

            self.state.stage = ConversationStage.ASK_THEME

            themes_list = ", ".join(f"{i + 1}) {t}" for i, t in enumerate(THEMES))
            reply_text = (
                "🌄 Vyber *TÉMA/TÉMATA* (nebo napiš **0** pro náhodný výběr):\n\n"
                + themes_list
            )
            logger.info("[CONV] ASK_STYLE → ASK_THEME")

        # ========== STAGE: ASK_THEME ==========
        elif stage == ConversationStage.ASK_THEME:
            if text_lower in ["random", "náhodně", "nahodne", "0"]:
                random_count = self._random_int(2, 4)
                context.themes = self._random_sample(THEMES, random_count)
                context.random_themes = True
                logger.info(f"[CONV] Random themes: {context.themes}")
            else:
                context.themes = self._parse_selection(text_raw, THEMES)
                context.random_themes = False
                logger.info(f"[CONV] Selected themes: {context.themes}")

            self.state.stage = ConversationStage.ASK_COUNT

            reply_text = (
                "🐾 Kolik *ZVÍŘAT* chceš na každém obrázku? "
                "(nebo napiš **0** pro náhodně)\n"
                "Napiš číslo (např. 1, 2, 3, 5...).\n\n"
                "_Poznámka: Vygeneruje se vždy 12 obrázků pro kalendář (jeden pro každý měsíc)._"
            )
            logger.info("[CONV] ASK_THEME → ASK_COUNT")

        # ========== STAGE: ASK_COUNT ==========
        elif stage == ConversationStage.ASK_COUNT:
            if text_lower in ["random", "náhodně", "nahodne", "0"]:
                context.animals_per_image = self._random_int(1, 4)
                context.random_count = True
                logger.info(f"[CONV] Random count: {context.animals_per_image}")
            else:
                context.animals_per_image = int(text_raw) if text_raw.isdigit() else 1
                context.random_count = False
                logger.info(f"[CONV] Selected count: {context.animals_per_image}")

            self.state.stage = ConversationStage.CONFIRM

            # Summary
            summary = (
                "*📝 Shrnutí:*\n"
                f"• Popis: {context.description}\n"
                f"• Zvířata: {', '.join(context.animals)}"
                f"{' (náhodně)' if context.random_animals else ''}\n"
                f"• Styly: {', '.join(context.styles)}"
                f"{' (náhodně)' if context.random_styles else ''}\n"
                f"• Témata: {', '.join(context.themes)}"
                f"{' (náhodně)' if context.random_themes else ''}\n"
                f"• Zvířat na obrázku: {context.animals_per_image}"
                f"{' (náhodně)' if context.random_count else ''}\n"
                f"• Celkem obrázků: 12 (kalendář - každý měsíc)\n\n"
                "Pokud je to OK, napiš **OK**.\n"
                "Pokud chceš začít znovu, napiš */start*."
            )

            reply_text = summary
            logger.info("[CONV] ASK_COUNT → CONFIRM")

        # ========== STAGE: CONFIRM ==========
        elif stage == ConversationStage.CONFIRM:
            if text_lower == "ok" or text_lower == "ok.":
                # Check all required fields
                if not all([context.animals, context.styles, context.themes, context.animals_per_image]):
                    self.state.stage = ConversationStage.START
                    reply_text = (
                        "⚠️ Něco chybí, začneme raději znovu.\n"
                        "Napiš krátký popis obrázků."
                    )
                    logger.info("[CONV] CONFIRM FAILED - missing data")
                else:
                    self.state.stage = ConversationStage.GENERATE
                    reply_text = "✨ Generuji 12 promptů pro kalendář… chvíli počkej."
                    logger.info("[CONV] CONFIRM SUCCESS → GENERATE")
            else:
                # User wants to restart
                self.state.stage = ConversationStage.START
                reply_text = (
                    "🔄 OK, začneme znovu.\n"
                    "Napiš krátký popis obrázků."
                )
                logger.info("[CONV] CONFIRM CANCELLED")

        # ========== DEFAULT ==========
        else:
            self.state.stage = ConversationStage.START
            reply_text = "🔄 Začneme znovu.\nNapiš krátký popis obrázků."
            logger.info("[CONV] DEFAULT case - restart")

        return reply_text, self.state

    def get_prompts(self, use_ai: bool = False) -> List[Dict[str, str]]:
        """Get generated prompts for current context.

        Args:
            use_ai: If True, use OpenAI GPT to generate unique prompts for each month

        Returns:
            List of dicts with prompt, month, orientation, etc.
        """
        if not self.state or self.state.stage != ConversationStage.GENERATE:
            raise ValueError("Cannot generate prompts - not in GENERATE stage")

        context = self.state.context

        if use_ai:
            # Use GPT to generate month-specific prompts
            return self._generate_prompts_with_ai(context)
        else:
            # Simple prompt generation (fallback)
            return self._generate_simple_prompts(context)

    def _generate_simple_prompts(self, context: ConversationContext) -> List[Dict[str, str]]:
        """Generate simple prompts without AI (fallback).

        Args:
            context: Conversation context

        Returns:
            List of prompt dicts
        """
        prompts = []

        for idx, month in enumerate(MONTHS):
            animals_str = ", ".join(context.animals[:context.animals_per_image])
            style_str = context.styles[idx % len(context.styles)]
            theme_str = context.themes[idx % len(context.themes)]

            prompt = (
                f"{animals_str} in {theme_str} theme, {style_str} style, "
                f"high quality, detailed, professional, original design, no text, no logos, "
                f"suitable for calendar, 1024x1024 resolution"
            )

            prompts.append({
                "month": month,
                "prompt": prompt,
                "orientation": "landscape",
                "usage": "calendar",
                "animals": animals_str,
                "style": style_str,
                "theme": theme_str,
            })

        logger.info(f"[CONV] Generated {len(prompts)} simple prompts")
        return prompts

    def _generate_prompts_with_ai(self, context: ConversationContext) -> List[Dict[str, str]]:
        """Generate month-specific prompts using OpenAI GPT.

        Args:
            context: Conversation context

        Returns:
            List of prompt dicts
        """
        try:
            from openai import OpenAI
            from artomate.core.config import get_config
            
            config = get_config()
            client = OpenAI(api_key=config.OPENAI_API_KEY)

            # Prepare the prompt for GPT
            system_prompt = """You are an expert at creating Midjourney prompts for calendar images with deep knowledge of animal ecology, geography, and behavior.

Create 12 unique, detailed prompts (one for each month: January to December).

CRITICAL RULES - ANIMAL ECOLOGY & GEOGRAPHY:
1. Consider WHERE each animal naturally lives (climate zone):
   - Polar animals (polar bear, penguin, arctic fox) → cold regions year-round
   - Tropical animals (parrot, monkey, sloth) → warm/hot regions year-round
   - Temperate animals (deer, fox, rabbit) → seasonal changes
   - Desert animals (camel, lizard) → hot, dry regions
   - Ocean animals (whale, dolphin, seal) → marine environments

2. Match the MONTH/SEASON to the animal's natural habitat:
   - January (winter): Show tropical animals in their warm habitat, polar animals in their element
   - June (summer): Temperate animals active, tropical animals in rainy season
   - Don't show polar bears in summer heat or tropical parrots in snow

3. Animal behavior by season (for temperate zones):
   - Winter: Hibernation, winter coats, survival mode
   - Spring: Mating season, newborns, nest building
   - Summer: Active, feeding, raising young
   - Fall: Migration, preparing for winter, storing food

4. REALISTIC environments:
   - Match habitat to animal (forest for deer, ocean for dolphin, savanna for lion)
   - Show appropriate weather (snow for arctic fox, rain for tropical frog)
   - Include ecosystem elements (prey, plants, terrain)

Format prompts for Midjourney with:
- Detailed descriptions (100-150 words)
- Animal in natural habitat with appropriate season/weather
- Style parameters matching the requested art style
- Lighting and atmosphere for the month
- Quality specifications: --ar 3:4 --quality 2 --stylize 500

Return ONLY a JSON array (no markdown, no explanations):
[
  {"prompt": "detailed midjourney prompt with --parameters", "month": "January", "orientation": "portrait", "usage": "calendar", "animals": "specific animals", "habitat": "natural habitat", "season": "season description"},
  ...12 total
]"""

            user_message = f"""Generate 12 calendar image prompts in JSON format for Midjourney.

Context:
- Animals: {', '.join(context.animals)}
- Styles: {', '.join(context.styles)}
- Themes: {', '.join(context.themes)}
- Animals per image: {context.animals_per_image}
- Description: {context.description}

IMPORTANT INSTRUCTIONS:
1. Create 12 unique prompts (one for each month: January to December)
2. Each prompt should feature {context.animals_per_image} animal(s) from the list
3. Consider GEOGRAPHY - where does each animal naturally live?
   - Match the animal to appropriate climate/habitat
   - If animal is from tropics, show warm environment even in January
   - If animal is polar, show cold environment even in July
4. Consider BEHAVIOR for that specific month:
   - What is the animal doing in that season?
   - Hibernating, migrating, mating, caring for young?
5. Use the requested styles: {', '.join(context.styles)}
6. Incorporate themes where appropriate: {', '.join(context.themes)}
7. Format as Midjourney prompts with --ar 3:4 --quality 2 --stylize 500

EXAMPLE for clarity:
- Polar Bear in January: "Majestic polar bear on arctic ice under northern lights, winter hunting season..."
- Monkey in January: "Playful monkey in lush tropical rainforest, wet season, vibrant green canopy..."
- Fox in January: "Red fox with thick winter coat hunting in snowy forest, crisp winter morning..."

Return ONLY a JSON array starting with [ and ending with ]
Each object must have: prompt, month, orientation, usage, animals, habitat, season"""

            logger.info("[CONV] Calling OpenAI GPT to generate month-specific prompts...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.9,
                max_tokens=4000,
            )

            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            prompts = json.loads(content)

            # Validate and ensure all fields are present
            for prompt_data in prompts:
                if "animals" not in prompt_data:
                    # Extract animals from prompt or use defaults
                    animals_str = ", ".join(context.animals[:context.animals_per_image])
                    prompt_data["animals"] = animals_str
                
                if "style" not in prompt_data:
                    prompt_data["style"] = context.styles[0]
                
                if "theme" not in prompt_data:
                    prompt_data["theme"] = context.themes[0]
                
                if "habitat" not in prompt_data:
                    prompt_data["habitat"] = "natural environment"
                
                if "season" not in prompt_data:
                    # Infer season from month
                    month = prompt_data.get("month", "")
                    if month in ["December", "January", "February"]:
                        prompt_data["season"] = "winter"
                    elif month in ["March", "April", "May"]:
                        prompt_data["season"] = "spring"
                    elif month in ["June", "July", "August"]:
                        prompt_data["season"] = "summer"
                    else:
                        prompt_data["season"] = "autumn"

            logger.info(f"[CONV] Generated {len(prompts)} AI-powered prompts with ecological context")
            return prompts

        except Exception as e:
            logger.error(f"[CONV] Failed to generate AI prompts: {e}")
            logger.info("[CONV] Falling back to simple prompt generation")
            return self._generate_simple_prompts(context)

    # ========== HELPERS ==========

    @staticmethod
    def _parse_selection(text: str, items: List[str]) -> List[str]:
        """Parse user selection by number or name.

        Args:
            text: User input (e.g., "1, 3, 5" or "Cat, Dog")
            items: List of items to select from

        Returns:
            List of selected items
        """
        import re
        inputs = re.split(r'[,\s]+', text)
        result = []

        for inp in inputs:
            inp = inp.strip()
            if not inp:
                continue

            # Try as number
            if inp.isdigit():
                num = int(inp)
                if 1 <= num <= len(items):
                    result.append(items[num - 1])
                    continue

            # Try by name (case-insensitive)
            for item in items:
                if item.lower() == inp.lower():
                    result.append(item)
                    break
            else:
                # If not found in list, add as-is
                result.append(inp)

        return result

    @staticmethod
    def _random_sample(items: List[str], count: int) -> List[str]:
        """Get random sample from list.

        Args:
            items: List to sample from
            count: Number of items

        Returns:
            Random sample
        """
        import random
        return random.sample(items, min(count, len(items)))

    @staticmethod
    def _random_int(min_val: int, max_val: int) -> int:
        """Get random integer in range.

        Args:
            min_val: Min value
            max_val: Max value

        Returns:
            Random integer
        """
        import random
        return random.randint(min_val, max_val)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dict.

        Returns:
            Dictionary representation
        """
        if not self.state:
            return {}

        context = self.state.context
        return {
            "stage": self.state.stage.value,
            "context": {
                "description": context.description,
                "animals": context.animals,
                "random_animals": context.random_animals,
                "styles": context.styles,
                "random_styles": context.random_styles,
                "themes": context.themes,
                "random_themes": context.random_themes,
                "animals_per_image": context.animals_per_image,
                "random_count": context.random_count,
                "image_count": context.image_count,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationEngine":
        """Deserialize state from dict.

        Args:
            data: Dictionary representation

        Returns:
            ConversationEngine instance with restored state
        """
        engine = cls()

        if not data:
            return engine

        try:
            stage_value = data.get("stage", "start")
            stage = ConversationStage(stage_value)

            ctx_data = data.get("context", {})
            context = ConversationContext(
                description=ctx_data.get("description"),
                animals=ctx_data.get("animals", []),
                random_animals=ctx_data.get("random_animals", False),
                styles=ctx_data.get("styles", []),
                random_styles=ctx_data.get("random_styles", False),
                themes=ctx_data.get("themes", []),
                random_themes=ctx_data.get("random_themes", False),
                animals_per_image=ctx_data.get("animals_per_image", 1),
                random_count=ctx_data.get("random_count", False),
                image_count=ctx_data.get("image_count", 12),
            )

            engine.state = ConversationState(stage=stage, context=context)
            logger.info(f"[CONV] Restored state from dict: {stage.value}")
        except Exception as e:
            logger.warning(f"[CONV] Failed to restore state: {e}")
            engine.state = None

        return engine
