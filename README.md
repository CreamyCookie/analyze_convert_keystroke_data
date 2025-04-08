# Create keystroke dataset to train heuristic tap hold functions 
The following steps were already done and the resulting QMK code can be found [here](https://github.com/CreamyCookie/qmk_userspace/tree/main/keyboards/ducktopus/keymaps/vial/features).

Of course, you may want to change settings and redo them.

## Step 1: Filter and convert the dataset
The original dataset has approximately 136,000,000 presses and 168,000 volunteers. For more information, and where to download it, see the [dataset section](#dataset).

After filtering out bad (too slow), suspicious (too fast), and incorrect data (uppercase letter, but no shift pressed), we are left with 48,064,975 presses and 67,647 volunteers.

Extract the downloaded dataset into the `extract_archive_in_here` directory.

Then run [filter_and_convert_keystroke_dataset.py](filter_and_convert_keystroke_dataset.py). 

## Step 2: Analyze converted dataset to create training dataset
Run [analyze.py](analyze.py).

## Step 3: Start "evolving" heuristic tap hold functions
For that, head over to the [evolve_heuristic_tap_hold](https://github.com/CreamyCookie/evolve_heuristic_tap_hold) repository.

# Analysis output
The following is the output of step 2.

-------------------------------------------------------------------------------

All durations are milliseconds.

Loading events from filtered_events.csv.gz

Loaded 96_129_950 events


# Counts per key
| key       |     count |
|-----------|-----------|
| space     | 7_247_964 |
| e         | 4_418_273 |
| t         | 3_199_986 |
| o         | 2_827_989 |
| a         | 2_787_965 |
| i         | 2_721_249 |
| n         | 2_405_392 |
| s         | 2_211_163 |
| backspace | 2_170_296 |
| r         | 1_949_707 |
| shift     | 1_750_737 |
| h         | 1_728_413 |
| l         | 1_507_940 |
| d         | 1_271_297 |
| u         | 1_044_181 |
| c         |   917_091 |
| w         |   897_914 |
| m         |   887_845 |
| .         |   886_472 |
| y         |   849_914 |
| g         |   744_767 |
| f         |   690_287 |
| p         |   672_809 |
| b         |   521_973 |
| k         |   421_211 |
| v         |   411_532 |
| '         |   189_910 |
| ,         |   141_238 |
| j         |    90_000 |
| ?         |    86_434 |
| x         |    68_136 |
| q         |    37_775 |
| /         |    33_258 |
| 1         |    27_224 |
| -         |    25_260 |
| 0         |    24_523 |
| caps_lock |    18_781 |
| ;         |    17_685 |
| 2         |    16_956 |
| z         |    15_051 |
| left      |    11_907 |
| !         |    11_375 |
| 3         |    10_802 |
| 9         |     9_782 |
| 4         |     9_632 |
| 5         |     8_638 |
| =         |     7_854 |
| 6         |     7_073 |
| 7         |     5_674 |
| >         |     5_461 |

# Simultaneous counts
| key               |  count |
|-------------------|--------|
| shift i space     | 14_779 |
| shift t h         |  3_530 |
| shift w e         |  1_835 |
| shift u s         |  1_219 |
| ctrl backspace    |  1_100 |
| shift a m         |    959 |
| shift s space     |    797 |
| shift o k         |    691 |
| ctrl left         |    615 |
| shift d o         |    482 |
| space shift i     |    477 |
| shift h o         |    451 |
| shift c o         |    422 |
| shift c h         |    419 |
| space shift s     |    395 |
| shift h e         |    395 |
| shift m a         |    383 |
| shift s h         |    382 |
| shift n o         |    363 |
| shift s o         |    353 |
| shift m o         |    352 |
| shift w h         |    349 |
| shift p m         |    345 |
| shift p l         |    336 |
| shift c l         |    324 |
| shift s u         |    317 |
| shift y o         |    310 |
| shift i n         |    281 |
| shift ? space     |    280 |
| space shift f     |    279 |
| shift w i         |    270 |
| shift e n         |    261 |
| shift a p         |    256 |
| shift a s         |    253 |
| shift s a         |    250 |
| shift l e         |    250 |
| shift n e         |    240 |
| space shift t     |    224 |
| space shift m     |    214 |
| shift i t         |    202 |
| shift o n         |    198 |
| shift a space     |    197 |
| shift j o         |    197 |
| shift f l         |    197 |
| shift backspace s |    194 |
| ctrl right        |    192 |
| space shift c     |    191 |
| space shift d     |    183 |
| shift o u         |    183 |
| shift c a         |    171 |

# Simultaneous mods counts
| key            | count |
|----------------|-------|
| ctrl shift     |   786 |
| ctrl_r shift   |    92 |
| alt ctrl       |    75 |
| alt shift      |    49 |
| alt ctrl shift |     3 |
| shift shift_r  |     2 |
| ctrl_l shift   |     1 |

# Durations
## All keys
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_992 | 112 |    103 |       304 |

## Non-mods
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_830 | 106 |    101 |       208 |

### Zero overlap
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_055 |  93 |     88 |       178 |

### Overlap
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_830 | 106 |    101 |       208 |

## Mods
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_992 | 285 |    222 |     1_280 |

### Zero overlap
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_930 | 242 |    176 |     1_360 |

### Overlap
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_992 | 285 |    222 |     1_280 |


# Time between previous release and this press (no overlap)
## All keys
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 1_499 | 114 |     72 |       736 |

## Non-mods
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 1_499 | 112 |     72 |       713 |

## Mods
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 1_499 | 238 |    125 |     1_471 |


# Intersections
## Non-mods
### Space THEN others
#### Overlap duration
| min | max | avg | median | 99% below |
|-----|-----|-----|--------|-----------|
| 1   | 620 |  31 |     26 |       104 |

#### Duration between both presses
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 6_589 | 100 |     96 |       192 |

### All non-mods
#### Overlap duration
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 3_217 |  38 |     32 |       116 |

#### Overlap percentages
| min | max | avg | median | 99% below |
|-----|-----|-----|--------|-----------|
| 0   | 100 |  29 |     27 |        83 |

#### Duration between both presses
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 6_589 |  94 |     90 |       187 |

## Mods
### Space THEN others
#### Overlap duration
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 2_895 |  39 |     32 |       136 |

#### Duration between both presses
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 6_376 |  91 |     82 |       180 |

### All mods
#### Overlap duration
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 1   | 5_232 |  75 |     72 |       169 |

#### Overlap percentages
| min | max | avg | median | 99% below |
|-----|-----|-----|--------|-----------|
| 0   | 100 |  53 |     41 |       100 |

#### Duration between both presses
| min |   max | avg | median | 99% below |
|-----|-------|-----|--------|-----------|
| 0   | 6_939 | 200 |    137 |     1_188 |

#### Duration between presses (only wrapped)
| min    | max |  avg | median | 99% below |
|--------|-----|------|--------|-----------|
| -6_880 |  -1 | -228 |   -140 |       -22 |


# Counts per overlap-type
| type                     |      count |     % |
|--------------------------|------------|-------|
| non-mod zero overlap     | 25_531_735 | 99.67 |
| mod zero overlap         |     84_879 |  0.33 |
| total zero overlap       | 25_616_614 |       |
|                          |            |       |
| non-mod overlaps non-mod | 12_180_827 | 90.14 |
| non-mod overlaps mod     |    102_121 |  0.76 |
| mod overlaps non-mod     |  1_229_889 |  9.1  |
| mod overlaps mod         |        475 |  0    |
| total overlaps           | 13_513_312 |       |
|                          |            |       |
| non-mod wraps non-mod    |    117_310 | 17.08 |
| non-mod wraps mod        |      1_927 |  0.28 |
| mod wraps non-mod        |    567_001 | 82.56 |
| mod wraps mod            |        536 |  0.08 |
| total wraps              |    686_774 |       |
|                          |            |       |
| non-mod                  | 46_308_757 | 96.35 |
| mod                      |  1_756_218 |  3.65 |
| total                    | 48_064_975 |       |

## Overlaps
| mods overlaps any | non-mods overlaps any |
|-------------------|-----------------------|
| 1_230_364         |            12_282_948 |

as a ratio: `1 : 9.98`

## Wraps
| mods wraps any | non-mods wraps any |
|----------------|--------------------|
| 567_537        |            119_237 |

as a ratio: `4.76 : 1`


## Of non-mods
| type                |     % |
|---------------------|-------|
| no overlap/wrap     | 64.26 |
|                     |       |
| any overlap         | 34.01 |
| - overlaps non-mod  | 30.66 |
| - overlaps mod      |  0.26 |
| - overlapped by mod |  3.1  |
|                     |       |
| any wrap            |  1.73 |
| - wraps non-mod     |  0.3  |
| - wraps mod         |  0    |
| - wrapped by mod    |  1.43 |

## Of mods
| type                    |     % |
|-------------------------|-------|
| no overlap/wrap         |  4.27 |
|                         |       |
| any overlap             | 67.07 |
| - overlaps non-mod      | 61.9  |
| - overlaps mod          |  0.02 |
| - overlapped by non-mod |  5.14 |
|                         |       |
| any wrap                | 28.66 |
| - wraps non-mod         | 28.54 |
| - wraps mod             |  0.03 |
| - wrapped by non-mod    |  0.1  |

# Training Data
| type                |      count |     % |
|---------------------|------------|-------|
| total               | 10_299_575 |       |
|                     |            |       |
| mod                 |  1_319_001 | 12.81 |
| non-mod             |  8_980_574 | 87.19 |
|                     |            |       |
| mod overlap         |    975_101 |  9.93 |
| non-mod overlap     |  8_848_600 | 90.07 |
|                     |            |       |
| mod wrap            |    343_900 | 72.27 |
| non-mod wrap        |    131_974 | 27.73 |
|                     |            |       |
| mod triple-down     |     28_959 | 10.32 |
| non-mod triple-down |    251_715 | 89.68 |

## Most common mods
| key   |     count |
|-------|-----------|
| shift | 1_318_915 |
| ctrl  |        81 |
| alt   |         5 |

-------------------------------------------------------------------------------

# Dataset
The dataset that was used here, can be downloaded at:

https://userinterfaces.aalto.fi/136Mkeystrokes/

```
Vivek Dhakal, Anna Maria Feit, Per Ola Kristensson, Antti Oulasvirta
Observations on Typing from 136 Million Keystrokes. 
In Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems, ACM, 2018.

@inproceedings{dhakal2018observations,
author = {Dhakal, Vivek and Feit, Anna and Kristensson, Per Ola and Oulasvirta, Antti},
booktitle = {Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems (CHI '18)},
title = {{Observations on Typing from 136 Million Keystrokes}},
year = {2018}
publisher = {ACM}
doi = {https://doi.org/10.1145/3173574.3174220}
keywords = {text entry, modern typing behavior, large-scale study}
}
```

You are free to use this data for non-commercial use in your own research or projects with attribution to the authors.
