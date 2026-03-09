"""Core game logic for Escape From Epenstein Island."""

import random
import time
from typing import Optional, Dict

# items available at Donaldo El Trumpo's shop; prices in dinero, heal/shield
# values describe how much health or shield the item restores when used.
SHOP_ITEMS = {
    "Health Kit": {"price": 30, "heal": 25, "shield": 0},
    "Shield Potion": {"price": 25, "heal": 0, "shield": 25},
    "Golden Apple": {"price": 50, "heal": 10, "shield": 10},
}


class Player:
    """Represents a player in Escape From Epenstein Island.

    Tracks the player's current health, amount of Diddy Oil, and dinero (in-game
    currency). Health is an integer where 0 means the player is dead. Diddy Oil
    can be used for special abilities and dinero is spent at shops or for
    upgrades.

    The player can also accumulate temporary shield points that absorb damage
    and carry items in an inventory purchased from stores like Donaldo El
    Trumpo's shop.

    Attributes:
        health (int): Current hit points (max 100 by default).
        diddy_oil (int): Units of Diddy Oil the player has.
        dinero (int): Amount of in-game money the player carries.
        shield (int): Temporary shield points that absorb damage before health.
        inventory (Dict[str, int]): Counts of items the player is carrying.
    """

    MAX_HEALTH = 100
    MAX_SHIELD = 50

    def __init__(self, health: int = MAX_HEALTH, diddy_oil: int = 0, dinero: int = 0, shield: int = 0):
        self.health = health
        self.diddy_oil = diddy_oil
        self.dinero = dinero
        self.shield = shield
        # inventory maps item names to quantity
        self.inventory: Dict[str, int] = {}

    # --- Health management -----------------------------------------------
    def take_damage(self, amount: int) -> None:
        """Reduce the player's health by *amount*, absorbing damage with shield first.

        Shield points are consumed before health is reduced.  Excess damage carries
        over to the player's health.  ``amount`` must be non-negative.
        """
        if amount < 0:
            raise ValueError("Damage amount cannot be negative")
        if self.shield >= amount:
            self.shield -= amount
        else:
            remaining = amount - self.shield
            self.shield = 0
            self.health = max(self.health - remaining, 0)

    def heal(self, amount: int) -> None:
        """Increase the player's health by *amount* (maximum ``MAX_HEALTH``)."""
        self.health = min(self.health + amount, self.MAX_HEALTH)

    def add_shield(self, amount: int) -> None:
        """Increase the player's shield points (capped at ``MAX_SHIELD``)."""
        if amount < 0:
            raise ValueError("Cannot add a negative amount of shield")
        self.shield = min(self.shield + amount, self.MAX_SHIELD)

    @property
    def is_alive(self) -> bool:
        """True if the player still has health remaining."""
        return self.health > 0

    # --- Diddy Oil --------------------------------------------------------
    def add_oil(self, amount: int) -> None:
        """Add *amount* of Diddy Oil to the player."""
        if amount < 0:
            raise ValueError("Cannot add a negative amount of oil")
        self.diddy_oil += amount

    # --- Inventory management ------------------------------------------------
    def add_item(self, item: str, count: int = 1) -> None:
        """Add *count* of *item* to the player's inventory."""
        if count < 0:
            raise ValueError("Cannot add a negative number of items")
        self.inventory[item] = self.inventory.get(item, 0) + count

    def use_item(self, item: str) -> bool:
        """Use one unit of *item* from inventory and apply its effect.

        Returns ``True`` if the item was in inventory and applied, ``False``
        otherwise.  Unknown items simply disappear with no effect.
        """
        if self.inventory.get(item, 0) <= 0:
            return False
        # apply the item's known effects
        if item == "Health Kit":
            self.heal(25)
        elif item == "Shield Potion":
            self.add_shield(25)
        elif item == "Golden Apple":
            self.heal(10)
            self.add_shield(10)
        else:
            print(f"You use the {item}, but nothing seems to happen.")
        self.inventory[item] -= 1
        if self.inventory[item] <= 0:
            del self.inventory[item]
        return True

    def use_oil(self, amount: int) -> bool:
        """Consume *amount* of Diddy Oil.

        Returns ``True`` if the player had enough oil and the operation succeeded.
        Otherwise, no oil is consumed and ``False`` is returned.
        """
        if amount < 0:
            raise ValueError("Cannot use a negative amount of oil")
        if amount > self.diddy_oil:
            return False
        self.diddy_oil -= amount
        return True

    # --- Dinero -----------------------------------------------------------
    def add_dinero(self, amount: int) -> None:
        """Increase the player's dinero by *amount*."""
        if amount < 0:
            raise ValueError("Cannot add a negative amount of dinero")
        self.dinero += amount

    def spend_dinero(self, amount: int) -> bool:
        """Attempt to spend *amount* of dinero.

        Returns ``True`` if the player had enough funds. Otherwise, no dinero is
        deducted and ``False`` is returned.
        """
        if amount < 0:
            raise ValueError("Cannot spend a negative amount of dinero")
        if amount > self.dinero:
            return False
        self.dinero -= amount
        return True


def random_travel_event(player: Player) -> Optional[str]:
    """Apply a random event that occurs when the player travels.

    If an event is triggered (30% chance), the player is presented with a small
    menu tailored to the type of event. Their choice may further modify state.
    There is still a separate chance for a battle with Epenstein either in the
    absence of an event or after the event resolution.

    Returns the name of the event if one happened, or ``None`` if no event was
    triggered. Side-effects (state changes, printed output) are handled by the
    event handler.
    """
    # 30% chance for a passive (no event) outcome
    if random.random() > 0.3:
        # even without an event we might run into Epenstein
        if random.random() < 0.2:
            battle_with_epenstein(player)
        return None

    event = random.choice(["stole_oil", "found_oil", "lost_health", "shop"])
    handle_travel_event(player, event)

    # after resolving the event maybe battle
    if random.random() < 0.2:
        battle_with_epenstein(player)
    return event



def handle_travel_event(player: Player, event: str) -> None:
    """Interactively resolve a travel event.

    The *event* string identifies which random occurrence happened; the player
    is given a small sub-menu of choices to react.  Effects are printed and the
    player's state may be modified.
    """
    if event == "stole_oil":
        print("Diddy darted past and grabbed some of your oil!")
        print("1) Chase him and try to snatch it back")
        print("2) Let him go")
        print("3) Bribe him with dinero to get it back")
        choice = input("Choose an action [1-3]: ").strip()
        if choice == "1":
            damage = random.randint(5, 10)
            player.take_damage(damage)
            recovered = random.randint(1, 3)
            player.diddy_oil += recovered
            print(f"You got hurt chasing Diddy (-{damage} health) but recovered {recovered} oil.")
        elif choice == "3":
            cost = random.randint(5, 15)
            if player.spend_dinero(cost):
                gained = random.randint(1, 3)
                player.diddy_oil += gained
                print(f"You paid {cost} dinero and recovered {gained} oil.")
            else:
                print("You didn't have enough dinero; Diddy keeps the oil.")
        else:
            print("You let Diddy go.  Maybe next time you'll hold tight!")
    elif event == "found_oil":
        print("You spot a glint of baby oil on the ground.")
        print("1) Pick it up")
        print("2) Ignore it")
        print("3) Mark the spot for later")
        choice = input("Choose an action [1-3]: ").strip()
        if choice == "1":
            found = random.randint(1, 5)
            player.diddy_oil += found
            print(f"You scoop up {found} oil.")
        elif choice == "3":
            print("You make a mental note to return once you're loaded.")
        else:
            print("You walk past it.  Maybe someone else will find it.")
    elif event == "lost_health":
        print("You stumbled and took a nasty tumble.")
        print("1) Climb back up and bandage yourself")
        print("2) Push on through")
        print("3) Sit and rest for a moment")
        choice = input("Choose an action [1-3]: ").strip()
        if choice == "1":
            heal = random.randint(5, 10)
            player.heal(heal)
            print(f"You patch yourself up and recover {heal} health.")
        elif choice == "3":
            if random.random() < 0.5:
                extra = random.randint(1, 5)
                player.take_damage(extra)
                print(f"While resting you slip again and lose {extra} health.")
            else:
                recovered = random.randint(5, 15)
                player.heal(recovered)
                print(f"The extra rest actually helps; you gain {recovered} health.")
    elif event == "shop":
        print("As you wander a clearing, you spot a small stall manned by Donaldo El Trumpo!")
        shop(player)
    else:
        # unknown event shouldn't happen
        print("An odd silence falls over the path… nothing to do.")


def display_stats(player: Player) -> None:
    """Print the player's current health, shield, Diddy Oil, dinero, and items."""
    print(f"Health: {player.health}/{player.MAX_HEALTH}")
    print(f"Shield: {player.shield}/{player.MAX_SHIELD}")
    print(f"Diddy Oil: {player.diddy_oil}")
    print(f"Dinero: {player.dinero}")
    if player.inventory:
        print("Inventory:")
        for name, qty in player.inventory.items():
            print(f"  {name} x{qty}")
    else:
        print("Inventory: empty")
    print("-")


def battle_with_epenstein(player: Player) -> None:
    """Initiate a quick typing battle vs Epenstein.

    The player must type the word ``DIDDY`` as fast as possible.  If they either
    enter the wrong word or take longer than ``BATTLE_TIMEOUT`` seconds, they
    lose health; otherwise they escape unscathed.
    """
    BATTLE_TIMEOUT = 2.0  # seconds
    print("!!! Epenstein appears! Type 'DIDDY' as fast as you can to fight him!")
    start = time.time()
    response = input(">>> ").strip().upper()
    elapsed = time.time() - start
    if response == "DIDDY" and elapsed <= BATTLE_TIMEOUT:
        print(f"You typed fast enough ({elapsed:.2f}s). Epenstein recoils.")
    else:
        damage = random.randint(10, 25)
        player.take_damage(damage)
        print(f"Too slow or wrong word! You take {damage} damage.")


def player_action_menu(player: Player) -> None:
    """Present the player with three actions and update state accordingly.

    Choices are:
      1. Travel  the player loses 10 health and may trigger a random event (no dinero cost).
      2. Fortnite – the player uses 1 unit of Diddy Oil to "play" the game.
      3. Nap – the player heals 20 health (capped at MAX_HEALTH).

    The function reads input from standard input and validates the choice.  It
    prints the resulting state changes.
    """
    options = {
        "1": "travel",
        "2": "fortnite",
        "3": "nap",
        "4": "stats",
        "5": "inventory",
    }

    print("What would you like to do?")
    print("1) Travel")
    print("2) Fortnite")
    print("3) Nap")
    print("4) View stats")
    print("5) Inventory")

    choice = input("Enter the number of your choice: ").strip()
    action = options.get(choice)
    if not action:
        print("Invalid selection – nothing happens.")
        return

    if action == "travel":
        if player.health <= 0:
            print("You can't travel; you're already out of health.")
        else:
            print("You travel across the island...")
            player.take_damage(10)
            if not player.spend_dinero(20):
                print("You didn't have enough dinero for the trip.")
            # random event on travel (may show additional options)
            random_travel_event(player)
    elif action == "inventory":
        inventory_menu(player)
    elif action == "fortnite":
        # fortune-based oil game
        if player.diddy_oil <= 0:
            print("You have no Diddy Oil to play Fortnite.")
        else:
            try:
                guess = int(input("Pick a number between 1 and 5: ").strip())
            except ValueError:
                print("That's not a number—game over!")
                guess = None
            if guess is None or guess < 1 or guess > 5:
                print("Invalid guess; you lose 1 oil as penalty.")
                player.diddy_oil = max(player.diddy_oil - 1, 0)
            else:
                roll = random.randint(1, 5)
                if guess == roll:
                    reward = random.randint(1, 3)
                    player.diddy_oil += reward
                    print(f"Lucky! You guessed {roll} and earned {reward} oil.")
                else:
                    loss = random.randint(1, 2)
                    player.diddy_oil = max(player.diddy_oil - loss, 0)
                    print(f"Unlucky, it was {roll}. You lost {loss} oil.")
    elif action == "nap":
        print("You take a quick nap and feel refreshed.")
        player.heal(20)
    elif action == "stats":
        display_stats(player)




def dream_event(player: Player) -> None:
    """5% chance each turn to dream of Epenstein and Donaldo stealing oil.

    Both figures appear in a surreal dream and pilfer half of the player's
    current Diddy Oil (rounded down).  If the player has no oil the dream
    simply passes.
    """
    if random.random() < 0.05:
        if player.diddy_oil > 0:
            stolen = player.diddy_oil // 2
            player.diddy_oil -= stolen
            print("You drift into a bizarre dream…")
            print("Epenstein and Donaldo El Trumpo loom over you, laughing!")
            print(f"When you wake up you realize they've taken {stolen} Diddy Oil.")
            print(f"Oil remaining: {player.diddy_oil}")
        else:
            # no oil to steal, just a weird dream
            print("You shake off a strange dream where shadowy figures pointed at your empty pockets.")

# shop and inventory helpers ------------------------------------------------

def shop(player: Player) -> None:
    """Allow the player to purchase items from Donaldo El Trumpo's shop."""
    print("Welcome to Donaldo El Trumpo's legendary shop!")
    while True:
        print("Items for sale:")
        for idx, (name, data) in enumerate(SHOP_ITEMS.items(), start=1):
            print(f"{idx}) {name} - {data['price']} dinero")
        print("q) Leave shop")
        choice = input("Choose an item to buy or 'q' to leave: ").strip()
        if choice.lower() == 'q':
            print("You exit the shop.")
            break
        try:
            idx = int(choice)
        except ValueError:
            print("Invalid selection.")
            continue
        if idx < 1 or idx > len(SHOP_ITEMS):
            print("Invalid selection.")
            continue
        item_name = list(SHOP_ITEMS.keys())[idx-1]
        price = SHOP_ITEMS[item_name]['price']
        if player.spend_dinero(price):
            player.add_item(item_name)
            print(f"You purchased a {item_name}.")
        else:
            print("You don't have enough dinero.")
    print("Thanks for visiting Donaldo!")


def inventory_menu(player: Player) -> None:
    """Let the player view and use items from their inventory."""
    if not player.inventory:
        print("Your inventory is empty.")
        return
    print("Your inventory:")
    for idx, (name, qty) in enumerate(player.inventory.items(), start=1):
        print(f"{idx}) {name} x{qty}")
    print("q) Back")
    choice = input("Choose an item to use or 'q' to go back: ").strip()
    if choice.lower() == 'q':
        return
    try:
        idx = int(choice)
    except ValueError:
        print("Invalid selection.")
        return
    if idx < 1 or idx > len(player.inventory):
        print("Invalid selection.")
        return
    item_name = list(player.inventory.keys())[idx-1]
    if player.use_item(item_name):
        print(f"You used a {item_name}.")
    else:
        print(f"You don't have any {item_name} left.")


# simple test/demo logic when run as script
if __name__ == "__main__":
    p = Player()
    print("Welcome to Escape From Epenstein Island!")
    # boost the player with some starting resources for demo
    p.take_damage(25)
    p.add_oil(5)
    p.add_dinero(100)
    # give a couple of starter items so the inventory feature can be tried
    p.add_item("Health Kit", 1)
    p.add_item("Shield Potion", 1)

    # main game loop runs until death
    while p.is_alive:
        player_action_menu(p)
        # dream check after each action
        dream_event(p)
        if not p.is_alive:
            print("You have perished on the island...")
            break
    print("Game over.")
