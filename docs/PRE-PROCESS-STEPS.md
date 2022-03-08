# Dataset Pre-processing Steps 

## Dropping Columns
Unnecessary columns were dropped prior to any pre-processing to reduce the amount of redundant checks and niche cases that needed to be handled.

## Delimiter replacement
Prior to working with the dataset, some manual pre-processing took place using regex find/replace to get the dataset quickly ready for use.

Prior to setting delimiters, following replacements were completed to account for exceptions:
1. i.e., -> i.e,
2. IEEE., -> EEEE,
3. ACME., -> ACME,
4. OSA., -> OSA,
5. et. al., -> et. al,

With exceptions resolved, a global replacement was completed for:
1. ., -> ,
2. ; -> |

The replacement of the ".," values may not have been required everywhere, but it was done as a quick way to create an array of author names in Neo4j, as all author names were inside `"double quotes"`, which Neo4j treats as strings. These strings can now be split during initialization.

## Header Modifications
Headers were all modified to be lower case and without spaces for easier manipulation and consistency.

## Value Creation

