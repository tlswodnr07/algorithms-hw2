# Repository instructions

- Implement the URL shortener using only the Python standard library.
- In `src/`, do not use `dict`, `set`, or Python's built-in `hash()` function. Use the
  project's explicit hash-table implementations instead.
- Generate short codes from monotonically increasing integer IDs encoded as base62.
  Never derive codes from URLs or hash values.
- Keep behavior aligned with `SPEC.md`, validate user input, and escape user-provided
  text before including it in HTML.
- Do not weaken or alter tests to make an implementation pass. Add focused tests for
  new behavior and run `make test` after code changes.
- Keep Git work on `feature/<issue>-<short-name>` branches, merge completed work into
  `develop`, and use commit messages in the form `Step N: description (#issue)`.
