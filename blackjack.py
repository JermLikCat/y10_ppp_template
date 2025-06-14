class BlackjackGame:
    def __init__(self):
        # Initialize money
        self.player_money = 1000
        
        # Opening screen
        self.display_opening_screen()
        
        # Bet screen (Game loop)
        self.game_loop()
    
    def display_opening_screen(self):
        print("Welcome to Blackjack!")
        print("Hope you have fun!\n")
    
    def display_bet_screen(self, player_money):
        print(f"Money: {player_money}")
        print()
        bet_amount = input("How much would you like to bet? ")
        while not bet_amount.isnumeric() or int(bet_amount) <= 0 or int(bet_amount) > player_money:
            print("Invalid bet amount!")
            bet_amount = input("How much would you like to bet? ")
        return int(bet_amount)
    
    def game_loop(self):
        while self.player_money > 0:
            bet = self.display_bet_screen(self.player_money)
            self.player_money -= bet
            round = BlackjackRound(self.player_money, bet)
            self.player_money = round.player_money
        print("You ran out of money!")
        
class BlackjackRound:
    SUITS = ("\u2663", "\u2665", "\u2666", "\u2660")
    RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
    
    def __init__(self, player_money, bet, cards = None, dealer_deck = None, player_deck = None):
        self.player_money = player_money
        self.bet = bet
        
        if cards is None:  
            # Initialize cards
            self.cards = self.generate_card_list(self.SUITS, self.RANKS)
        else:
            self.cards = cards
        
        if dealer_deck is None:
            # Draw dealer cards
            self.dealer_deck = Deck()
        else:
            self.dealer_deck = dealer_deck
        self.dealer_deck.draw(self.cards, 2)

        # Initialize empty player cards
        if player_deck is None:
            self.player_deck = Deck()
        else:
            self.player_deck = player_deck
        self.player_deck.draw(self.cards, 2)
        self.split_check()
        self.game_loop()
    
    def game_loop(self):
        # Blackjack Check
        if self.player_deck.return_value() == 21:
            print("Blackjack!")
        else:
            while self.user_choice():
                # Check if player has lost
                if self.did_bust(self.player_deck):
                    break
                
        # Display dealer's and player's final cards
        print("Your final cards: ")
        self.player_deck.print_deck()
        
        print("Dealer's current cards: ")
        self.dealer_deck.print_deck()
        while self.dealer_deck.return_value() < 17:
            self.dealer_deck.draw(self.cards)
        
        print("Dealer's final cards: ")
        self.dealer_deck.print_deck()
        
        # Check final outcome
        self.player_money += self.check_final_outcome(self.bet)
    
    def split_check(self):
        if self.player_deck.can_split() and self.bet * 2 < self.player_money:
            print("Your deck: ")
            self.player_deck.print_deck()
            split = input("Would you like to split? (y/n) ").strip().lower()
            while split != "y" and split != "n":
                print("Invalid input! Please only input 'hit' or 'stand'.")
                split = input("Would you like to split? (y/n) ").strip().lower()
            
            if split == "y":
                self.split()
                
    def split(self):
        
        # make a new round with 1 of the same card
        round = BlackjackRound()
        self.player_money = round.player_money
    
    def user_choice(self) -> bool:
        """Returns False if hit, and returns True if stand."""
        
        # Print current deck
        print("Your deck: ")
        self.player_deck.print_deck()
        
        # Print dealer deck with second card hidden
        print("Dealer's deck: ")
        self.dealer_deck.print_deck([1])
        
        
            
        
        choice = input("Hit or stand? ").strip().lower()
        while choice != "hit" and choice != "stand":
            print("Invalid input! Please only input 'hit' or 'stand'.")
            choice = input("Hit or stand? ").strip().lower()
        
        if choice == "hit":
            self.player_deck.draw(self.cards, 1)
            return True
        elif choice == "stand":
            return False
    
    def generate_card_list(self, suits, ranks):
        result = []
        for suit in suits:
            for rank in ranks:
                result.append(suit + rank)
        return Deck(result)
    
    def did_bust(self, deck) -> bool:
        if deck.return_value() > 21:
            return True
        else:
            return False
        
    def check_final_outcome(self, bet):
        player_did_bust = self.did_bust(self.player_deck)
        dealer_did_bust = self.did_bust(self.dealer_deck)
        
        # If both player and dealer bust
        if player_did_bust and dealer_did_bust:
            return self.push(bet)
        elif player_did_bust and not dealer_did_bust:
            return self.loss(bet)
        elif not player_did_bust and dealer_did_bust:
            return self.win(bet)
        else:
            player_deck_val = self.player_deck.return_value()
            dealer_deck_val = self.dealer_deck.return_value()
            if player_deck_val > dealer_deck_val:
                return self.win(bet)
            elif player_deck_val < dealer_deck_val:
                return self.loss(bet)
            elif player_deck_val == dealer_deck_val:
                return self.push(bet)
        
    # Outcomes
    def push(self, bet):
        print("Push!")
        return bet
        
    def win(self, bet):
        print("You won!")
        return bet * 2
        
    def loss(self, bet):
        print("You lost.")
        return 0
        
class Deck:
    def __init__(self, cards: list[str] = None):
        # Prevent same list from being used in different constructions of objects of Deck (Strange python thing, more info here: https://stackoverflow.com/questions/366422/how-can-i-avoid-issues-caused-by-pythons-early-bound-default-parameters-e-g-m)
        if cards is None: 
            self.cards = []
        else:
            self.cards = cards
    
    def draw(self, card_deck, quantity: int = 1):
        from random import randint
        
        for _ in range(quantity):
            index = randint(0, len(card_deck.cards) - 1)
            self.cards.append(card_deck.cards[index])
            card_deck.cards.pop(index)
        
    def print_deck(self, hidden: list[int] = None):
        """Displays deck with all indexes in list of int given being hidden"""
        
        # Prevent same list from being used in different calls
        if hidden is None: 
            hidden = []
        
        if len(self.cards) > 0:
            for x, card in enumerate(self.cards):
                if x not in hidden:
                    print(card, end = " ")
                else:
                    print("X", end = " ")
        else:
            print("No cards!", end = "")
                
        print()
    
    def return_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            if card[1] not in ['A', 'K', 'Q', 'J']:
                value += int(card[1:])
            elif card[1] in ['K', 'Q', 'J']:
                value += 10
            elif card[1] in ['A']:
                # Deal with aces at the end
                aces += 1
                
                # Add one to value first
                value += 1
                
        # Ace logic
        for _ in range(aces):
            if value <= 11: # if value + 10 < 21
                value += 10
        
        return value
    
    def can_split(self):
        if len(self.cards) == 2:
            if self.cards[0][1:] == self.cards[1][1:]:
                return True
        return False
    
game = BlackjackGame()