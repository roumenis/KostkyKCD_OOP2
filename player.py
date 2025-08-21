import json, os

PLAYERS_FILE = "players.json"

START_COINS = 100

class Player:
    def __init__(self, name, score=0, coins=None):
        self.name = name
        self.score = 0 # Initialize score to 0 from the start
        self.coins = coins if coins is not None else START_COINS # Default coins to START_COINS

    def add_score(self, points):
        self.score += points

    def change_coins(self, amount):
        self.coins += amount
        if self.coins <= 0:
            print(f"Player {self.name} has run out of coins! Deleting player :)")
            self.delete_player()
        else:
            self.save()

    def delete_player(self):
        players = self.load_players()
        if self.name in players:
            del players[self.name]
            self.save_players(players)
            print(f"Player {self.name} has been deleted.") 

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
        if round_score < self.risk_low:
            return random.random() < self.risk_low_chance / 100
        elif round_score < self.risk_high:
            return random.random() < self.risk_high_chance / 100 and remaining_dice >= self.min_dice_continue
        else:
            return False