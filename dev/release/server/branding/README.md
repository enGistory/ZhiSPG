# Server Branding

This folder contains the white-label assets applied to the bundled frontend static files inside the executable server jar.

To switch brands later:

1. Replace `logo.png` and `favicon.png`.
2. Replace `login-background.png` if the login visual should change.
3. Update `brand.config.json`.
4. Rebuild `dev/release/server/Dockerfile`.

`hideRightHeaderLinks` hides the tutorial, official website, and GitHub shortcuts from the top-right header.
`loginPage` controls the white-label login page background and layout patch.

The patch script intentionally replaces user-visible `OpenSPG` text but does not replace the uppercase `OPENSPG` password hash salt.
