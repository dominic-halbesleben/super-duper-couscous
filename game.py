"""Core game logic for Escape From Epenstein Island."""

import random
import time
from typing import Optional


class Player:
    """Represents a player in Escape From Epenstein Island.

    Tracks the player's current health, amount of Diddy Oil, and dinero (in-game
    currency). Health is an integer where 0 means the player is dead. Diddy Oil
    can be used for special abilities and dinero is spent at shops or for
    upgrades.

    Attributes:
        health (int): Current hit points (max 100 by default).
        diddy_oil (int): Units of Diddy Oil the player has.
        dinero (int): Amount of in-game money the player carries.
    """

    MAX_HEALTH = 100

    def __init__(self, health: int = MAX_HEALTH, diddy_oil: int = 0, dinero: int = 0):
        self.health = health
        self.diddy_oil = diddy_oil
        self.dinero = dinero

    # --- Health management -----------------------------------------------
    def take_damage(self, amount: int) -> None:
        """Reduce the player's health by *amount* (minimum 0)."""
        self.health = max(self.health - amount, 0)

    def heal(self, amount: int) -> None:
        """Increase the player's health by *amount* (maximum ``MAX_HEALTH``)."""
        self.health = min(self.health + amount, self.MAX_HEALTH)

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

    Returns a short description of the event if one happened, or ``None`` if no
    event was triggered. Events may modify the player's state.
    Additionally may trigger a battle with Epenstein.
    """
    # 30% chance for a passive event
    if random.random() > 0.3:
        # maybe still battle?
        if random.random() < 0.2:
            # 20% chance to start a battle anyway
            battle_with_epenstein(player)
        return None

    event = random.choice(["stole_oil", "found_oil", "lost_health"])
    if event == "stole_oil":
        # Diddy steals some Baby Oil
        stolen = min(player.diddy_oil, random.randint(1, 3))
        player.diddy_oil -= stolen
        msg = f"Diddy stole your Baby Oil ({stolen} units)!"
    elif event == "found_oil":
        found = random.randint(1, 5)
        player.diddy_oil += found
        msg = f"You found {found} units of Baby Oil on the path."
    else:  # lost_health
        damage = random.randint(5, 15)
        player.take_damage(damage)
        msg = f"A nasty fall! You lost {damage} health."

    print(msg)
    # after event maybe battle
    if random.random() < 0.2:
        battle_with_epenstein(player)
    return msg



def display_stats(player: Player) -> None:
    """Print the player's current health, Diddy Oil, and dinero."""
    print(f"Health: {player.health}/{player.MAX_HEALTH}")
    print(f"Diddy Oil: {player.diddy_oil}")
    print(f"Dinero: {player.dinero}")
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
      1. Travel – the player loses 10 health and spends 20 dinero.
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
    }

    print("What would you like to do?")
    print("1) Travel")
    print("2) Fortnite")
    print("3) Nap")
    print("4) View stats")

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
            # random event on travel
            random_travel_event(player)
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


# simple test/demo logic when run as script
if __name__ == "__main__":
    p = Player()
    print("Welcome to Escape From Epenstein Island!")
    # boost the player with some starting resources for demo
    p.take_damage(25)
    p.add_oil(5)
    p.add_dinero(100)

    # main game loop runs until death
    while p.is_alive:
        player_action_menu(p)
        if not p.is_alive:
            print("You have perished on the island...")
            break
    print("Game over.")
