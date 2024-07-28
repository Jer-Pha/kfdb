# Kinda Funny Database

[kfdb.app](https://www.kfdb.app/)

## What is KFDB?

KFDB is a database that contains all Kinda Funny [YouTube](https://www.youtube.com/kindafunnygames) and [Patreon](https://www.patreon.com/kindafunny) content.

### How is the data gathered?

#### YouTube

YouTube video IDs, titles, descriptions, and publish dates are pulled directly from the YouTube API. Producers, Hosts, Shows, and Channels are manually input by [Jer-Pha](https://github.com/Jer-Pha).

_Note: paid YouTube membership videos are not part of the database._

#### Patreon

Patreon videos are pulled via RSS feed at the **10 USD** tier. Only the title and date of the episode is pulled. The database does not provide access to paid content. There are _some_ videos from [patreon.com/KindaFunnyGames](https://www.patreon.com/kindafunnygames) in the database. We no longer update new content from this Patreon page.

_Note: content from higher tiers (e.g. Monthly Hangouts) is not included in the database._

## Search

Users can add operators to searches for more precise results.

#### Operators

- A plus sign immediately \+**before** a word ensures that word will be in all results
- A minus sign \-~~before~~ the word removes all results with that word
- An asterisk is a wildcard, matching any words that start\*, \*end, or \*contain\* the given word
- Multi-word searches will match any of the given words, unless you add "quotation marks" around words that you want searched as a phrase

## Edits

Videos, shows, channels, and hosts all have an edit button. If a user believes something is incorrect or missing, they are able to submit an edit. The only exception to this is submitting pictures. Pictures must be submitted through email by sending to [info @ kfdb.app](mailto:info@kfdb.app)

## API

KFDB data is available to use for free via the [KFDB API](https://www.kfdb.app/api/docs/). Currently, the API is open to the public and does not require an authorization token for access. Please let us know if you're using the API in your project! We would love to check it out.
