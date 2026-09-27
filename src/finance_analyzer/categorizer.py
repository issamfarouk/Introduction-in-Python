"""Guess the category of a transaction from its description."""

from finance_analyzer.transaction import Transaction

# Category -> words that appear in the description (lowercase, English and German)
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Income": ["salary", "gehalt", "lohn"],
    "Housing": ["rent", "miete", "strom", "stadtwerke"],
    "Groceries": ["lidl", "rewe", "aldi", "edeka", "netto", "kaufland", "penny"],
    "Eating out": ["starbucks", "pizza", "mcdonald", "burger", "restaurant", "cafe"],
    "Subscriptions": [
        "netflix",
        "spotify",
        "disney",
        "fitx",
        "gym",
        "vodafone",
        "telekom",
    ],
    "Transport": ["deutschlandticket", "bahn", "db vertrieb", "uber", "tank"],
    "Shopping": ["amazon", "zalando", "ikea", "mediamarkt"],
    "Health & Care": ["dm drogerie", "rossmann", "apotheke"],
}

UNCATEGORIZED = "Uncategorized"


def categorize(description: str, amount: float) -> str:
    """Return the category for one transaction."""
    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category

    # No keyword matched: at least tell money in from money out
    match amount:
        case a if a > 0:
            return "Other income"
        case _:
            return "Other"


def categorize_all(transactions: list[Transaction]) -> None:
    """Fill in the category of every transaction that does not have one yet."""
    for t in transactions:
        if t.category == UNCATEGORIZED:
            t.category = categorize(t.description, t.amount)
