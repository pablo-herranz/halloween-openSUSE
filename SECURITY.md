# Security policy

A theme is mostly artwork, but this one also ships scripts that run as root:
`install/install-root.sh` writes to `/usr/share` and `/etc/sddm.conf.d` and
rebuilds the initrds, and `install/uninstall-root.sh` undoes that. Plasma
global themes and SDDM themes can also contain QML.

## Supported versions

Fixes go into `main` and the next release. Older releases are not patched.

## Reporting a vulnerability

Please don't open a public issue. Report it privately through GitHub:
**Security** → **Report a vulnerability** on
[the repository](https://github.com/plusky/halloween-openSUSE/security/advisories/new).
Include what is affected, how to reproduce it, and its impact.

You'll get an answer within a week. Once a fix is ready, it is released and
the advisory is published, crediting you if you like.
