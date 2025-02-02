import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python_files')))

import pytest
import json
from python_files.deck import Card, Deck
from python_files.player import Player, Bot, Dealer, BettingRound
from python_files.poker_rules import PokerRules
from python_files.game import TurnManager, Game
from flask import Flask, request
from texas_hold_em_poker import app, handle_post_request, new_game, start_game, advance_turn

@pytest.fixture
def sample_deck():
    return Deck("deck.json")

@pytest.fixture
def sample_player():
    return Player("Giocatore")

@pytest.fixture
def sample_bot():
    return Bot("Bot1")

@pytest.fixture
def sample_dealer():
    return Dealer("Dealer")

@pytest.fixture
def sample_poker_rules():
    return PokerRules()

@pytest.fixture
def sample_game():
    return Game(num_players=4)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_card_creation():
    card = Card("Hearts", "A")
    assert card.suit == "Hearts"
    assert card.value == "A"
    assert repr(card) == "A Hearts"

def test_deck_loading(sample_deck):
    assert len(sample_deck.deck_data) > 0

def test_deck_shuffling(sample_deck):
    original_deck = sample_deck.deck_data.copy()
    sample_deck.shuffle()
    assert sample_deck.deck_data != original_deck

def test_draw_card(sample_deck):
    initial_size = len(sample_deck.deck_data)
    card = sample_deck.draw_card()
    assert card is not None
    assert len(sample_deck.deck_data) == initial_size - 1

def test_player_creation(sample_player):
    assert sample_player.name == "Giocatore"
    assert sample_player.chips == 1000000000

def test_add_remove_card(sample_player):
    card = Card("Hearts", "A")
    sample_player.add_card(card)
    assert sample_player.has_card(card) == True
    sample_player.remove_card(card)
    assert sample_player.has_card(card) == False

def test_bot_decision(sample_bot):
    game_state = {
        'community_cards': [Card("Hearts", "2"), Card("Clubs", "5"), Card("Diamonds", "10")],
        'current_bet': 100,
        'pot': 500,
        'players': [sample_bot]
    }
    decision = sample_bot.make_decision(game_state, BettingRound.PRE_FLOP)
    assert decision in ['fold', 'call', 'raise']

def test_poker_hand_ranking(sample_poker_rules):
    hand = [Card("Hearts", "10"), Card("Hearts", "J"), Card("Hearts", "Q"), Card("Hearts", "K"), Card("Hearts", "A")]
    assert sample_poker_rules.royal_flush(hand) == True

def test_turn_manager():
    players = [Player('small_blind'), Player('big_blind'), Player('player1'), Player('player2')]
    turn_manager = TurnManager(players)
    assert turn_manager.current_turn == 2

def test_game_creation(sample_game):
    assert len(sample_game.players) == 4
    assert sample_game.phase == Game.PRE_FLOP

def test_game_setup(sample_game):
    sample_game.setup_players()
    assert len(sample_game.players[0].cards) == 2
    assert sample_game.pot == sample_game.small_blind + sample_game.big_blind

def test_game_phases(sample_game):
    sample_game.setup_players()
    sample_game.move_to_flop()
    assert len(sample_game.community_cards) == 3
    sample_game.move_to_turn()
    assert len(sample_game.community_cards) == 4
    sample_game.move_to_river()
    assert len(sample_game.community_cards) == 5

# Flask app tests
def test_new_game(client):
    response = client.post('/new-game')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'player_hand' in data
    assert 'community_cards' in data

def test_start_game(client):
    response = client.post('/start-game')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'player_hand' in data
    assert 'community_cards' in data

def test_advance_turn(client):
    response = client.post('/advance-turn')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'player_hand' in data
    assert 'community_cards' in data

def test_handle_post_request(client):
    response = client.post('/', data={'action': 'bet', 'betAmount': '10'})
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'player_hand' in data
    assert 'community_cards' in data
    assert 'message' in data

import sys
import pytest

if __name__ == "__main__":
    result = pytest.main(['-v', __file__])
    if result != 0:
        sys.exit(result)