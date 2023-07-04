# How to release a new version

1. Run in the root directory `bump2version <major, minor, patch>` (creates commit and tag)
2. Push to GitHub (don't forget to push tags, too)
3. This triggers a GitHub action to build and push the image and to bump the typescript client
4. Draft a GitHub release based on the tag, auto-create the changelog
5. Publish the release
