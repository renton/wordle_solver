import sys
from collections import defaultdict
from math import log2

# load all words from `words.txt` and filter out all solutions from `solutions.txt`
def load_words(filename="words.txt", used_filename="solutions.txt"):
    with open(filename) as f:
        word_list = [w.strip().lower() for w in f if len(w.strip()) == 5 and w.strip().isalpha()]
    try:
        with open(used_filename) as f:
            used_words = set(w.strip().lower() for w in f if len(w.strip()) == 5)
        word_list = [w for w in word_list if w not in used_words]
    except FileNotFoundError:
        print("Warning: solutions.txt not found. Skipping used-word filtering.")
    return word_list

def get_feedback(guess, answer):
    feedback = ['b'] * 5
    answer_chars = list(answer)

    # First pass: greens
    for i in range(5):
        if guess[i] == answer[i]:
            feedback[i] = 'g'
            answer_chars[i] = None

    # Second pass: yellows
    for i in range(5):
        if feedback[i] == 'b' and guess[i] in answer_chars:
            feedback[i] = 'y'
            answer_chars[answer_chars.index(guess[i])] = None

    return ''.join(feedback)


def print_feedback(guess, feedback):
    symbols = {'g': '🟩', 'y': '🟨', 'b': '⬛'}
    print(f"{guess.upper()}  {''.join(symbols[c] for c in feedback)}")

def filter_words(possible_words, guess, feedback):
    return [word for word in possible_words if get_feedback(guess, word) == feedback]

def entropy_score(guess, possible_words):
    pattern_counts = defaultdict(int)
    for actual in possible_words:
        pattern = get_feedback(guess, actual)
        pattern_counts[pattern] += 1

    total = len(possible_words)
    # we want to choose words which partition and distribute counts into as many patterns as possible
    entropy = 0
    for pattern, count in pattern_counts.items():
        p = count / total
        entropy -= p * log2(p)
    return entropy

def suggest_best_guess(possible_words, all_words):
    scored = []
    total = len(all_words)

    for idx, word in enumerate(all_words, 1):
        score = entropy_score(word, possible_words)
        scored.append((word, score))

        # Print progress bar
        percent = idx / total
        bar_len = 30
        filled_len = int(bar_len * percent)
        bar = '█' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write(f"\rScoring guesses: |{bar}| {percent:.0%} ({idx}/{total})")
        sys.stdout.flush()

    print()  # newline after progress bar completes

    # Prefer guesses from the solution list if scores are close
    scored.sort(key=lambda x: (-x[1], x[0] not in possible_words))

    return scored[0][0], scored[:min(20, len(scored))]

def main():
    all_words = load_words("words.txt")
    possible_words = all_words[:]

    round_num = 1
    while True:
        print(f"\nRound {round_num}")
        print(f"{len(possible_words)} possible words remaining.")

        guess, ranked = suggest_best_guess(possible_words, all_words)
        for i, (word, score) in enumerate(ranked):
            print(f"{i} {word} {score:.3f}")

        print(f"Suggested next guess: {guess.upper()}")

        user_guess = input("Enter your guess: ").strip().lower()
        result = input("Enter result (g=green, y=yellow, b=black): ").strip().lower()
        print_feedback(user_guess, result)

        if result == "ggggg":
            print("Solved!")
            break

        possible_words = filter_words(possible_words, user_guess, result)

        if not possible_words:
            print("No words remaining. Something went wrong.")
            break

        round_num += 1


if __name__ == "__main__":
    main()
