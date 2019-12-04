# About this documentation

This documentation lives at https://onespacemedia.github.io/cms/.
If you are reading this documentation in the GitHub repository, you almost certainly don't want to be.

## Editing this documentation

This documentation is generated using [docsify](https://docsify.js.org/).
When working on it locally, you definitely want to install and use docsify for an optimal editing experience:

```
npm install -g docsify-cli
docsify serve docs/
```

Then visit http://localhost:3000/ for a pretty, live-reloading experience.

Via the magic of docsify, there is no build step, there is no build _system_, and there is no deployment step.
Pushing to or merging changes in to the `master` branch will automatically deploy to GitHub pages.

## Style

Single newlines are turned into a space (i.e. essentially ignored) by Markdown, so you can insert them mid-paragraph. Therefore, this document tries to stick to a one-sentence-per-line style in its source code (aka ["Semantic Linefeeds"](https://rhodesmill.org/brandon/2012/one-sentence-per-line/)),
partly to make diffs easier to read.

One-sentence-per-line should be considered a _maximum_ line length;
feel free to insert linebreaks to break long sentences into clauses.

## Adding a new section

To add a new top-level section to the documentation, simply create a Markdown file in the docs/ directory.
Then add a new entry to `_sidebar.md`:

```
* [New section name](my-new-section.md)
```
