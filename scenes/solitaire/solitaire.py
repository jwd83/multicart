import pygame
import random
from scene import Scene
from utils import *


class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # 0=Hearts, 1=Diamonds, 2=Clubs, 3=Spades
        self.rank = rank  # 1=Ace, 2-10=Numbers, 11=Jack, 12=Queen, 13=King
        self.face_up = False
        self.rect = pygame.Rect(0, 0, 60, 80)
        self.dragging = False
        
    def is_red(self):
        return self.suit in [0, 1]  # Hearts and Diamonds
        
    def is_black(self):
        return self.suit in [2, 3]  # Clubs and Spades
        
    def can_stack_on(self, other_card):
        """Can this card be placed on another card in tableau?"""
        if other_card is None:
            return self.rank == 13  # Only Kings on empty spaces
        return (self.is_red() != other_card.is_red() and 
                self.rank == other_card.rank - 1)
                
    def can_place_on_foundation(self, foundation_pile):
        """Can this card be placed on foundation?"""
        if not foundation_pile:
            return self.rank == 1  # Only Aces on empty foundations
        top_card = foundation_pile[-1]
        return (self.suit == top_card.suit and 
                self.rank == top_card.rank + 1)
                
    def get_rank_name(self):
        names = {1: "A", 11: "J", 12: "Q", 13: "K"}
        return names.get(self.rank, str(self.rank))
        
    def get_suit_symbol(self):
        symbols = ["♥", "♦", "♣", "♠"]
        return symbols[self.suit]


class Solitaire(Scene):
    def __init__(self, game):
        super().__init__(game)
        
        # Game state
        self.deck = self.create_deck()
        self.stock = []
        self.waste = []
        self.foundations = [[] for _ in range(4)]  # One for each suit
        self.tableau = [[] for _ in range(7)]  # 7 columns
        
        # UI state
        self.selected_cards = []  # Cards being dragged
        self.drag_offset = (0, 0)
        self.last_click_time = 0
        self.double_click_threshold = 500  # milliseconds
        
        # Card dimensions and positions
        self.card_width = 60
        self.card_height = 80
        self.card_spacing = 20
        self.tableau_y_offset = 20
        
        self.setup_game()
        
    def create_deck(self):
        """Create a standard 52-card deck"""
        deck = []
        for suit in range(4):
            for rank in range(1, 14):
                deck.append(Card(suit, rank))
        random.shuffle(deck)
        return deck
        
    def setup_game(self):
        """Set up initial game state"""
        deck_copy = self.deck.copy()
        
        # Deal cards to tableau
        for col in range(7):
            for row in range(col + 1):
                if deck_copy:
                    card = deck_copy.pop(0)
                    if row == col:  # Last card in column is face up
                        card.face_up = True
                    self.tableau[col].append(card)
                    
        # Remaining cards go to stock
        self.stock = deck_copy
        self.update_card_positions()
        
    def update_card_positions(self):
        """Update the screen positions of all cards"""
        # Stock pile position
        stock_x, stock_y = 20, 20
        for i, card in enumerate(self.stock):
            card.rect.x = stock_x
            card.rect.y = stock_y
            
        # Waste pile position  
        waste_x, waste_y = stock_x + self.card_width + 10, 20
        for i, card in enumerate(self.waste):
            card.rect.x = waste_x + min(i * 2, 20)  # Slight fan effect
            card.rect.y = waste_y
            
        # Foundation piles
        foundation_start_x = 320
        for pile_idx, pile in enumerate(self.foundations):
            pile_x = foundation_start_x + pile_idx * (self.card_width + 10)
            for i, card in enumerate(pile):
                card.rect.x = pile_x
                card.rect.y = 20
                
        # Tableau columns
        tableau_start_x = 20
        tableau_start_y = 120
        for col_idx, column in enumerate(self.tableau):
            col_x = tableau_start_x + col_idx * (self.card_width + 10)
            for row_idx, card in enumerate(column):
                card.rect.x = col_x
                card.rect.y = tableau_start_y + row_idx * self.tableau_y_offset
                
    def get_card_at_pos(self, pos):
        """Get the topmost card at given position"""
        # Check tableau first (reverse order to get topmost)
        for col in self.tableau:
            for card in reversed(col):
                if card.rect.collidepoint(pos) and card.face_up:
                    return card, 'tableau'
                    
        # Check waste pile
        if self.waste:
            top_waste = self.waste[-1]
            if top_waste.rect.collidepoint(pos):
                return top_waste, 'waste'
                
        # Check foundations
        for i, pile in enumerate(self.foundations):
            if pile:
                top_card = pile[-1]
                if top_card.rect.collidepoint(pos):
                    return top_card, f'foundation_{i}'
                    
        # Check stock pile
        if self.stock:
            stock_rect = pygame.Rect(20, 20, self.card_width, self.card_height)
            if stock_rect.collidepoint(pos):
                return None, 'stock'
                
        return None, None
        
    def get_movable_cards(self, card):
        """Get all cards that move with the selected card"""
        # Find which tableau column the card is in
        for col in self.tableau:
            if card in col:
                card_index = col.index(card)
                # Return this card and all cards below it
                return col[card_index:]
        return [card]  # Single card from waste or foundation
        
    def can_move_cards(self, cards, target_pos):
        """Check if cards can be moved to target position"""
        if not cards:
            return False
            
        first_card = cards[0]
        
        # Check if trying to move to foundation
        foundation_start_x = 320
        foundation_y = 20
        if (foundation_y <= target_pos[1] <= foundation_y + self.card_height):
            for i in range(4):
                pile_x = foundation_start_x + i * (self.card_width + 10)
                if (pile_x <= target_pos[0] <= pile_x + self.card_width):
                    # Only single cards can go to foundation
                    if len(cards) == 1:
                        return first_card.can_place_on_foundation(self.foundations[i])
                    return False
                    
        # Check if trying to move to tableau
        tableau_start_x = 20
        tableau_start_y = 120
        for col_idx in range(7):
            col_x = tableau_start_x + col_idx * (self.card_width + 10)
            if (col_x <= target_pos[0] <= col_x + self.card_width):
                target_column = self.tableau[col_idx]
                if not target_column:
                    # Empty column - only Kings allowed
                    return first_card.rank == 13
                else:
                    # Check if can stack on bottom card
                    bottom_card = target_column[-1]
                    return first_card.can_stack_on(bottom_card)
                    
        return False
        
    def move_cards(self, cards, target_pos):
        """Move cards to target position"""
        if not self.can_move_cards(cards, target_pos):
            return False
            
        first_card = cards[0]
        
        # Remove cards from their current location
        for col in self.tableau:
            for card in cards:
                if card in col:
                    col.remove(card)
                    
        if first_card in self.waste:
            self.waste.remove(first_card)
            
        for pile in self.foundations:
            if first_card in pile:
                pile.remove(first_card)
                
        # Add to new location
        # Check foundation
        foundation_start_x = 320
        foundation_y = 20
        if (foundation_y <= target_pos[1] <= foundation_y + self.card_height):
            for i in range(4):
                pile_x = foundation_start_x + i * (self.card_width + 10)
                if (pile_x <= target_pos[0] <= pile_x + self.card_width):
                    self.foundations[i].append(first_card)
                    break
        else:
            # Add to tableau
            tableau_start_x = 20
            for col_idx in range(7):
                col_x = tableau_start_x + col_idx * (self.card_width + 10)
                if (col_x <= target_pos[0] <= col_x + self.card_width):
                    self.tableau[col_idx].extend(cards)
                    break
                    
        # Flip top card in source tableau column if needed
        for col in self.tableau:
            if col and not col[-1].face_up:
                col[-1].face_up = True
                
        self.update_card_positions()
        return True
        
    def handle_stock_click(self):
        """Handle clicking on stock pile"""
        if self.stock:
            # Move 3 cards from stock to waste (or fewer if less available)
            cards_to_move = min(3, len(self.stock))
            for _ in range(cards_to_move):
                card = self.stock.pop()
                card.face_up = True
                self.waste.append(card)
        else:
            # Reset: move all waste cards back to stock
            while self.waste:
                card = self.waste.pop()
                card.face_up = False
                self.stock.append(card)
        self.update_card_positions()
        
    def auto_move_to_foundation(self, card):
        """Try to automatically move card to foundation"""
        for i, pile in enumerate(self.foundations):
            if card.can_place_on_foundation(pile):
                # Remove card from current location
                if card in self.waste:
                    self.waste.remove(card)
                for col in self.tableau:
                    if card in col:
                        col.remove(card)
                        if col and not col[-1].face_up:
                            col[-1].face_up = True
                            
                pile.append(card)
                self.update_card_positions()
                self.play_sound("jsfxr-drop1")
                return True
        return False
        
    def check_win(self):
        """Check if game is won"""
        return all(len(pile) == 13 for pile in self.foundations)

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            
        # Handle mouse input
        mouse_pos = pygame.mouse.get_pos()
        
        if 1 in self.game.just_mouse_down:  # Left click
            current_time = pygame.time.get_ticks()
            
            if not self.selected_cards:
                # Start drag or handle special clicks
                clicked_card, location = self.get_card_at_pos(mouse_pos)
                
                if location == 'stock':
                    self.handle_stock_click()
                elif clicked_card:
                    # Check for double-click for auto-move to foundation
                    if (current_time - self.last_click_time < self.double_click_threshold):
                        if not self.auto_move_to_foundation(clicked_card):
                            # Start drag if auto-move failed
                            self.selected_cards = self.get_movable_cards(clicked_card)
                            self.drag_offset = (mouse_pos[0] - clicked_card.rect.x,
                                              mouse_pos[1] - clicked_card.rect.y)
                    else:
                        # Single click - start drag
                        self.selected_cards = self.get_movable_cards(clicked_card)
                        self.drag_offset = (mouse_pos[0] - clicked_card.rect.x,
                                          mouse_pos[1] - clicked_card.rect.y)
                        
            self.last_click_time = current_time
            
        elif 1 in self.game.just_mouse_up:  # Left release
            if self.selected_cards:
                # Try to place the selected cards
                target_pos = (mouse_pos[0] - self.drag_offset[0],
                            mouse_pos[1] - self.drag_offset[1])
                            
                if not self.move_cards(self.selected_cards, target_pos):
                    # Move failed, return cards to original position
                    self.update_card_positions()
                else:
                    self.play_sound("jsfxr-drop1")
                    
                self.selected_cards = []
                
        # Update dragged card positions
        if self.selected_cards and pygame.mouse.get_pressed()[0]:
            base_x = mouse_pos[0] - self.drag_offset[0]
            base_y = mouse_pos[1] - self.drag_offset[1]
            for i, card in enumerate(self.selected_cards):
                card.rect.x = base_x
                card.rect.y = base_y + i * self.tableau_y_offset
                
        # Check for win condition
        if self.check_win():
            self.log("Congratulations! You won!")

    def draw(self):
        # Green felt background
        self.screen.fill((0, 100, 0))
        
        # Draw empty pile outlines
        empty_color = (0, 80, 0)
        
        # Stock pile outline
        stock_rect = pygame.Rect(20, 20, self.card_width, self.card_height)
        pygame.draw.rect(self.screen, empty_color, stock_rect, 2)
        
        # Waste pile outline
        waste_rect = pygame.Rect(90, 20, self.card_width, self.card_height)
        pygame.draw.rect(self.screen, empty_color, waste_rect, 2)
        
        # Foundation pile outlines
        for i in range(4):
            foundation_rect = pygame.Rect(320 + i * 70, 20, self.card_width, self.card_height)
            pygame.draw.rect(self.screen, empty_color, foundation_rect, 2)
            
        # Tableau column outlines
        for i in range(7):
            tableau_rect = pygame.Rect(20 + i * 70, 120, self.card_width, self.card_height)
            pygame.draw.rect(self.screen, empty_color, tableau_rect, 2)
        
        # Draw all cards
        all_cards = []
        
        # Add stock cards (only show back of top card)
        if self.stock:
            all_cards.append(self.stock[-1])
            
        # Add waste cards
        all_cards.extend(self.waste)
        
        # Add foundation cards
        for pile in self.foundations:
            all_cards.extend(pile)
            
        # Add tableau cards
        for column in self.tableau:
            all_cards.extend(column)
            
        # Sort by y position to draw in correct order
        all_cards.sort(key=lambda c: c.rect.y)
        
        # Draw each card
        for card in all_cards:
            if card in self.selected_cards:
                continue  # Draw selected cards last
                
            self.draw_card(card)
            
        # Draw selected cards on top
        for card in self.selected_cards:
            self.draw_card(card)
            
        # Draw win message
        if self.check_win():
            win_text = self.standard_text("YOU WIN!")
            self.blit_centered(win_text, self.screen, (0.5, 0.9))
            
    def draw_card(self, card):
        """Draw a single card"""
        if card.face_up:
            # Face up - white card with rank and suit
            color = (220, 220, 220) if card.is_red() else (240, 240, 240)
            pygame.draw.rect(self.screen, color, card.rect)
            pygame.draw.rect(self.screen, (0, 0, 0), card.rect, 2)
            
            # Draw rank and suit
            text_color = (200, 0, 0) if card.is_red() else (0, 0, 0)
            rank_text = self.make_text(
                card.get_rank_name() + card.get_suit_symbol(),
                text_color, 12
            )
            
            self.screen.blit(rank_text, (card.rect.x + 5, card.rect.y + 5))
            
        else:
            # Face down - blue back
            pygame.draw.rect(self.screen, (0, 0, 150), card.rect)
            pygame.draw.rect(self.screen, (0, 0, 0), card.rect, 2)
            
            # Draw pattern
            center_x = card.rect.centerx
            center_y = card.rect.centery
            pygame.draw.circle(self.screen, (100, 100, 200), (center_x, center_y), 15, 2)
