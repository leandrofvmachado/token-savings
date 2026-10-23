# token-savings

One install for the tools from the post "Como economizar tokens e diminuir a conta do Claude":

- [Caveman](https://github.com/JuliusBrussee/caveman): terse replies, better for long conversations.
- [Ponytail](https://github.com/dietrichgebert/ponytail): less code, about 10% cheaper in code sessions.

Both are referenced from their upstream repos, pinned to tested commits. Nothing is copied.

## Install

```
/plugin marketplace add <owner>/token-savings
/plugin install token-savings@token-savings
```

## Note

Both tools inject their instructions at every session start and start active. Remove with `/plugin uninstall token-savings@token-savings`, then uninstall `caveman` and `ponytail`.
