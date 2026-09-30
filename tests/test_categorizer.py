from finance_analyzer import categorize


def test_known_shops():
    assert categorize("Lidl", -20.0) == "Groceries"
    assert categorize("REWE Markt", -40.0) == "Groceries"
    assert categorize("Miete", -750.0) == "Housing"
    assert categorize("Netflix", -12.99) == "Subscriptions"


def test_keyword_only_at_start_of_word():
    assert categorize("Current account fee", -5.0) == "Other"


def test_money_going_out_is_never_income():
    assert categorize("Gehaltszahlung", 2000.0) == "Income"
    assert categorize("Lohnsteuer", -300.0) == "Other"


def test_unknown_description():
    assert categorize("Something new", -5.0) == "Other"
    assert categorize("Something new", 10.0) == "Other income"
