# blackjack.py
# Main game file for Blackjack with Pygame
# Ibrahim Taha
# 04.08.2025

import pygame
import os
import sys
from deck import Deck  # Import Deck from deck.py
from hand import Hand  # Import Hand from hand.py

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (0, 0, 139)  # Dark blue
TEXT_COLOR = (255, 255, 255)  # White
BUTTON_COLOR = (200, 200, 200)  # Light gray
BUTTON_HOVER_COLOR = (150, 150, 150)  # Darker gray
CARD_WIDTH = 100
CARD_HEIGHT = 145
WIN_COLOR = (0, 255, 0)  # Green
LOSS_COLOR = (255, 0, 0)  # Red

# Game states
STATE_DEALING = 0
STATE_PLAYER_TURN = 1
STATE_DEALER_TURN = 2
STATE_GAME_OVER = 3





class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blackjack")

        # Load card images
        self.card_images = {}
        self.load_card_images()

        # Create font objects
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Add score tracking
        self.wins = 0
        self.losses = 0

        # Initialize game
        self.reset_game()

        # Initialize game
        self.reset_game()

        # Add dealer score tracking
        self.dealer_wins = 0
        self.dealer_losses = 0


    def load_card_images(self):
        """Load all card images from the 'img' folder"""
        # Using the 'img' folder as seen in your screenshots
        image_dir = 'img'

        # Try to load card back image (using red_back.png from your folder)
        try:
            back_path = os.path.join(image_dir, 'red_back.png')
            if os.path.exists(back_path):
                self.card_back = pygame.image.load(back_path)
                self.card_back = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
            else:
                print(f"Warning: Card back image not found at {back_path}")
                # Create a default card back
                self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                self.card_back.fill((0, 0, 128))  # Navy blue
        except pygame.error as e:
            print(f"Error loading card back: {e}")
            # Create a default card back
            self.card_back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            self.card_back.fill((0, 0, 128))  # Navy blue

        # Define card values and suits for filenames
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        suits = ['clubs', 'diamonds', 'hearts', 'spades']

        # Load each card image or create a default
        for suit in suits:
            for value in values:
                filename = f"{value}_of_{suit}.png"
                try:
                    path = os.path.join(image_dir, filename)
                    if os.path.exists(path):
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
                    else:
                        print(f"Warning: Card image not found: {filename}")
                        # Create a default card image
                        img = self.create_default_card(value, suit)
                    self.card_images[filename] = img
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
                    # Create a default card image
                    img = self.create_default_card(value, suit)
                    self.card_images[filename] = img

    def create_default_card(self, value, suit):
        """Create a default card image if the image file is missing"""
        img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        img.fill((255, 255, 255))  # White background

        # Add a border
        pygame.draw.rect(img, (0, 0, 0), (0, 0, CARD_WIDTH, CARD_HEIGHT), 2)

        # Add text for value and suit
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{value.upper()} of {suit.capitalize()}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
        img.blit(text, text_rect)

        return img

    def reset_game(self):
        """Reset the game to its initial state"""
        self.deck = Deck()
        self.deck.shuffle()

        self.player_hand = Hand()
        self.dealer_hand = Hand()

        # Deal initial cards
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

        self.game_state = STATE_PLAYER_TURN
        self.message = "Your turn: Hit or Stand?"
        self.show_dealer_first_card_only = True

    def player_hit(self):
        """Player takes another card"""
        # Deal one card to the player
        self.player_hand.add_card(self.deck.deal())

        # Check if player busts
        if self.player_hand.is_busted():
            self.game_state = STATE_GAME_OVER
            self.message = "You busted! Dealer wins."
            self.losses += 1  # Increment loss counter
            self.show_dealer_first_card_only = False

    def player_stand(self):
        """Player stands, dealer's turn"""
        self.game_state = STATE_DEALER_TURN
        self.show_dealer_first_card_only = False
        self.dealer_play()

    def dealer_play(self):
        """Dealer's turn logic"""
        # Dealer hits until they have 17 or more
        while self.dealer_hand.calculate_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())

        # Determine the winner
        self.game_state = STATE_GAME_OVER

        player_value = self.player_hand.calculate_value()
        dealer_value = self.dealer_hand.calculate_value()

        if self.dealer_hand.is_busted():
            self.message = "Dealer busted! You win!"
            self.wins += 1  # Increment player wins
            self.dealer_losses += 1  # Increment dealer losses
        elif dealer_value > player_value:
            self.message = "Dealer wins!"
            self.losses += 1  # Increment player losses
            self.dealer_wins += 1  # Increment dealer wins
        elif player_value > dealer_value:
            self.message = "You win!"
            self.wins += 1  # Increment player wins
            self.dealer_losses += 1  # Increment dealer losses
        else:
            self.message = "Push! It's a tie."
            # No score change for a tie

    def draw_card(self, card, x, y, face_up=True):
        """Draw a card at the specified position"""
        if face_up:
            filename = card.get_image_filename()
            if filename in self.card_images:
                self.screen.blit(self.card_images[filename], (x, y))
            else:
                # If image not found, create a default card
                print(f"Warning: Card image not found: {filename}")
                default_card = self.create_default_card(
                    str(card.raw_value) if card.raw_value <= 10 else card.name.split()[0].lower(),
                    card.suit.lower()
                )
                self.screen.blit(default_card, (x, y))
        else:
            # Draw card back
            self.screen.blit(self.card_back, (x, y))

    def draw_hand(self, hand, x, y, is_dealer=False):
        """Draw all cards in a hand"""
        for i, card in enumerate(hand.cards):
            # For dealer's hand, hide the second card if needed
            face_up = True
            if is_dealer and i > 0 and self.show_dealer_first_card_only:
                face_up = False

            self.draw_card(card, x + i * 30, y, face_up)

    def check_button_click(self, mouse_pos, x, y, width, height):
        """Check if a button was clicked"""
        return (x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height)

    def draw_button(self, text, x, y, width, height):
        """Draw a button"""
        mouse = pygame.mouse.get_pos()

        # Check if mouse is over button
        if x <= mouse[0] <= x + width and y <= mouse[1] <= y + height:
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, (x, y, width, height))
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, (x, y, width, height))

        # Add text to button
        text_surf = self.small_font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surf, text_rect)

    # Add the new method here
    def draw_score_counters(self):
        """Draw the win/loss counters with appropriate colors"""
        # Create a slightly larger, but not bold font
        score_font = pygame.font.SysFont(None, 30)

        # Dealer's score (next to dealer area)
        dealer_win_text = score_font.render(f"Wins: {self.dealer_wins}", True, WIN_COLOR)
        dealer_loss_text = score_font.render(f"Losses: {self.dealer_losses}", True, LOSS_COLOR)

        # Player's score (next to player area)
        player_win_text = score_font.render(f"Wins: {self.wins}", True, WIN_COLOR)
        player_loss_text = score_font.render(f"Losses: {self.losses}", True, LOSS_COLOR)

        # Blit dealer scores next to dealer area
        self.screen.blit(dealer_win_text, (50, 200))
        self.screen.blit(dealer_loss_text, (50, 230))

        # Blit player scores next to player area
        self.screen.blit(player_win_text, (50, 500))
        self.screen.blit(player_loss_text, (50, 530))

    def draw_game(self):
        """Draw the game state"""
        # Fill background
        self.screen.fill(BACKGROUND_COLOR)

        # Draw hands
        self.draw_hand(self.dealer_hand, 50, 50, True)
        self.draw_hand(self.player_hand, 50, 350)

        # Draw scores
        dealer_score = self.dealer_hand.calculate_value() if not self.show_dealer_first_card_only else "?"
        player_score = self.player_hand.calculate_value()

        dealer_text = self.font.render(f"Dealer: {dealer_score}", True, TEXT_COLOR)
        player_text = self.font.render(f"Player: {player_score}", True, TEXT_COLOR)

        self.screen.blit(dealer_text, (50, 10))
        self.screen.blit(player_text, (50, 310))

        # Add this line to call the new method
        self.draw_score_counters()

        # Draw message
        message_text = self.font.render(self.message, True, TEXT_COLOR)
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 250))

        # Draw buttons based on game state
        if self.game_state == STATE_PLAYER_TURN:
            self.draw_button("Hit", SCREEN_WIDTH // 2 - 125, 500, 100, 40)
            self.draw_button("Stand", SCREEN_WIDTH // 2 + 25, 500, 100, 40)
        elif self.game_state == STATE_GAME_OVER:
            self.draw_button("Play Again", SCREEN_WIDTH // 2 - 50, 500, 100, 40)

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()

        while running:
            # Draw everything
            self.draw_game()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Check which button was clicked based on game state
                    if self.game_state == STATE_PLAYER_TURN:
                        # Hit button
                        if self.check_button_click(mouse_pos, SCREEN_WIDTH // 2 - 125, 500, 100, 40):
                            self.player_hit()

                        # Stand button
                        elif self.check_button_click(mouse_pos, SCREEN_WIDTH // 2 + 25, 500, 100, 40):
                            self.player_stand()

                    # Play Again button
                    elif self.game_state == STATE_GAME_OVER:
                        if self.check_button_click(mouse_pos, SCREEN_WIDTH // 2 - 50, 500, 100, 40):
                            self.reset_game()

            # Update display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(30)

        pygame.quit()
        sys.exit()


# Run the game if this file is executed directly
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()