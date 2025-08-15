import random, json, os

PLAYERS_FILE = "players.json"

START_COINS = 100
WIN_REW = 20
LOOSE_PEN = 20

class Player:
    def __init__(self, name, score=0, coins=None):
        self.name = name
        self.score = 0 # Initialize score to 0 from the start
        self.coins = coins if coins is not None else START_COINS # Default coins to START_COINS

    def add_score(self, points):
        self.score += points

    def change_coins(self, amount):
        self.coins += amount
        self.save()

    @classmethod
    def load_players(cls):
        if os.path.exists(PLAYERS_FILE):
            with open(PLAYERS_FILE, "r") as f:
                data = json.load(f)
                return {name: cls(name, coins=coins) for name, coins in data.items()}
        return {}

    @classmethod
    def save_players(cls, players):
        with open(PLAYERS_FILE, "w") as f:
            json.dump({player.name: player.coins for player in players.values()}, f, indent=4)

    def save(self):
        players = self.load_players()
        players[self.name] = self
        self.save_players(players)

    @classmethod
    def load_or_create(cls, name):
        players = cls.load_players()
        if name in players:
            return players[name]
        else:
            player = cls(name)
            player.save()
            return player

# TODO - Make some logic for AI player
class AIPlayer(Player):
    def choose_dices(self, scoring_dices):
        # AI logic to choose which dices to keep
        # For simplicity, let's say AI keeps all scoring dices
        return scoring_dices
    def decide_continue(self):
        # AI logic to decide whether to continue rolling
        # For simplicity, let's say AI always continues if it has scoring dices
        return True if self.score > 0 else False

class Dice:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        self.value = random.randint(1,6)
        return self.value

class RollSet:
    def __init__(self, count = 6):
        self.dice = [Dice() for _ in range(count)]
        self.remaining = count

    def roll_all(self):
        self.remaining = len(self.dice)
        return self.roll_remaining()

    def roll_selected(self, indices):
        for i in indices:
            self.dice[i].roll()
        return self.get_values()

    def roll_remaining(self): # This method rolls the remaining dice in the set and returns their values.
        values = []
        for i in range(self.remaining):
            values.append(self.dice[i].roll())
        return values

    def get_values(self):
        return [die.value for die in self.dice] # This method returns the current values of all dice in the set.


class Game:
    def __init__(self, target_score=1500):
        all_players = Player.load_players()
        if not all_players:
            print("No players found, creating new ones.")

        print("Available players:")
        for name in all_players:
            print(f"- {name}")

        # Choose player 1
        name1 = input("Choose first player: ").strip()
        player1 = Player.load_or_create(name1)

        # Choose player 2
        name2 = input("Choose second player: ").strip()
        player2 = Player.load_or_create(name2)

        self.players = [player1, player2]
        print(f"Players: {player1.name} vs {player2.name}")
        self.roll_set = RollSet()
        self.target_score = target_score

    def score_counter(self, values):
        score = 0
        counts = {i: values.count(i) for i in range(1, 7)}

        # Special combinations
        if sorted(values) == [1, 2, 3, 4, 5, 6]:
            return 1500
        if sorted(values) == [2, 3, 4, 5, 6]:
            return 750
        if sorted(values) == [1, 2, 3, 4, 5]:
            return 500

        # Check for triples
        for num in range(1, 7):
            if counts[num] >= 3:
                if num == 1:
                    # 1×1×1 = 1000,
                    triple_score = 1000
                else:
                    # ex. 2×2×2 = 200
                    triple_score = num * 100

                # Counting multiplers (4 same = multipler, 5 same = 4×, 6 same = 8×)
                multiplier = 2 ** (counts[num] - 3)  # 3 same → 1×, 4 same → 2×, 5 same → 4×...
                score += triple_score * multiplier
                counts[num] = 0

        score += counts[1] * 100
        score += counts[5] * 50

        return score

    def get_scoring_dice(self, values):
        # Special combinations
        sorted_vals = sorted(values)
        if sorted_vals in ([1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6], [1, 2, 3, 4, 5]):
            print("Special combination!")
            return values.copy()

        counts = {i: values.count(i) for i in range(1, 7)}
        scoring = []

        # Triples and more
        for num in range(1, 7):
            if counts[num] >= 3:
                scoring.extend([num] * counts[num])
                counts[num] = 0

        # 1  and 5 scoring
        scoring.extend([1] * counts[1])
        scoring.extend([5] * counts[5])

        if not scoring:
            return []

        print("Pointing dices:", scoring)

        while True:
            selection = input("Select dices to take (separated by space): ")
            try:
                chosen = [int(x) for x in selection.split()]
                temp_scoring = scoring.copy()
                valid = True
                for num in chosen:
                    if num in temp_scoring:
                        temp_scoring.remove(num)
                    else:
                        valid = False
                        break
                if valid:
                    return chosen
                else:
                    print("Invalid selection, try again.")
            except ValueError:
                print("Invalid input, please enter numbers separated by spaces.")

    def play_turn(self, player):
        self.roll_set.remaining = 6
        round_score = 0

        while True:
            print(f"\n{player.name} plays!")
            values = self.roll_set.roll_remaining()
            print(f"{player.name} threw: {values}")

            chosen = self.get_scoring_dice(values)

            if not chosen:
                print("No scoring dice! Bad luck")
                return

            print(f"Scoring dices: {chosen}")

            points = self.score_counter(chosen)
            round_score += points

            self.roll_set.remaining -= len(chosen)

            # HOT DICE
            if self.roll_set.remaining == 0:
                print("Hot dice! You play with all dices again.")
                self.roll_set.remaining = 6

            cont = input("Another run? (y/n): ").strip().lower()
            if cont != 'y':
                player.add_score(round_score)
                print(f"End of round, {player.name} scored {round_score} and has {player.score} points.")
                return

    def play(self):
        print("=== Hra V Kostky ===")
        while True:
            for player in self.players:
                self.play_turn(player)
                if player.score >= self.target_score:
                    print(f"\n{player.name} won with score {player.score} !")
                    player.change_coins(20)
                    for other in self.players:
                        if other != player:
                            other.change_coins(-20)
                    return

if __name__ == "__main__":
        # test score_counter
        #game = Game(["Test"])

        # test_cases = [
        #   ([1], 100),
        #   ([5], 50),
        #   ([1, 1, 1], 1000),
        #   ([1, 1, 1, 1], 2000),
        #   ([1, 1, 1, 1, 1], 4000),
        #   ([1, 1, 1, 1, 1, 1], 8000),
        #   ([2, 2, 2], 200),
        #   ([2, 2, 2, 2], 400),
        #   ([2, 2, 2, 2, 2], 800),
        #   ([2, 2, 2, 2, 2, 2], 1600),
        #   ([3, 3, 3], 300),
        #   ([4, 4, 4], 400),
        #   ([5, 5, 5], 500),
        #   ([6, 6, 6], 600),
        #   ([1, 2, 3, 4, 5], 500),
        #   ([2, 3, 4, 5, 6], 750),
        #   ([1, 2, 3, 4, 5, 6], 1500)
        #]

        #for dice, expected in test_cases:
        #   result = game.score_counter(dice)
        #  print(f"{dice} → {result} points (expected {expected}) {'✅' if result == expected else '❌'}")

        # Game start
        while True:
            game = Game()
            game.play()
            again = input("Play again? (y/n): ").strip().lower()
            if again != 'y':
                print("Thanks for playing!")
                break
            print("Starting a new game...")
            game.roll_set = RollSet()  # Reset roll set for new game