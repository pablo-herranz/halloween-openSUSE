# Security policy

A theme is mostly artwork, but `sudo make install` runs `tools/install.py` as
root, which writes to `/usr/share`, `/usr/lib64/firefox` and (with
`install-defaults`) `/etc`. The development helpers in `tools/dev/` also run
as root on test machines and rebuild the initrds. Plasma global themes and
SDDM themes can also contain QML, and the Firefox theme is installed where
Firefox doesn't check signatures.

## Supported versions

Fixes go into `main` and the next release. Older releases are not patched.

## Reporting a vulnerability

Please don't open a public issue. Report it privately through GitHub:
**Security** → **Report a vulnerability** on
[the repository](https://github.com/plusky/halloween-openSUSE/security/advisories/new).
Include what is affected, how to reproduce it, and its impact.

You'll get an answer within a week. Once a fix is ready, it is released and
the advisory is published, crediting you if you like.
