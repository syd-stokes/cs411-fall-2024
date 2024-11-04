import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 20.00, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 25.00, 'MED')

@pytest.fixture
def sample_meal(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Battle Management Test Cases
##################################################

def test_battle_with_two_meals(battle_model, sample_meals, mock_update_meal_stats, mocker):
    """Test a successful battle between two meals."""
    # Assign sample meals to combatants
    battle_model.combatants = sample_meals
    
    # Mock `get_battle_score` to provide predictable scores
    mocker.patch.object(battle_model, 'get_battle_score', side_effect=[75, 70])
    
    # Mock `get_random` to return a controlled value
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.1)
    
    winner = battle_model.battle()

    # Ensure battle completed and returned the correct winner
    assert winner in [sample_meals[0].meal, sample_meals[1].meal]

    # Verify `update_meal_stats` calls for win/loss
    mock_update_meal_stats.assert_any_call(sample_meals[0].id, 'win')
    mock_update_meal_stats.assert_any_call(sample_meals[1].id, 'loss')

    # Confirm the loser was removed from the combatants list
    remaining_combatant = battle_model.combatants[0]
    assert len(battle_model.combatants) == 1
    assert remaining_combatant.meal == winner

def test_battle_with_insufficient_combatants(battle_model):
    """Test error when only one combatant tries to battle."""
    # Only one combatant in the list
    battle_model.combatants = [Meal(1, 'Single Meal', 'Cuisine', 10.00, 'LOW')]
    
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle_random_number_influence(battle_model, sample_meals, mocker):
    """Test how random number and score delta influence the battle outcome."""
    # Assign sample meals to combatants
    battle_model.combatants = sample_meals
    
    # Case where delta is greater than the random number (combatant 1 wins)
    mocker.patch.object(battle_model, 'get_battle_score', side_effect=[90, 80])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.1)

    winner = battle_model.battle()
    assert winner == sample_meals[0].meal
    
    # Reset combatants for the next test case
    battle_model.combatants = sample_meals

    # Case where delta is less than the random number (combatant 2 wins)
    mocker.patch.object(battle_model, 'get_battle_score', side_effect=[80, 90])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.5)

    winner = battle_model.battle()
    assert winner == sample_meals[1].meal


##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test successfully retrieving the battle score from the given meal combatant."""
    retrieved_score = battle_model.get_battle_score(sample_meal1)
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - 3
    assert retrieved_score == expected_score, f"Expected score of {expected_score}, got {retrieved_score}"



##################################################
# Combatant Management Functions
##################################################

def test_clear_singular_combatant(battle_model, sample_meal1):
    """Test clearing the combatants list of len 1."""
    battle_model.combatants = [sample_meal1]

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_multiple_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing the entire combatants list of len > 1."""
    battle_model.combatants = [sample_meal1, sample_meal2]

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_clear_empty_combatant(battle_model):
    """Test clearing the empty combatants list of len = 0."""
    battle_model.combatants = []

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants list should be empty after clearing"

def test_get_all_combatants_multiple(battle_model, sample_meal1, sample_meal2):
    """Test successfully retrieving all combatants from the list."""
    battle_model.combatants = [sample_meal1, sample_meal2]

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_get_all_combatants_singular(battle_model, sample_meal1):
    """Test successfully retrieving all combatants from the list of len 1."""
    battle_model.combatants = [sample_meal1]

    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 1
    assert all_combatants[0].id == 1

def test_prep_two_combatants(battle_model, sample_meal1, sample_meal2):
    """Test successfully prepping all combatants from the list of len 2."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants == [sample_meal1, sample_meal2]

def test_prep_one_combatant(battle_model, sample_meal1):
    """Test successfully prepping one combatant."""
    battle_model.prep_combatant(sample_meal1)
    
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants == [sample_meal1]

def test_prep_three_combatants(battle_model, sample_meal1, sample_meal2):
    """Test error when trying to prep and add a third combatant."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    assert len(battle_model.combatants) == 2, "There should be exactly two combatants prepped."
    assert battle_model.combatants == [sample_meal1, sample_meal2], "Combatants list does not match expected entries."
    
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(Meal(3, 'Meal 3', 'Cuisine 3', 15.00, 'HIGH'))