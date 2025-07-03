import os
import json
import random
import string

ADJECTIVES = [
    "happy",
    "quick",
    "bright",
    "clever",
    "mighty",
    "silent",
    "shiny",
    "brave",
    "gentle",
    "silly",
    "ephemeral",
    "winsome",
    "loquacious",
    "sedulous",
    "perfervid",
    "ebullient",
    "serendipitous",
    "lugubrious",
    "tenacious",
    "verdant",
    "amicable",
    "halcyon",
    "incandescent",
    "mellifluous",
    "wistful",
    "refractory",
    "obdurate",
    "pulchritudinous",
    "quixotic",
    "sagacious",
]

ANIMALS = [
    "turtle",
    "fox",
    "lion",
    "eagle",
    "panda",
    "wolf",
    "cat",
    "dog",
    "bear",
    "otter",
    "pangolin",
    "axolotl",
    "quokka",
    "okapi",
    "capybara",
    "narwhal",
    "echidna",
    "binturong",
    "kiwi",
    "aye-aye",
    "manatee",
    "quetzal",
    "fossa",
    "tuatara",
    "weta",
    "kakapo",
    "solenodon",
    "bandicoot",
    "jerboa",
    "caracal",
]

NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Oscar",
    "Peggy",
    "Sybil",
    "Taro",
    "Ayumi",
    "Sven",
    "Indira",
    "Kiara",
    "Lionel",
    "Mei",
    "Nikhil",
    "Chandra",
    "Soren",
    "Aisha",
    "Lorenzo",
    "Freya",
    "Hugo",
    "Camille",
    "Darius",
    "Elara",
    "Finnian",
    "Giselle",
    "Hector",
    "Imani",
    "Jiro",
    "Kiana",
    "Leif",
    "Marisol",
    "Nolan",
    "Ophelia",
    "Quinlan",
]

MATH_LAST = [
    "Gauss",
    "Euler",
    "Abel",
    "Noether",
    "Riemann",
    "Hilbert",
    "Cauchy",
    "Godel",
    "Hardy",
    "Taylor",
    "Lagrange",
    "Pascal",
    "Descartes",
    "Turing",
    "Cantor",
    "Bernoulli",
    "Fermat",
    "Leibniz",
    "Kronecker",
    "Poincare",
    "Weyl",
    "Borel",
    "Zariski",
    "Grothendieck",
    "VonNeumann",
    "Burnside",
    "Bessel",
    "Peano",
    "Kolmogorov",
    "Erdos",
]

VERBS = [
    "Solves",
    "Integrates",
    "Adds",
    "Subtracts",
    "Multiplies",
    "Divides",
    "Calculates",
    "Proves",
    "Graphs",
    "Analyzes",
    "Derives",
    "Evaluates",
    "Simplifies",
    "Models",
    "Transforms",
    "Approximates",
    "Differentiates",
    "Optimizes",
    "Estimates",
    "Deciphers",
    "Interpolates",
    "Extrapolates",
    "Predicts",
    "Validates",
    "Simulates",
    "Normalizes",
    "Parametrizes",
    "Factorizes",
    "Classifies",
    "Explores",
]


ALPHANUM = string.ascii_letters + string.digits


def maybe_cap(word: str) -> str:
    return word.capitalize() if random.random() < 0.5 else word.lower()


def gen_username() -> str:
    r = random.random()
    if r < 0.4:
        adj = maybe_cap(random.choice(ADJECTIVES))
        animal = maybe_cap(random.choice(ANIMALS))
        return adj + animal
    elif r < 0.8:
        name = maybe_cap(random.choice(NAMES))
        extra = "".join(random.choices(ALPHANUM, k=random.randint(0, 5)))
        return name + extra
    else:
        prefix = "".join(random.choices(ALPHANUM, k=random.randint(0, 3)))
        last = maybe_cap(random.choice(MATH_LAST))
        verb = maybe_cap(random.choice(VERBS))
        return prefix + last + verb


def parse_source(problem_id: str) -> str:
    try:
        _year, contest, _num = problem_id.split("-", 2)
    except ValueError:
        return ""
    contest_upper = contest.upper()
    contest_clean = contest_upper.replace(" ", "")
    if contest_upper.startswith("AIME"):
        return "AIME"
    if contest_upper == "AHSME":
        return "AHSME"
    if contest_upper == "8":
        return "AMC8"
    if contest_clean.startswith("10"):
        return "AMC10"
    return "AMC12"


def update_file(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for item in data:
        source = parse_source(item.get("ID", ""))
        if item.get("Source") != source:
            item["Source"] = source
            changed = True
        item["Provider"] = gen_username()
        changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    bases = [d for d in os.listdir(".") if d.endswith("_problems") and os.path.isdir(d)]
    for base in bases:
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".json"):
                    print(f"Updating {os.path.join(root, name)}")
                    update_file(os.path.join(root, name))


if __name__ == "__main__":
    main()
