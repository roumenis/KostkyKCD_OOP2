from game import Game
WIN_REW = 20
LOOSE_PEN = 20

if __name__ == "__main__":
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