---
description: Release and Push Process
---

When the user asks to push changes to the repository, or perform a release, ALWAYS follow these steps exactly:

1. **Review and Update Documentation**
   - Check the `README.md` and ensure all newly added features or bug fixes are documented.
   - Update the version number in `package.json` to the appropriate new version.

2. **Wait for User Approval (CRITICAL)**
   - DO NOT execute any `git push` or `gh release` commands yet.
   - Use the `notify_user` tool to summarize the changes made to the README and the proposed version bump.
   - Explicitly ask the user to confirm that the changes look correct before proceeding.

3. **Commit**
   - Once the user gives the "Go ahead" or confirms, stage all changes: `git add .`
   - Commit the changes with a clear message: `git commit -m "chore: release vX.Y.Z - <short summary of changes>"`

4. **Tag**
   - Create an annotated git tag with a description of the changes: `git tag -a vX.Y.Z -m "Release vX.Y.Z - <summary>"`

5. **Push and Release**
   - Push the code and the tags to the remote branch: `git push origin HEAD --tags`
   - Use the GitHub CLI to create the release: `gh release create vX.Y.Z --title "vX.Y.Z - <title>" --notes "<release notes>"`
