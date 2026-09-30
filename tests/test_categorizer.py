from finance_analyzer import categorize


def test_known_shops():
    assert categorize("Lidl", -20.0) == "Groceries"
    assert categorize("REWE Markt", -40.0) == "Groceries"
    assert categorize("Miete", -750.0) == "Housing"
    assert categorize("Netflix", -12.99) == "Subscriptions"


def test_housing_insurance_and_fees():
    assert categorize("Studierendenwerk Dortmund", -420.0) == "Housing"
    assert categorize("Techniker Krankenkasse", -146.0) == "Insurance"
    assert categorize("Rundfunk ARD, ZDF, DRadio", -55.0) == "Fees & Taxes"


def test_transfers():
    assert categorize("Transfer to a friend", -40.0) == "Transfers"
    assert categorize("Wise", -200.0) == "Transfers"
    assert categorize("Apple Pay top-up by *1234", 500.0) == "Transfers"


def test_keyword_only_at_start_of_word():
    # "rent" must not be found inside "Parent" or "Current"
    assert categorize("Parent meeting", -5.0) == "Other"
    assert categorize("Current account", -5.0) == "Other"
    # "markt" must not be found inside "Mediamarkt"
    assert categorize("Mediamarkt", -300.0) == "Shopping"


def test_money_going_out_is_never_income():
    assert categorize("Gehaltszahlung", 2000.0) == "Income"
    assert categorize("Lohnsteuer", -300.0) == "Other"


def test_unknown_description():
    assert categorize("Something new", -5.0) == "Other"
    assert categorize("Something new", 10.0) == "Other income"
