"""kbtool: the knowledge base of the NRPIC-cosmology program (brief section 12).

Stages filled so far: K0 (environment, layout, schema) and K1 (manifests, inventory,
`kb verify-downloads`). Everything under kb-data/raw is untrusted data: this package
reads it as bytes, never executes, compiles or imports anything from it.
"""
__version__ = "0.1.0"
SCHEMA_VERSION = 1
