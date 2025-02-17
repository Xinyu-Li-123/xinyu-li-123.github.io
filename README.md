This is the github repo for my blog website. It's built with [Hugo](https://gohugo.io/). The theme is [hermit-v2](https://github.com/1bl4z3r/hermit-V2).

## Todo

- [ ] Provide options to fold all code blocks in front matter

    This is because some of the leetcode note contains long codes, making it hard to read.

    Either there is a feature in hermit v2 that does this, or we will have to implement it ourselves.

- [*] For each "folder", list the most recent 3 posts in that folder.

## Tips

To create posts in VSCode, you can install the [Insert Date String](https://marketplace.visualstudio.com/items?itemName=jsynowiec.vscode-insertdatestring) extension, so that it's easier to fill in the `date` attribute in the front matter of the post.

## Extension to Hermit-v2

- Group by `lastmod` instead of `date`

    We group posts by their last modified date, instead of their creation date. The last mod date is by default the git's last commit date of the file.

- Display recent posts

    In `hugo.toml`, set `displayRecent` to true. If `disableRecent` is not set to true in the page's front matter (defined in the `_index.md` file of the page's folder), a section of recent post will be displayed. The section's title and number of recent post are defined by `recentTitle` and `recentCount` respectively in `hugo.toml`.

    Below is an example that defines a recent post section with title "Recent Posts" and 3 most recent posts.

    ```toml
    displayRecent = true
    recentTitle = "Recent Posts"
    recentCount = 3
    ```