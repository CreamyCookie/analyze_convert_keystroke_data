import csv
import gzip
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Iterable

from utils.pattern import AlternatingPatternMatcher
from utils.constants import TrainingDataColId, TIME_I, IS_DOWN_I, KEY_I, MAIN_AREA_KEYS, MOD_KEYS
from utils.training_data import TrainingData
from utils.format import pct_row, pct, print_table, pct2_row, trim_trailing_zero, print_h1, print_h2, print_h3, print_h4
from utils.serialization import TabMinDialect, read_from_csv_gz

DATASET_PATH = Path(__file__).parent / 'dataset'

LOG_PATH = DATASET_PATH / 'filtered_events.csv.gz'
TRAIN_PATH = DATASET_PATH / f'training_data.csv.gz'

PRINT_INDIVIDUAL = False
DURATION_NUM_FMT = '_.0f'

NON_MOD_VALUE = False
MOD_VALUE = True

KEYS_PERCENTAGE_BELOW = 0.99

# does not include removals from key being pressed down consecutively
event_after_this_one_was_removed = set()


def print_stats(durations, fmt=DURATION_NUM_FMT):
    if not durations:
        print("was empty\n")
        return

    sorted_durations = sorted(durations)
    most_below = perc_below(sorted_durations)

    num_below = trim_trailing_zero(KEYS_PERCENTAGE_BELOW * 100)

    print_table([
        ['min', 'max', 'avg', 'median', f'{num_below}% below'],
        None,
        [
            f"{min(durations):{fmt}}",
            f"{max(durations):{fmt}}",
            f"{mean(durations):{fmt}}",
            f"{median(durations):{fmt}}",
            f"{most_below:{fmt}}",
        ]
    ])
    print()


def perc_below(sorted_durations):
    i = len(sorted_durations) * KEYS_PERCENTAGE_BELOW
    rem = i - int(i)
    j = int(i) + 1
    if j >= len(sorted_durations):
        j = len(sorted_durations) - 1
    most_below = sorted_durations[int(i)] * (1 - rem) + sorted_durations[j] * rem
    return most_below


def print_intersection_stats(intersections, kind):
    all_overlap_durations = []
    all_overlap_percentages = []
    all_durations_between_both_pressed = []

    space_with_others_overlap_durations = []
    space_duration_between_both_presses = []

    for keys, overlap_data in intersections.items():
        overlap_durations = []
        overlap_percentages = []
        durations_between_both_presses = []
        for (overlap_duration, overlap_percentage, duration_between_both_pressed) in overlap_data:
            overlap_durations.append(overlap_duration)
            if overlap_percentage >= 0:
                overlap_percentages.append(overlap_percentage)
            durations_between_both_presses.append(duration_between_both_pressed)

        if PRINT_INDIVIDUAL:
            print_h3(f"{keys[0]} with {keys[1]}")
            print_h4("Overlap duration")
            print_stats(overlap_durations)
        all_overlap_durations.extend(overlap_durations)

        if PRINT_INDIVIDUAL:
            print_h4("Overlap percentages")
            print_stats(overlap_percentages, fmt='_.2%')
        all_overlap_percentages.extend(overlap_percentages)

        if PRINT_INDIVIDUAL:
            print_h4("Duration between both presses")
            print_stats(durations_between_both_presses)
        all_durations_between_both_pressed.extend(durations_between_both_presses)

        if keys[0] == "space":
            space_with_others_overlap_durations.extend(overlap_durations)
            space_duration_between_both_presses.extend(durations_between_both_presses)

    print_h3("Space THEN others")
    print_h4("Overlap duration")
    print_stats(space_with_others_overlap_durations)

    print_h4("Duration between both presses")
    print_stats(space_duration_between_both_presses)

    print_h3(f"All {kind}")
    print_h4("Overlap duration")
    print_stats(all_overlap_durations)

    print_h4("Overlap percentages")
    print_stats(all_overlap_percentages)

    print_h4("Duration between both presses")
    print_stats(all_durations_between_both_pressed)


def load_events(path: Path):
    return read_from_csv_gz(path, map_keys_and_remove_pause_marker)


def map_keys_and_remove_pause_marker(
        rows: Iterable[tuple[str, str, str]]
) -> list[tuple[int, bool, str]]:
    result = []
    prev_row = None

    for timestamp, is_down, key in rows:
        if key == '':
            event_after_this_one_was_removed.add(prev_row)
            continue

        timestamp = int(timestamp)
        is_down = is_down == '1'

        if key is None:
            # the , is likely incorrect, but we don't know the actual
            # values because it was before the pynput vk change
            # (from now on we will get an int instead of None instead)
            key = ","
        else:
            if isinstance(key, int):
                print("don't know what this is (skipping):", key, timestamp)
                event_after_this_one_was_removed.add(prev_row)
                continue

            # this can boost performance by making string comparisons O(1) as only the identity is compared
            # it also saves memory by not repeating same strings in memory
            key = sys.intern(key.lower())

        row = (timestamp, is_down, key)
        result.append(row)
        prev_row = row

    return result


def p_rows(counter: Counter, postfix=""):
    total = counter.total()
    if not postfix.startswith(" "):
        postfix = " " + postfix
    return [
        pct_row("non-mod" + postfix, counter[NON_MOD_VALUE], total),
        pct_row("mod" + postfix, counter[MOD_VALUE], total),
        ["total" + postfix, total],
    ]


def p_multi_rows(counter: Counter, interfix: str):
    total = counter.total()
    return [
        pct_row("non-mod " + interfix + " non-mod", counter[(NON_MOD_VALUE, NON_MOD_VALUE)], total),
        pct_row("non-mod " + interfix + " mod", counter[(NON_MOD_VALUE, MOD_VALUE)], total),
        pct_row("mod " + interfix + " non-mod", counter[(MOD_VALUE, NON_MOD_VALUE)], total),
        pct_row("mod " + interfix + " mod", counter[(MOD_VALUE, MOD_VALUE)], total),
        ["total " + interfix, total],
    ]


def count_any_first(counter: Counter, first_key):
    return counter[(first_key, NON_MOD_VALUE)] + counter[(first_key, MOD_VALUE)]


def count_any_second(counter: Counter, second_key):
    return counter[(NON_MOD_VALUE, second_key)] + counter[(MOD_VALUE, second_key)]


def count_any(key, *multiple_counter):
    result = 0
    for counter in multiple_counter:
        for keys, count in counter.items():
            if key in keys:
                result += count
    return result


def p_variations(key):
    opposite_key = not key
    opposite_name = "mod" if opposite_key else "non-mod"

    # will be different from the version from total_counts, because wrap and overlap have two
    # elements, and so will be counted multiple times here
    total = zero_overlap_counts[key] + count_any(key, overlap_counts, wrap_counts)
    return [
        ['type', '%'],
        None,
        ["no overlap/wrap", pct(zero_overlap_counts[key], total)],
        [],
        ["any overlap", pct(count_any(key, overlap_counts), total)],
        ["- overlaps non-mod", pct(overlap_counts[(key, NON_MOD_VALUE)], total)],
        ["- overlaps mod", pct(overlap_counts[(key, MOD_VALUE)], total)],
        ["- overlapped by " + opposite_name, pct(overlap_counts[(opposite_key, key)], total)],
        [],
        ["any wrap", pct(count_any(key, wrap_counts), total)],
        ["- wraps non-mod", pct(wrap_counts[(key, NON_MOD_VALUE)], total)],
        ["- wraps mod", pct(wrap_counts[(key, MOD_VALUE)], total)],
        ["- wrapped by " + opposite_name, pct(wrap_counts[(opposite_key, key)], total)],
    ]


def print_counter_as_table(counter, header, n_most_common):
    l = [header, None]
    for k, v in counter.most_common(n_most_common):
        l.append([k, v])
    print_table(l)


def collect_training_data(events, mod_counter: Counter):
    result = TrainingData([])

    # a = some key we don't care about that is down before p (to not exclude overlaps with p)
    # p = previous, x = tap (or) hold key, n = next key (after tap hold)
    # z = after x and n, another key will be pressed
    pattern = 'ApAPAxPnzXzNzXz'

    # make sure this is consistent with TrainingDataColId and InputTrainCol
    order = 'pPxnNXz'

    matcher = AlternatingPatternMatcher(pattern, down_index=IS_DOWN_I, key_index=KEY_I)
    for match in matcher.all_matches(events, continue_at_letter='x'):
        th_down = events[match['x']]

        is_mod = th_down[KEY_I] in MOD_KEYS
        is_next_main = events[match['n']][KEY_I] in MAIN_AREA_KEYS
        if is_mod and not is_next_main:
            continue

        next_up = events[match['N']]

        if (next_up[TIME_I] - th_down[TIME_I]) > 9000:
            continue

        last = max(match.values())
        all_but_last = (events[j] for j in match.values() if j != last)
        if any(e in event_after_this_one_was_removed for e in all_but_last):
            continue

        prev = events[match['p']]
        prev_is_mod = prev[KEY_I] in MOD_KEYS

        r = [events[match[o]][TIME_I] for o in order]
        r.append(prev_is_mod)
        r.append(is_mod)
        result.elements.append(tuple(r))

        is_triple_down = match['n'] + 1 == match['z']
        is_wrapped = match['N'] < match['X']
        result.add_count(is_mod, is_wrapped, is_triple_down)
        if is_mod:
            mod_counter[th_down[KEY_I]] += 1

    return result


def find_prev_event(events, start_index, key_to_find, key_to_find_down, max_search_window=7):
    for i in range(start_index, max(0, start_index - max_search_window), -1):
        if events[i][KEY_I] == key_to_find:
            if events[i][IS_DOWN_I] == key_to_find_down:
                return events[i]
            else:
                # we are assuming that we don't want the key we're looking for in the opposite state
                break


def write_csv_of_training_data(training_data: TrainingData):
    with gzip.open(str(TRAIN_PATH), 'wt', newline='', encoding='utf-8') as gz_file:
        writer = csv.writer(gz_file, dialect=TabMinDialect)

        writer.writerow(TrainingDataColId.member_names)
        for el in training_data.elements:
            # The last element is a boolean, so make it an int.
            writer.writerow((col.to_csv(el[col.value]) for col in TrainingDataColId))

    print(f'Written training data to {TRAIN_PATH}')


if __name__ == '__main__':
    print('All durations are milliseconds.')
    print()
    print(f'Loading events from {LOG_PATH.name}')
    events = load_events(LOG_PATH)
    print(f"Loaded {len(events):_} events")

    key_durations = {}
    zero_overlap_durations = {MOD_VALUE: [], NON_MOD_VALUE: []}
    mod_intersections = {}
    non_mod_intersections = {}
    down = {}

    duration_between_previous_release_and_this_press = {}
    last_release_key = None
    last_release_timestamp = None

    total_counts = Counter()
    zero_overlap_counts = Counter()

    overlap_counts = Counter()
    wrap_counts = Counter()  # e.g. Shift down, A down, A up, Shift up

    mods_simultaneous_counts = Counter()
    simultaneous_counts = Counter()
    key_counts = Counter()
    mods_down = set()

    wrapped_durations_press_and_next_press = []

    for i, (timestamp, is_pressed, key) in enumerate(events):
        if is_pressed:
            if key in down:
                raise ValueError(f'event {i}: key {key} pressed at {timestamp} but already down - down: {down}')

            down[key] = timestamp
            total_counts[key in MOD_KEYS] += 1

            key_counts[key] += 1
            if key in MOD_KEYS:
                mods_down.add(key)
            elif (len(down) > 2 or 'shift' not in down) and not down.keys().isdisjoint(MOD_KEYS):
                # mods are pressed right now, but this is not one
                # ignoring mods only overlapping mods here (same for non-mods)
                simultaneous_counts[" ".join(down.keys())] += 1
        else:
            # Key is released
            when_down = down.get(key)
            if when_down is None:
                raise ValueError(f'event {i}: key {key} released at {timestamp} but not pressed - down: {down}')

            del down[key]
            if key in mods_down:
                if len(mods_down) > 1:
                    mods_simultaneous_counts[" ".join(sorted(mods_down))] += 1
                mods_down.remove(key)

            released_at = timestamp
            dur = released_at - when_down

            if last_release_key is not None:
                between_dur = when_down - last_release_timestamp
                # negative value mean that the previous key was released after this one was pressed down
                if 0 <= between_dur < 1500:
                    duration_between_previous_release_and_this_press.setdefault(key, []).append(between_dur)
            last_release_key = key
            last_release_timestamp = timestamp

            key_durations.setdefault(key, []).append(dur)
            is_mod = key in MOD_KEYS

            if not down and events[i - 1][KEY_I] == key and events[i - 1][IS_DOWN_I]:
                zero_overlap_counts[is_mod] += 1
                zero_overlap_durations[is_mod].append(dur)

            for other_key, other_when_down in down.items():
                other_is_mod = other_key in MOD_KEYS

                if other_when_down < when_down:
                    # the other key was down before this one, and it isn't released yet,
                    # so it completely wraps this one (e.g. Shift down, A down, A up, Shift up)
                    overlap_duration = dur
                    intersect_key = (other_key, key)

                    wrap_counts[(other_is_mod, is_mod)] += 1
                    wrapped_durations_press_and_next_press.append(
                        other_when_down - when_down)
                else:
                    # the other key was down after this one (e.g. Shift down, A down, Shift up, A up)
                    # Since this key (Shift in the example) will already be up, when the other key (A)
                    # is up, it would not be registered, if we only consider if the other key is mod
                    overlap_duration = released_at - other_when_down
                    intersect_key = (key, other_key)

                    overlap_counts[(is_mod, other_is_mod)] += 1

                overlap_percentage = -1
                if dur == 0:
                    print(f'{key} from {when_down} to {released_at} was pressed for 0 ms')
                else:
                    # the duration the just-now-released key is held down with a not-yet-released key
                    # divided by the total duration this key was held down
                    overlap_percentage = overlap_duration / dur

                duration_between_both_pressed = abs(other_when_down - when_down)

                intersections = mod_intersections if is_mod or other_is_mod else non_mod_intersections
                intersections.setdefault(intersect_key, []).append(
                    (overlap_duration, overlap_percentage, duration_between_both_pressed))

    if down:
        print(f"Somehow pressed_keys is not empty: {down}")
    print()
    print()

    print_h1('Counts per key')
    print_counter_as_table(key_counts, ["key", "count"], 50)
    print()
    print_h1('Simultaneous counts')
    print_counter_as_table(simultaneous_counts, ["key", "count"], 50)
    print()
    print_h1('Simultaneous mods counts')
    print_counter_as_table(mods_simultaneous_counts, ["key", "count"], 50)
    print()

    all_durations = []
    mod_durations = []
    non_mod_durations = []

    print_h1("Durations")
    if PRINT_INDIVIDUAL:
        print_h2("Per key")

    for key, durations in key_durations.items():
        if PRINT_INDIVIDUAL:
            print_h3(f"Key '{key}'")
            print_stats(durations)
        all_durations.extend(durations)
        d = mod_durations if key in MOD_KEYS else non_mod_durations
        d.extend(durations)

    print_h2("All keys")
    print_stats(all_durations)

    print_h2("Non-mods")
    print_stats(non_mod_durations)

    print_h3("Zero overlap")
    print_stats(zero_overlap_durations[NON_MOD_VALUE])

    print_h3("Overlap")
    print_stats(sum((v for k, v in key_durations.items() if k not in MOD_KEYS), start=[]))

    print_h2("Mods")
    print_stats(mod_durations)

    print_h3("Zero overlap")
    print_stats(zero_overlap_durations[MOD_VALUE])

    print_h3("Overlap")
    print_stats(sum((v for k, v in key_durations.items() if k in MOD_KEYS), start=[]))

    all_between_durations = []
    mod_between_durations = []
    non_mod_between_durations = []

    print()
    print_h1("Time between previous release and this press (no overlap)")
    if PRINT_INDIVIDUAL:
        print_h2("Per key")

    for key, durations in duration_between_previous_release_and_this_press.items():
        if PRINT_INDIVIDUAL:
            print_h3(f"Key '{key}'")
            print_stats(durations)

        all_between_durations.extend(durations)
        d = mod_between_durations if key in MOD_KEYS else non_mod_between_durations
        d.extend(durations)

    print_h2("All keys")
    print_stats(all_between_durations)

    print_h2("Non-mods")
    print_stats(non_mod_between_durations)

    print_h2("Mods")
    print_stats(mod_between_durations)

    print()
    print_h1("Intersections")
    print_h2("Non-mods")
    print_intersection_stats(non_mod_intersections, 'non-mods')

    print_h2("Mods")
    print_intersection_stats(mod_intersections, 'mods')

    print_h4("Duration between presses (only wrapped)")
    print_stats(wrapped_durations_press_and_next_press)
    print()

    print_h1("Counts per overlap-type")

    print_table([
        ['type', 'count', '%'],
        None,
        *p_rows(zero_overlap_counts, "zero overlap"),
        [],
        *p_multi_rows(overlap_counts, "overlaps"),
        [],
        *p_multi_rows(wrap_counts, "wraps"),
        [],
        *p_rows(total_counts),
    ])
    print()

    # we want to know the real ratio of mods overlapping anything to non-mods overlapping anything
    moa = count_any_first(overlap_counts, MOD_VALUE)
    nmoa = count_any_first(overlap_counts, NON_MOD_VALUE)

    # same for wrap
    mwa = count_any_first(wrap_counts, MOD_VALUE)
    nmwa = count_any_first(wrap_counts, NON_MOD_VALUE)

    print_h2('Overlaps')
    print_table([
        ["mods overlaps any", "non-mods overlaps any"],
        [moa, nmoa],
    ])
    print()
    if moa > 0:
        print(f'as a ratio: `1 : {nmoa / moa:.2f}`')
    print()

    print_h2('Wraps')
    print_table([
        ['mods wraps any', 'non-mods wraps any'],
        [mwa, nmwa],
    ])
    print()
    if nmwa > 0:
        print(f'as a ratio: `{mwa / nmwa:.2f} : 1`')
    print()
    print()

    print_h2("Of non-mods")
    print_table(p_variations(NON_MOD_VALUE))
    print()

    print_h2("Of mods")
    print_table(p_variations(MOD_VALUE))
    print()

    mod_training_data_counter = Counter()

    TRAINING_DATA = collect_training_data(events, mod_training_data_counter)
    print_h1("Training Data")
    print_table([
        ['type', 'count', '%'],
        None,
        ['total', TRAINING_DATA.count],
        [],
        pct2_row('mod', TRAINING_DATA.mod_count, TRAINING_DATA.non_mod_count),
        pct2_row('non-mod', TRAINING_DATA.non_mod_count, TRAINING_DATA.mod_count),
        [],
        pct2_row('mod overlap', TRAINING_DATA.mod_overlap_count, TRAINING_DATA.non_mod_overlap_count),
        pct2_row('non-mod overlap', TRAINING_DATA.non_mod_overlap_count, TRAINING_DATA.mod_overlap_count),
        [],
        pct2_row('mod wrap', TRAINING_DATA.mod_wrap_count, TRAINING_DATA.non_mod_wrap_count),
        pct2_row('non-mod wrap', TRAINING_DATA.non_mod_wrap_count, TRAINING_DATA.mod_wrap_count),
        [],
        pct2_row('mod triple-down', TRAINING_DATA.mod_triple_down_count, TRAINING_DATA.non_mod_triple_down_count),
        pct2_row('non-mod triple-down', TRAINING_DATA.non_mod_triple_down_count, TRAINING_DATA.mod_triple_down_count),
    ])
    print()

    print_h2("Most common mods")
    print_counter_as_table(mod_training_data_counter, ["key", "count"], 50)
    print()

    write_csv_of_training_data(TRAINING_DATA)
