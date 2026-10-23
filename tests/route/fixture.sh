#!/usr/bin/env bash
# Build a scratch repo for /route tests in the directory given as $1.
set -euo pipefail
d=$1; mkdir -p "$d"/{app,services,config,tests,docs,notes,plan}; cd "$d"
git init -q 2>/dev/null || true
cat > app/cart.py <<'P'
def total(items):
    return sum(i["price"] * i["qty"] for i in items)
P
cat > app/client.py <<'P'
def get_cart():
    return []
P
cat > services/billing.py <<'P'
import json
def cfg(): return json.load(open("config/shared.json"))
P
cp services/billing.py services/shipping.py
echo '{"currency": "USD"}' > config/shared.json
cat > tests/test_cart.py <<'P'
import unittest
from app.cart import total
class T(unittest.TestCase):
    def test_total(self): self.assertEqual(total([{"price": 2, "qty": 3}]), 6)
    def test_empty(self): self.assertEqual(total([]), 1)  # failing on purpose
if __name__ == "__main__": unittest.main()
P
printf '# Guide\n\nInvoke the REST endpoint with an idempotent POST and a bearer token.\n' > docs/guide.md
printf '# API\n\nGET /items\n' > docs/api.md
printf '<html><body><h1>Acme</h1><p>Buy now! Limited offer!</p></body></html>\n' > docs/landing.html
printf '# TODO\n- [x] cart total\n- [ ] fix test_empty\n- [ ] discount codes\n' > TODO.md
printf '# Fixture\nTest: python3 -m unittest discover -s tests -t .\n' > CLAUDE.md
git add -A && git -c user.name=t -c user.email=t@t commit -qm init
