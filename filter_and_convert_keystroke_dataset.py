import csv
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path

from utils.serialization import TabMinDialect

DATASET_PATH = Path(__file__).parent / 'dataset'

EXTRACTED_ARCHIVE_PATH = DATASET_PATH / 'extract_archive_in_here'
CSV_DIR_PATH = EXTRACTED_ARCHIVE_PATH / "files"
PARTICIPANTS_CSV_PATH = EXTRACTED_ARCHIVE_PATH / "metadata_participants.txt"

RESULT_PATH = DATASET_PATH / "filtered_events.csv.gz"
RESULT_USED_PARTICIPANTS_PATH = DATASET_PATH / "filtered_events.participants_used.json"
RESULT_USED_PARTICIPANTS_METADATA = DATASET_PATH / "filtered_events.participants_used_metadata.csv"

MAP_LETTER = {'ARW_LEFT': 'left', 'ARW_RIGHT': 'right', 'ARW_UP': 'up', 'ARw_DOWN': 'down',
              ' ': 'space', 'BKSP': 'backspace'}

CODE_TO_LETTER = {
    '8': 'backspace', '9': 'tab', '12': 'clear', '13': 'enter', '16': 'SHIFT', '17': 'ctrl',
    '18': 'alt', '19': 'pause', '20': 'caps_lock', '27': 'esc', '32': 'space', '33': 'page_up',
    '34': 'page_down', '35': 'end', '36': 'home', '37': 'left', '38': 'up', '39': 'right',
    '40': 'down', '41': 'select', '42': 'print', '43': 'execute', '44': 'print_screen',
    '45': 'insert', '46': 'delete', '47': 'help', '48': '0', '49': '1', '50': '2', '51': '3',
    '52': '4', '53': '5', '54': '6', '55': '7', '56': '8', '57': '9', '65': 'a', '66': 'b',
    '67': 'c', '68': 'd', '69': 'e', '70': 'f', '71': 'g', '72': 'h', '73': 'i', '74': 'j',
    '75': 'k', '76': 'l', '77': 'm', '78': 'n', '79': 'o', '80': 'p', '81': 'q', '82': 'r',
    '83': 's', '84': 't', '85': 'u', '86': 'v', '87': 'w', '88': 'x', '89': 'y', '90': 'z',
    '91': 'cmd_l', '92': 'cmd_r', '93': 'menu', '95': 'sleep', '96': 'num_0', '97': 'num_1',
    '98': 'num_2', '99': 'num_3', '100': 'num_4', '101': 'num_5', '102': 'num_6', '103': 'num_7',
    '104': 'num_8', '105': 'num_9', '106': '*', '107': '+', '108': 'separator', '109': '-',
    '110': '.', '111': '/', '112': 'f1', '113': 'f2', '114': 'f3', '115': 'f4', '116': 'f5',
    '117': 'f6', '118': 'f7', '119': 'f8', '120': 'f9', '121': 'f10', '122': 'f11', '123': 'f12',
    '124': 'f13', '125': 'f14', '126': 'f15', '127': 'f16', '128': 'f17', '129': 'f18',
    '130': 'f19', '131': 'f20', '132': 'f21', '133': 'f22', '134': 'f23', '135': 'f24',
    '144': 'num_lock', '145': 'scroll_lock', '160': 'shift_l', '161': 'shift_r', '162': 'ctrl_l',
    '163': 'ctrl_r', '164': 'alt_l', '165': 'alt_r', '166': 'browser_back',
    '167': 'browser_forward', '168': 'browser_refresh', '169': 'browser_stop',
    '170': 'browser_search', '171': 'browser_favorites', '172': 'browser_start_and_home',
    '173': 'media_volume_mute', '174': 'media_volume_down', '175': 'media_volume_up',
    '176': 'media_next', '177': 'media_previous', '178': 'media_stop', '179': 'media_play_pause',
    '180': 'start_mail', '181': 'select_media', '182': 'start_application_1',
    '183': 'start_application_2', '186': ';', '187': '+', '188': ',', '189': '-', '190': '.',
    '191': '/', '219': '[', '220': '\\', '221': ']', '222': "'", '226': '<'
}

LAYOUT_TO_SHIFTED_KEY_TO_KEY = {
    "qwerty": {"!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8",
               "(": "9", ")": "0", "?": "/", "{": "[", "}": "]", "_": "-", ":": ";", "<": ",",
               ">": ".", '"': "'", "|": "\\", "+": "="},
    "qwertz": {"!": "1", "\"": "2", "§": "3", "$": "4", "%": "5", "&": "6", "/": "7", "(": "8",
               ")": "9", "=": "0", "?": "ß", "*": "+", "'": "#", "_": "-", ":": ".", ";": ",",
               ">": "<", "~": "+", "°": "^"},
    "azerty": {"&": "1", "é": "2", '"': "3", "'": "4", "(": "5", "-": "6", "è": "7", "_": "8",
               "ç": "9", "à": "0", ")": "°", "+": "=", "?": ",", ".": ";", "/": ":", "§": "!"}
}

UPPERCASE = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
             'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'À', 'Á', 'Ä', 'Å', 'Ç', 'È', 'É', 'Í',
             'Ï', 'Ñ', 'Ô', 'Ö', 'Ø', 'Ù', 'Ü'}

LAYOUT_TO_UPPERCASE = {
    layout: UPPERCASE | values.keys() for (layout, values) in LAYOUT_TO_SHIFTED_KEY_TO_KEY.items()
}

SUPPORTED_LAYOUTS = LAYOUT_TO_UPPERCASE.keys()

KS_HEADER = ['PARTICIPANT_ID', 'TEST_SECTION_ID', 'SENTENCE', 'USER_INPUT', 'KEYSTROKE_ID',
             'PRESS_TIME',
             'RELEASE_TIME', 'LETTER', 'KEYCODE']

PARTICIPANT_IDX = KS_HEADER.index('PARTICIPANT_ID')
SECTION_IDX = KS_HEADER.index('TEST_SECTION_ID')
PRESS_TIME_IDX = KS_HEADER.index('PRESS_TIME')
RELEASE_TIME_IDX = KS_HEADER.index('RELEASE_TIME')
LETTER_IDX = KS_HEADER.index('LETTER')
KEYCODE_IDX = KS_HEADER.index('KEYCODE')

KS_HEADER_TO_INDEX = dict(enumerate(KS_HEADER))

maxInt = sys.maxsize

# find acceptable value for field size limit
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

num_participants_kept = 0
valid_participant_file_names = set()
participant_id_to_layout = {}

num_original_participants = 0
num_down = 0

participant_id_to_metadata = {}

with PARTICIPANTS_CSV_PATH.open(mode='r', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter='\t')

    for row in reader:
        num_original_participants += 1

        if not row['FINGERS'] or not row['ERROR_RATE'] or not row['AVG_WPM_15']:
            continue

        layout = row['LAYOUT']
        if layout not in SUPPORTED_LAYOUTS:
            continue
        layout = layout.strip()

        fingers = row['FINGERS'].strip()
        error_rate = float(row['ERROR_RATE'])
        avg_wpm_15 = float(row['AVG_WPM_15'])

        if avg_wpm_15 > 114 and error_rate == 0:
            # may have cheated (also not representable for most typists)
            continue

        # Average WPM is around 40. In the dataset it is 60.25 (median 59.89)
        # According to the study: Overlapping key presses indicate faster typing.
        # We want a lot of overlap, and we want faster typists.
        if fingers != "1-2" and error_rate < 3.3 and avg_wpm_15 > 40:
            num_participants_kept += 1
            pid = row['PARTICIPANT_ID']
            valid_participant_file_names.add(f'{pid}_keystrokes.txt')
            participant_id_to_layout[pid] = layout
            participant_id_to_metadata[pid] = dict(row)

print(num_participants_kept, 'of', num_original_participants)

keystrokes_result = []

max_dur_participant = None
max_dur_participant_dur = None

cur_t = 0
used_participants = set()


def parse_file(csv_path, writer):
    global cur_t, num_down

    if csv_path.name not in valid_participant_file_names:
        return

    participant_id = get_participant_id(csv_path)
    layout = participant_id_to_layout.get(participant_id)
    if not layout:
        return

    with csv_path.open(mode='r', newline='', encoding='ansi') as file:
        reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_NONE)

        # Skip the header row
        header = next(reader)
        if header != KS_HEADER:
            print_file_ignored(csv_path, f"Header is not correct: {header}")
            return

        section_id_to_rows = get_sections(csv_path, reader)

    if not section_id_to_rows:
        return

    # Sort the rows of each section
    events = sum(section_id_to_rows.values(), start=[])
    events.sort(key=lambda ev: ev[0])

    check_result = check_for_issues(events, layout)
    if check_result is not None:
        print_file_ignored(csv_path, check_result)
        return

    first_t = events[0][0]
    last_t = events[-1][0]

    if first_t < timestamp_of(2000, 1, 1):
        print_file_ignored(csv_path, 'Made before year 2000')
        return

    cur_delta = cur_t - first_t

    write_rows(writer, events, cur_delta)
    num_down += len(events) // 2

    # mark the end of this participant's block
    writer.writerow((last_t + cur_delta + to_ms(seconds=30), None, None))

    used_participants.add(participant_id)

    cur_t = last_t + cur_delta + to_ms(minutes=30)


def get_participant_id(path: Path) -> str:
    return path.name.split('_')[0]


def get_sections(csv_path, reader):
    section_id_to_rows = {}
    ignored_section_ids = set()
    num_presses = 0

    num_low_delta = 0

    check_if_section_was_finished = False
    prev_section_id = None
    participant_id = get_participant_id(csv_path)

    for row in reader:
        if len(row) < 8 or row[-1] == '':
            check_if_section_was_finished = True
            continue

        if row[PARTICIPANT_IDX] != participant_id:
            print_file_ignored(csv_path,
                               f'Participant ID differs from filename: {row[PARTICIPANT_IDX]}')
            return

        section_id = row[SECTION_IDX]
        if not section_id or section_id in ignored_section_ids:
            continue

        if check_if_section_was_finished:
            check_if_section_was_finished = False
            if section_id == prev_section_id:
                print_section_ignored(csv_path, section_id, 'There was an incomplete row')
                del section_id_to_rows[section_id]
                ignored_section_ids.add(section_id)
                continue

        section = section_id_to_rows.get(section_id)
        if section is None:
            section = []
            section_id_to_rows[section_id] = section

        # first use float as int("1.473278e+12") will fail
        press_time_ms = int(float(row[PRESS_TIME_IDX]))
        release_time_ms = int(float(row[RELEASE_TIME_IDX]))

        delta = release_time_ms - press_time_ms

        letter = row[LETTER_IDX]

        if delta < 0:
            # release before press
            del section_id_to_rows[section_id]
            ignored_section_ids.add(section_id)
            continue
        elif delta > to_ms(seconds=7):
            # We're assuming that given that this happened,
            # all times of this participant are unreliable
            print_file_ignored(csv_path,
                               f'{letter} at {press_time_ms} took way too long: {delta} ms')
            return
        elif delta < 1:
            print_section_ignored(csv_path, section_id,
                                  f'{letter} at {press_time_ms} was way too short: {delta} ms')
            del section_id_to_rows[section_id]
            ignored_section_ids.add(section_id)
            continue

        if letter == '' or not letter.isprintable():
            # Sometimes there seem to be key presses missing (see participant 100032)
            # but this may be a general problem (or due to using the mouse to move the cursor)

            # print_ignored(csv_path, 'No letter, only key codes')
            # return

            code = row[KEYCODE_IDX]
            letter = CODE_TO_LETTER.get(code)

        if letter is None:
            del section_id_to_rows[section_id]
            ignored_section_ids.add(section_id)
            continue

        if delta < 10:
            num_low_delta += 1

        prev_section_id = section_id
        num_presses += 1
        section.append([press_time_ms, 1, letter])
        section.append([release_time_ms, 0, letter])

    if not section_id_to_rows or not num_presses:
        return

    if (num_low_delta / num_presses) > 0.4:
        print_file_ignored(csv_path, 'A large percentage of key presses were too short')
        return

    return section_id_to_rows


def print_file_ignored(csv_path, message):
    print(f'{csv_path.name} IGNORED: {message}')


def print_section_ignored(csv_path, section_id, message):
    print(f'{csv_path.name} SECTION {section_id} IGNORED: {message}')


def to_ms(minutes=0, seconds=0):
    return minutes * 60 * 1000 + seconds * 1000


def timestamp_of(year, month, day):
    return int(datetime(year, month, day).timestamp() * 1000)


def to_timestamp(dt: datetime):
    return int(dt.timestamp() * 1000)


def check_for_issues(events, layout):
    down_lower_letters = {}
    num_overlap = 0
    uppercase = LAYOUT_TO_UPPERCASE[layout]

    for row in events:
        t, down, letter = row
        lower_letter = letter.lower()

        if down:
            if down_lower_letters:
                for k in down_lower_letters:
                    down_lower_letters[k] += 1
                num_overlap += 1

            if lower_letter in down_lower_letters:
                return f'{letter} down at {t} but was already'
            down_lower_letters[lower_letter] = 0

            if letter in uppercase and 'shift' not in down_lower_letters:
                return f'{letter} is uppercase at {t} but shift is not down'
        else:
            if lower_letter not in down_lower_letters:
                return f'{letter} up at {t} but is not even down'

            down_with_n_keys = down_lower_letters.pop(lower_letter)
            if lower_letter not in ('shift', 'ctrl') and down_with_n_keys > 3:
                return f'{letter} up at {t} was down with {down_with_n_keys} other keys at the same time'

    if down_lower_letters:
        return f'Some keys were never released: {down_lower_letters}'

    if num_overlap < 7:
        # This could be contested. It does skew the statistics (zero overlap vs overlap etc.),
        # but for our use case (tap hold), we do not need zero overlaps.
        return f'Too few overlapping keys: {num_overlap}'

    return None


def find_overlapping_timestamp(sections):
    """
    Both the sections and the rows inside each section must be sorted.
    Checks if the last timestamp in sections[n] < first timestamp in sections[n+1].
    If that is true for all sections, we return None.
    Otherwise, we return the two timestamp that are overlapping.
    """
    if len(sections) < 2:
        return None

    last_of_prev_t = None
    for section in sections:
        if last_of_prev_t is not None:
            first_of_cur_t = section[0][0]
            if first_of_cur_t <= last_of_prev_t:
                return last_of_prev_t, first_of_cur_t
        last_of_prev_t = section[-1][0]
    return None


def write_rows(writer, events, delta):
    # We will not map keys here to their non-shifted version, as that leads to conflicts (keys pressed down twice)
    for row in events:
        dt, down, letter = row
        letter = MAP_LETTER.get(letter, letter)
        last_t = dt + delta

        try:
            writer.writerow((last_t, down, letter.lower().strip().replace(' ', '_')))
        except csv.Error as e:
            raise e


def size_in_mib(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def name_and_size(path: Path) -> str:
    return f'{path.name}: {size_in_mib(path)} MiB'


with gzip.open(str(RESULT_PATH), 'wt', newline='', encoding='utf-8') as gz_file:
    writer = csv.writer(gz_file, dialect=TabMinDialect)

    for path in sorted(CSV_DIR_PATH.glob("*.txt"), key=lambda i: int(get_participant_id(i))):
        try:
            parse_file(path, writer)
        except csv.Error as e:
            print(f'{path.name} IGNORED: {e}')
        except Exception as e:
            print(path, e)
            raise e

print(f"{len(used_participants)} participants left")
print(f'{num_down} keys down (and up)')
print(name_and_size(RESULT_PATH))

RESULT_USED_PARTICIPANTS_PATH.write_text(
    json.dumps(sorted(used_participants, key=int))
)

with RESULT_USED_PARTICIPANTS_METADATA.open('w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ['PARTICIPANT_ID', 'AGE', 'GENDER', 'HAS_TAKEN_TYPING_COURSE', 'COUNTRY', 'LAYOUT',
                  'NATIVE_LANGUAGE',
                  'FINGERS', 'TIME_SPENT_TYPING', 'KEYBOARD_TYPE', 'ERROR_RATE', 'AVG_WPM_15',
                  'AVG_IKI', 'ECPC',
                  'KSPC', 'ROR']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=TabMinDialect)

    writer.writeheader()
    for pid, md in sorted(participant_id_to_metadata.items(),
                          key=lambda x: float(x[1]['AVG_WPM_15']), reverse=True):
        if pid in used_participants:
            writer.writerow(md)
