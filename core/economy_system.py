"""
Dynamic Trading and Economy System for Cra-mud-gen
Features NPC merchants, dynamic pricing, reputation, and player shops
"""
import random
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class MerchantType(Enum):
    """Types of NPC merchants"""
    GENERAL = "general"
    WEAPONSMITH = "weaponsmith"
    ARMORER = "armorer"
    ALCHEMIST = "alchemist"
    ENCHANTER = "enchanter"
    BLACK_MARKET = "black_market"
    TRAVELING = "traveling"
    COLLECTOR = "collector"
    GUILD = "guild"


class EconomicEvent(Enum):
    """Economic events that affect prices"""
    WAR = "war"  # Weapons/armor prices up
    PLAGUE = "plague"  # Medicine prices up
    HARVEST = "harvest"  # Food prices down
    SHORTAGE = "shortage"  # All prices up
    FESTIVAL = "festival"  # Luxury items up
    DISCOVERY = "discovery"  # New items available
    TRADE_ROUTE_OPENED = "trade_route"  # Prices down
    BANDIT_ACTIVITY = "bandits"  # Prices up


@dataclass
class TradeGood:
    """Represents an item in the economy"""
    name: str
    base_price: int
    category: str
    rarity: str
    demand_factor: float = 1.0
    supply_factor: float = 1.0
    quality: int = 100
    origin: str = "local"
    perishable: bool = False
    illegal: bool = False
    
    def get_current_price(self, economic_modifiers: Dict[str, float]) -> int:
        """Calculate current price based on various factors"""
        price = self.base_price
        
        # Supply and demand
        price *= (self.demand_factor / self.supply_factor)
        
        # Economic events
        category_modifier = economic_modifiers.get(self.category, 1.0)
        price *= category_modifier
        
        # Quality affects price
        price *= (self.quality / 100)
        
        # Rarity multiplier
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.5,
            "rare": 3.0,
            "epic": 5.0,
            "legendary": 10.0
        }
        price *= rarity_multipliers.get(self.rarity, 1.0)
        
        return max(1, int(price))


@dataclass
class Merchant:
    """NPC merchant with personality and inventory"""
    name: str
    merchant_type: MerchantType
    personality: Dict[str, Any]
    inventory: List[TradeGood]
    gold: int
    reputation_with_player: int = 0
    haggle_skill: int = 50
    markup: float = 1.2  # Sells at 120% of value
    markdown: float = 0.8  # Buys at 80% of value
    special_interests: List[str] = field(default_factory=list)
    faction: Optional[str] = None
    schedule: Dict[str, Tuple[int, int]] = field(default_factory=dict)  # day -> (open_hour, close_hour)
    
    def __post_init__(self):
        if not self.schedule:
            # Default schedule
            self.schedule = {
                "weekday": (8, 20),  # 8am to 8pm
                "weekend": (10, 18)  # 10am to 6pm
            }
    
    def is_open(self, current_time: datetime) -> bool:
        """Check if merchant is currently open"""
        day_type = "weekend" if current_time.weekday() >= 5 else "weekday"
        open_hour, close_hour = self.schedule.get(day_type, (0, 24))
        return open_hour <= current_time.hour < close_hour
    
    def get_selling_price(self, item: TradeGood, player_reputation: int) -> int:
        """Get price merchant sells to player"""
        base_price = item.get_current_price({})
        
        # Apply merchant markup
        price = base_price * self.markup
        
        # Reputation discount
        rep_discount = min(0.3, player_reputation / 1000)  # Max 30% discount
        price *= (1 - rep_discount)
        
        # Special interest bonus (merchant pays more for items they want)
        if item.category in self.special_interests:
            price *= 0.9  # 10% discount for special interest items
        
        return max(1, int(price))
    
    def get_buying_price(self, item: TradeGood, player_reputation: int) -> int:
        """Get price merchant pays to player"""
        base_price = item.get_current_price({})
        
        # Apply merchant markdown
        price = base_price * self.markdown
        
        # Reputation bonus
        rep_bonus = min(0.3, player_reputation / 1000)  # Max 30% bonus
        price *= (1 + rep_bonus)
        
        # Special interest bonus
        if item.category in self.special_interests:
            price *= 1.2  # 20% bonus for special interest items
        
        # Illegal goods penalty/bonus
        if item.illegal:
            if self.merchant_type == MerchantType.BLACK_MARKET:
                price *= 1.5  # Black market pays premium
            else:
                price *= 0.3  # Regular merchants pay less (risky)
        
        return max(1, int(price))


class EconomySystem:
    """Manages the game's economic simulation"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.merchants = {}
        self.economic_events = []
        self.price_history = {}
        self.trade_routes = {}
        self.market_trends = {}
        self.player_shops = {}
        self.current_tick = 0
        
        # Initialize base economy
        self._initialize_merchants()
        self._initialize_trade_goods()
        
    def _initialize_merchants(self):
        """Create various merchant NPCs"""
        # General merchant
        self.merchants["general_store"] = Merchant(
            name="Marcus the Trader",
            merchant_type=MerchantType.GENERAL,
            personality={"friendly": True, "honest": True, "gossiper": True},
            inventory=[],
            gold=5000,
            special_interests=["common", "consumables"]
        )
        
        # Weaponsmith
        self.merchants["weaponsmith"] = Merchant(
            name="Thorin Ironforge",
            merchant_type=MerchantType.WEAPONSMITH,
            personality={"gruff": True, "skilled": True, "perfectionist": True},
            inventory=[],
            gold=8000,
            haggle_skill=70,
            special_interests=["weapons", "metal", "crafting_materials"]
        )
        
        # Black market dealer
        self.merchants["black_market"] = Merchant(
            name="Shadow",
            merchant_type=MerchantType.BLACK_MARKET,
            personality={"mysterious": True, "cunning": True, "dangerous": True},
            inventory=[],
            gold=15000,
            haggle_skill=90,
            markup=1.5,
            markdown=0.6,
            special_interests=["illegal", "rare", "stolen"],
            schedule={"weekday": (22, 4), "weekend": (22, 4)}  # Night only
        )
        
        # Traveling merchant (appears randomly)
        self.merchants["traveling"] = Merchant(
            name="Khajiit Wanderer",
            merchant_type=MerchantType.TRAVELING,
            personality={"exotic": True, "mysterious": True, "well-traveled": True},
            inventory=[],
            gold=10000,
            haggle_skill=80,
            special_interests=["exotic", "foreign", "rare"],
            schedule={}  # Random appearance
        )
        
    def _initialize_trade_goods(self):
        """Initialize base trade goods catalog"""
        self.base_goods = {
            # Weapons
            "iron_sword": TradeGood("Iron Sword", 100, "weapons", "common"),
            "steel_blade": TradeGood("Steel Blade", 250, "weapons", "uncommon"),
            "enchanted_sword": TradeGood("Enchanted Sword", 1000, "weapons", "rare"),
            
            # Armor
            "leather_armor": TradeGood("Leather Armor", 150, "armor", "common"),
            "chainmail": TradeGood("Chainmail", 400, "armor", "uncommon"),
            
            # Consumables
            "health_potion": TradeGood("Health Potion", 50, "consumables", "common", perishable=True),
            "mana_potion": TradeGood("Mana Potion", 75, "consumables", "common", perishable=True),
            
            # Materials
            "iron_ore": TradeGood("Iron Ore", 20, "materials", "common"),
            "dragon_scale": TradeGood("Dragon Scale", 5000, "materials", "legendary"),
            
            # Illegal goods
            "poison": TradeGood("Poison", 200, "illegal", "uncommon", illegal=True),
            "stolen_artifact": TradeGood("Stolen Artifact", 10000, "illegal", "rare", illegal=True)
        }
    
    def simulate_economy_tick(self):
        """Simulate one economic tick (day/hour)"""
        self.current_tick += 1
        
        # Random economic events
        if random.random() < 0.1:  # 10% chance of event
            event_msg = self._trigger_economic_event()
            
        # Expire old events
        self.economic_events = [e for e in self.economic_events if e["started"] + e["duration"] > self.current_tick]
        
        # Update supply and demand
        for good_name, good in self.base_goods.items():
            # Random demand fluctuation
            good.demand_factor *= random.uniform(0.95, 1.05)
            good.demand_factor = max(0.5, min(2.0, good.demand_factor))
            
            # Random supply fluctuation
            good.supply_factor *= random.uniform(0.95, 1.05)
            good.supply_factor = max(0.5, min(2.0, good.supply_factor))
            
            # Record price history
            if good_name not in self.price_history:
                self.price_history[good_name] = []
            
            current_price = good.get_current_price(self._get_economic_modifiers())
            self.price_history[good_name].append(current_price)
            
            # Keep only last 100 prices
            if len(self.price_history[good_name]) > 100:
                self.price_history[good_name].pop(0)
        
        # Restock merchants
        self._restock_merchants()
        
        # Simulate player shops
        for shop in self.player_shops.values():
            shop.simulate_sales(self)
    
    def _trigger_economic_event(self) -> str:
        """Trigger a random economic event"""
        event = random.choice(list(EconomicEvent))
        duration = random.randint(5, 20)  # Event lasts 5-20 ticks
        
        self.economic_events.append({
            "event": event,
            "duration": duration,
            "started": self.current_tick
        })
        
        # Generate event description
        event_descriptions = {
            EconomicEvent.WAR: "War has broken out! Weapon and armor prices surge!",
            EconomicEvent.PLAGUE: "A plague spreads! Medicine becomes scarce!",
            EconomicEvent.HARVEST: "Bountiful harvest! Food prices drop!",
            EconomicEvent.SHORTAGE: "Supply shortage! All prices increase!",
            EconomicEvent.FESTIVAL: "Festival begins! Luxury goods in demand!",
            EconomicEvent.DISCOVERY: "New trade route discovered! Exotic goods available!",
            EconomicEvent.TRADE_ROUTE_OPENED: "Trade routes open! Prices stabilize!",
            EconomicEvent.BANDIT_ACTIVITY: "Bandits attack caravans! Prices rise!"
        }
        
        return event_descriptions.get(event, "Economic conditions change!")
    
    def _get_economic_modifiers(self) -> Dict[str, float]:
        """Get current economic modifiers based on active events"""
        modifiers = {}
        
        for event_data in self.economic_events:
            event = event_data["event"]
            
            if event == EconomicEvent.WAR:
                modifiers["weapons"] = modifiers.get("weapons", 1.0) * 1.5
                modifiers["armor"] = modifiers.get("armor", 1.0) * 1.5
            elif event == EconomicEvent.PLAGUE:
                modifiers["consumables"] = modifiers.get("consumables", 1.0) * 2.0
            elif event == EconomicEvent.HARVEST:
                modifiers["consumables"] = modifiers.get("consumables", 1.0) * 0.5
            elif event == EconomicEvent.SHORTAGE:
                for category in ["weapons", "armor", "consumables", "materials"]:
                    modifiers[category] = modifiers.get(category, 1.0) * 1.3
            elif event == EconomicEvent.FESTIVAL:
                modifiers["luxury"] = modifiers.get("luxury", 1.0) * 1.5
        
        return modifiers
    
    def _restock_merchants(self):
        """Restock merchant inventories"""
        for merchant_id, merchant in self.merchants.items():
            # Clear old perishable items
            merchant.inventory = [item for item in merchant.inventory 
                                 if not item.perishable or random.random() < 0.7]
            
            # Add new items based on merchant type
            new_items = self._generate_merchant_inventory(merchant.merchant_type)
            merchant.inventory.extend(new_items)
            
            # Limit inventory size
            if len(merchant.inventory) > 20:
                merchant.inventory = merchant.inventory[:20]
    
    def _generate_merchant_inventory(self, merchant_type: MerchantType) -> List[TradeGood]:
        """Generate appropriate inventory for merchant type"""
        inventory = []
        
        if merchant_type == MerchantType.GENERAL:
            # General merchants have variety
            for _ in range(random.randint(3, 8)):
                category = random.choice(["consumables", "materials", "weapons", "armor"])
                items = [g for g in self.base_goods.values() if g.category == category and not g.illegal]
                if items:
                    inventory.append(random.choice(items))
        
        elif merchant_type == MerchantType.WEAPONSMITH:
            # Weaponsmiths focus on weapons
            weapon_items = [g for g in self.base_goods.values() if g.category == "weapons"]
            inventory.extend(random.sample(weapon_items, min(5, len(weapon_items))))
        
        elif merchant_type == MerchantType.BLACK_MARKET:
            # Black market has illegal goods
            illegal_items = [g for g in self.base_goods.values() if g.illegal]
            inventory.extend(illegal_items)
            # Also some rare legal items
            rare_items = [g for g in self.base_goods.values() if g.rarity in ["rare", "legendary"]]
            inventory.extend(random.sample(rare_items, min(3, len(rare_items))))
        
        elif merchant_type == MerchantType.TRAVELING:
            # Traveling merchants have exotic goods
            if self.llm:
                # Generate unique exotic items
                exotic_item = self._generate_exotic_item()
                if exotic_item:
                    inventory.append(exotic_item)
            
            # Random high-value items
            valuable_items = [g for g in self.base_goods.values() if g.base_price > 500]
            inventory.extend(random.sample(valuable_items, min(4, len(valuable_items))))
        
        return inventory
    
    def _generate_exotic_item(self) -> Optional[TradeGood]:
        """Generate unique exotic item using LLM"""
        if not self.llm:
            # Fallback exotic items
            exotic_items = [
                TradeGood("Void Crystal", 3000, "exotic", "rare", origin="The Void"),
                TradeGood("Phoenix Feather", 5000, "exotic", "legendary", origin="Fire Realm"),
                TradeGood("Time Sand", 8000, "exotic", "legendary", origin="Temporal Nexus")
            ]
            return random.choice(exotic_items)
        
        try:
            prompt = "Generate a unique exotic trade item. Format: Name|Price|Rarity|Origin. Example: Starlight Essence|2500|rare|Celestial Realm"
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_game_response(prompt, {"theme": "fantasy"})
            else:
                response = self.llm.generate_game_response(prompt, {"theme": "fantasy"})
            
            parts = response.strip().split("|")
            if len(parts) >= 4:
                return TradeGood(
                    name=parts[0],
                    base_price=int(parts[1]),
                    category="exotic",
                    rarity=parts[2],
                    origin=parts[3]
                )
        except:
            pass
        
        return None
    
    def haggle(self, merchant: Merchant, item: TradeGood, is_buying: bool, 
               player_charisma: int) -> Tuple[bool, int, str]:
        """
        Attempt to haggle with merchant
        
        Returns: (success, final_price, message)
        """
        base_price = merchant.get_selling_price(item, 0) if is_buying else merchant.get_buying_price(item, 0)
        
        # Calculate haggle success
        player_skill = player_charisma * 5  # Convert charisma to skill
        skill_diff = player_skill - merchant.haggle_skill
        success_chance = 0.5 + (skill_diff / 200)  # -50% to +50% based on skill
        
        if random.random() < success_chance:
            # Successful haggle
            discount = random.uniform(0.05, 0.20)  # 5-20% discount
            if is_buying:
                final_price = int(base_price * (1 - discount))
                message = f"{merchant.name} agrees to lower the price!"
            else:
                final_price = int(base_price * (1 + discount))
                message = f"{merchant.name} agrees to pay more!"
            
            # Improve relationship
            merchant.reputation_with_player += 5
            
            return True, final_price, message
        else:
            # Failed haggle
            if random.random() < 0.3:  # 30% chance of negative consequence
                # Merchant is offended
                merchant.reputation_with_player -= 10
                if is_buying:
                    final_price = int(base_price * 1.1)  # 10% penalty
                    message = f"{merchant.name} is offended and raises the price!"
                else:
                    final_price = int(base_price * 0.9)  # 10% penalty
                    message = f"{merchant.name} is offended and offers less!"
            else:
                # No change
                final_price = base_price
                message = f"{merchant.name} refuses to budge on the price."
            
            return False, final_price, message
    
    def get_merchant_in_room(self, room_id: str) -> Optional[Merchant]:
        """Get merchant present in a specific room"""
        # Map rooms to merchants (would be more sophisticated in real game)
        room_merchants = {
            "market_square": "general_store",
            "forge": "weaponsmith", 
            "dark_alley": "black_market"
        }
        
        merchant_id = room_merchants.get(room_id)
        return self.merchants.get(merchant_id) if merchant_id else None
    
    def find_item_in_merchant(self, merchant: Merchant, item_name: str) -> Optional[TradeGood]:
        """Find item in merchant's inventory"""
        for item in merchant.inventory:
            if item_name.lower() in item.name.lower():
                return item
        return None
    
    def conduct_trade(self, merchant: Merchant, item: TradeGood, is_buying: bool, player_gold: int) -> Tuple[bool, str, int]:
        """
        Conduct a trade transaction
        
        Returns: (success, message, gold_change)
        """
        if is_buying:
            # Player buying from merchant
            price = merchant.get_selling_price(item, merchant.reputation_with_player)
            
            if player_gold < price:
                return False, f"You don't have enough gold! Need {price}, have {player_gold}.", 0
            
            if item not in merchant.inventory:
                return False, f"{merchant.name} doesn't have that item.", 0
            
            # Remove item from merchant, charge player
            merchant.inventory.remove(item)
            merchant.gold += price
            
            return True, f"You bought {item.name} for {price} gold!", -price
        
        else:
            # Player selling to merchant
            price = merchant.get_buying_price(item, merchant.reputation_with_player)
            
            if merchant.gold < price:
                return False, f"{merchant.name} doesn't have enough gold!", 0
            
            # Add item to merchant, pay player
            merchant.inventory.append(item)
            merchant.gold -= price
            
            return True, f"You sold {item.name} for {price} gold!", price


class PlayerShop:
    """Player-owned shop for selling to other players/NPCs"""
    
    def __init__(self, shop_name: str, location: str):
        self.name = shop_name
        self.location = location
        self.inventory = {}  # item -> (quantity, price)
        self.gold_earned = 0
        self.reputation = 0
        self.hired_npcs = []  # NPCs running the shop
        self.upgrades = set()
        self.daily_customers = 0
        self.sale_history = []
        
    def stock_item(self, item: TradeGood, quantity: int, price: int):
        """Stock an item in the shop"""
        if item.name in self.inventory:
            current_qty, _ = self.inventory[item.name]
            self.inventory[item.name] = (current_qty + quantity, price)
        else:
            self.inventory[item.name] = (quantity, price)
    
    def simulate_sales(self, economy: EconomySystem) -> List[str]:
        """Simulate NPC customers buying items"""
        messages = []
        
        # Number of customers based on reputation and location
        base_customers = 5
        rep_bonus = self.reputation // 100
        location_multiplier = {
            "market_district": 2.0,
            "town_square": 1.5,
            "back_alley": 0.5,
            "guild_hall": 1.2
        }.get(self.location, 1.0)
        
        num_customers = int((base_customers + rep_bonus) * location_multiplier)
        
        if "advertising" in self.upgrades:
            num_customers = int(num_customers * 1.5)
        
        for _ in range(num_customers):
            if not self.inventory:
                break
            
            # Random customer tries to buy something
            item_name = random.choice(list(self.inventory.keys()))
            quantity, price = self.inventory[item_name]
            
            if quantity > 0:
                # Check if price is competitive
                market_price = 100  # Would check actual market price
                if price <= market_price * 1.2:  # Within 20% of market
                    # Make sale
                    self.inventory[item_name] = (quantity - 1, price)
                    self.gold_earned += price
                    self.reputation += 1
                    
                    customer_name = self._generate_customer_name()
                    messages.append(f"{customer_name} bought {item_name} for {price} gold!")
                    
                    # Record sale
                    self.sale_history.append({
                        "item": item_name,
                        "price": price,
                        "customer": customer_name,
                        "timestamp": datetime.now()
                    })
        
        self.daily_customers = num_customers
        return messages
    
    def _generate_customer_name(self) -> str:
        """Generate random customer name"""
        first_names = ["John", "Mary", "Bob", "Alice", "Tom", "Sarah", "Mike", "Emma"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def hire_npc(self, npc_name: str, wage: int, skill_level: int):
        """Hire an NPC to help run the shop"""
        self.hired_npcs.append({
            "name": npc_name,
            "wage": wage,
            "skill": skill_level,
            "morale": 100
        })
    
    def upgrade_shop(self, upgrade_type: str) -> Tuple[bool, str]:
        """Upgrade the shop with various improvements"""
        upgrade_costs = {
            "advertising": 1000,
            "security": 2000,
            "expansion": 5000,
            "premium_location": 10000,
            "guild_membership": 3000
        }
        
        if upgrade_type not in upgrade_costs:
            return False, "Unknown upgrade type"
        
        if upgrade_type in self.upgrades:
            return False, "Already have this upgrade"
        
        cost = upgrade_costs[upgrade_type]
        # Check if player has enough gold (would check in game)
        
        self.upgrades.add(upgrade_type)
        
        benefits = {
            "advertising": "Customer traffic increased by 50%!",
            "security": "Reduced theft and better inventory protection!",
            "expansion": "Can now stock 50% more items!",
            "premium_location": "Moved to prime retail space!",
            "guild_membership": "Access to exclusive trade deals!"
        }
        
        return True, benefits.get(upgrade_type, "Shop upgraded!")