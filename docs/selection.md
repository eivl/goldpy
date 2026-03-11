# Quote selection

`goldpy` does not try to pretend there is only one obvious way to read a live
quote feed. The data coming back from Swissquote can contain multiple sources
and multiple spread profiles for the same pair, so the project makes the
selection rule explicit.

## The raw input

For a pair like `XAU/USD`, the upstream response may include:

- More than one platform
- More than one server within a platform
- More than one spread profile for each source

The service layer flattens those nested entries into candidate prices. Each
candidate keeps:

- Platform
- Server
- Spread profile
- Bid
- Ask
- Midpoint
- Spread
- Timestamp

That flattening step matters because it lets the selection logic compare like
with like.

## Aggregate mode

`aggregate` is the default because it answers the broad question most people
actually mean when they ask where gold is trading right now.

The algorithm:

1. Filter candidates by platform and spread profile if the caller requested it.
2. Pick the highest available bid.
3. Pick the lowest available ask.
4. Compute the midpoint from those two values.
5. Keep the latest timestamp seen across the candidates.

This means the final bid and ask can come from different sources. That is
intentional. It gives a concise market edge view instead of forcing both sides
to come from the same quote.

## Tightest mode

`tightest` is stricter. It keeps bid and ask together from a single candidate.

The algorithm:

1. Filter candidates by platform and spread profile if requested.
2. Compare candidates by spread, from smallest to largest.
3. If two candidates have the same spread, prefer the one with the higher
   midpoint.

This mode is useful when you care about the most competitive single quote
rather than the best bid and ask across the whole set.

## Filtering

Two optional filters shape the candidate set before any selection happens:

- `platform`
- `spread_profile`

If filtering removes every candidate, `goldpy` raises a selection error rather
than guessing what to do next.

## Why both modes exist

I wanted the tool to stay honest about what it shows.

`aggregate` is good when you want a quick read on the available market edges.
`tightest` is better when you want one coherent quote from one source/profile
combination. Neither is universally better. They answer slightly different
questions, so the CLI exposes both.
