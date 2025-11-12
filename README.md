This is the github repo for my blog website. It's built with [Hugo](https://gohugo.io/). The theme is a customized version of [Hermit-V2](https://github.com/1bl4z3r/hermit-V2), which is tracked in [this repo](https://github.com/Xinyu-Li-123/customized-hermit-V2/tree/main).

## Tips

To create posts in VSCode, you can install the [Insert Date String](https://marketplace.visualstudio.com/items?itemName=jsynowiec.vscode-insertdatestring) extension, so that it's easier to fill in the `date` attribute in the front matter of the post.

## TODO

- [ ] Allow custom code colorscheme

- [ ] Fix recent post bug. Currently it only fetches recent posts within 1 or 2 level of nested folders. It should be able to walk over all subfolders and fetch the most recent posts at compile time.

- [ ] Provide options to fold all code blocks in front matter

    This is because some of the leetcode note contains long codes, making it hard to read.

    Either there is a feature in hermit v2 that does this, or we will have to implement it ourselves.

- [ ] Change the color scheme of code block to lighe mode as well.

- [ ] Add a "go back to parent directory" button for each post / folder
