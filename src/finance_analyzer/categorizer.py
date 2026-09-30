"""Guess the category of a transaction from its description."""

from finance_analyzer.transaction import Transaction

# Category -> words that appear in the description (lowercase, English and German)
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Income": ["salary", "gehalt", "lohn"],
    "Housing": [
        "rent",
        "miete",
        "strom",
        "stadtwerke",
        "studierendenwerk",
        "wohnheim",
        "nebenkosten",
    ],
    "Insurance": ["krankenkasse", "versicherung"],
    "Groceries": [
        "lidl",
        "rewe",
        "aldi",
        "edeka",
        "netto",
        "kaufland",
        "penny",
        "markt",
        "market",
        "supermarkt",
        "metzgerei",
    ],
    "Eating out": [
        "starbucks",
        "pizza",
        "mcdonald",
        "burger",
        "restaurant",
        "cafe",
        "wolt",
        "lieferando",
        "kebab",
        "bäckerei",
    ],
    "Subscriptions": [
        "netflix",
        "spotify",
        "disney",
        "fitx",
        "gym",
        "vodafone",
        "telekom",
    ],
    "Transport": [
        "deutschlandticket",
        "bahn",
        "uber",
        "tank",
        "bolt",
        "lime",
        "flixbus",
    ],
    "Shopping": [
        "amazon",
        "zalando",
        "ikea",
        "mediamarkt",
        "saturn",
        "action",
        "woolworth",
        "tedi",
        "primark",
    ],
    "Health & Care": ["drogerie", "rossmann", "apotheke"],
    "Fees & Taxes": ["rundfunk", "fee", "gebühr", "steuer"],
    "Transfers": ["transfer", "überweisung", "top-up", "wise", "paypal", "western"],
}

UNCATEGORIZED = "Uncategorized"


def categorize(description: str, amount: float) -> str:
    """Return the category for one transaction.

    Keywords only match at the start of a word, not in the middle of one.
    """
    words = description.lower().split()
    for category, keywords in CATEGORY_KEYWORDS.items():
        # Money going out can't be income
        if category == "Income" and amount <= 0:
            continue
        for keyword in keywords:
            if any(word.startswith(keyword) for word in words):
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
