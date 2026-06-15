#!/usr/bin/env bash
set -euo pipefail

EXPECTED_SHA="4b017248db110204ae80551d557ec324d48237dccff282f9254d85bae21d0ad3"

PATCH_URL="https://bionic-ultime-1.preview.emergentagent.com/api/r4-patch"
PATCH_FILE="/tmp/r4_completed_sentinel.patch"

echo "▸ 1/6  Download du patch ..."
curl -sfL "$PATCH_URL" -o "$PATCH_FILE"
ACTUAL_SHA=$(sha256sum "$PATCH_FILE" | cut -d' ' -f1)
if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
    echo "✗ SHA256 MISMATCH · attendu=$EXPECTED_SHA · actual=$ACTUAL_SHA"
    exit 1
fi
echo "  ✓ SHA256 vérifié : $EXPECTED_SHA"

echo "▸ 2/6  Synchro origin/conflict_080626_1045 ..."
git fetch origin conflict_080626_1045

echo "▸ 3/6  Création branche r4_completed_sentinel_merge depuis _1045 ..."
git checkout -B r4_completed_sentinel_merge origin/conflict_080626_1045

echo "▸ 4/6  Application du patch (git am) ..."
git -c user.email="${GIT_AUTHOR_EMAIL:-r4-merge@bionic.local}" \
    -c user.name="${GIT_AUTHOR_NAME:-R4 Cherry-Pick}" \
    am "$PATCH_FILE"
git log --oneline -1

echo "▸ 5/6  Validation tests ..."
cd backend
python3 -m pip install pytest pytest-asyncio --quiet 2>/dev/null || true
python3 -m pytest tests/test_worker_r4_completed_sentinel.py tests/test_worker_partial_recovery.py -q --tb=no
cd ..

echo "▸ 6/6  Push vers GitHub ..."
git push -u origin r4_completed_sentinel_merge

REPO_URL=$(git config --get remote.origin.url | sed -E 's#(git@github.com:|https://github.com/)([^.]+)(\.git)?#https://github.com/\2#')
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo " ✅ R4 PUSHED · PR READY"
echo "════════════════════════════════════════════════════════════════════════"
echo " Créer la PR : ${REPO_URL}/compare/conflict_080626_1045...r4_completed_sentinel_merge"
echo "════════════════════════════════════════════════════════════════════════"
