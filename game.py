from player import Player, AIPlayer
from dice import RollSet

class Game:
    def __init__(self):
        #load players or create new ones
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

        # Choose game type
        self.target_score, self.bet = self.game_type()
        print(f"Game type selected: Target score {self.target_score} bet is {self.bet} coins.")

        self.players = [player1, player2]
        print(f"Players: {player1.name} vs {player2.name}")
        self.roll_set = RollSet()

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
                    player.change_coins(self.bet)
                    for other in self.players:
                        if other != player:
                            other.change_coins(-self.bet)
                    return
    def game_type(self):
        print("Choose game type: ")
        print("1:   Beggars - Target score 1500, Bet: 10 coins")
        print("2:   Bourgeois - Target score 2000, Bet: 20 coins")
        print("3:   High stakes - Target score 3000, Bet: 50 coins")

        while True:
            choice = input("Enter your chouice (1-3): ").strip()
            if choice == '1':
                return 1500, 10
            elif choice == '2':
                return 2000, 20
            elif choice == '3':
                return 3000, 50
            else:
                print("Invalid choice, please choose 1, 2, or 3 !!!")