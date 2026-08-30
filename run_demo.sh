#!/bin/bash
# Praxis Demo Launcher
# Kills any existing Streamlit on 8502, seeds memory, starts the app.

set -e

echo "🧠 Praxis — Accenture Innovation Challenge 2026"
echo "   Team: Worst Pace Scenario"
echo ""

# Kill any process holding port 8502
echo "⏹  Clearing port 8502..."
lsof -ti:8502 | xargs kill -9 2>/dev/null || true
sleep 1

# Ensure data dir exists
mkdir -p data

# Reset the demo database so memory is clean for a fresh demo
echo "🗄  Resetting demo database..."
python3 -c "
import os
os.environ['PRAXIS_DB_PATH'] = 'data/praxis.duckdb'
import praxis.c5_memory.gateway as gw
import duckdb, shutil
try:
    conn = duckdb.connect('data/praxis.duckdb')
    conn.execute('DROP TABLE IF EXISTS decision_memory')
    conn.execute('DROP TABLE IF EXISTS outcome_memory')
    conn.execute('DROP TABLE IF EXISTS lineage_registry')
    conn.close()
    print('   Tables cleared.')
except:
    pass
"

# Seed Decision 1 memory fixture
echo "🌱 Seeding Decision 1 memory fixture..."
python3 -c "
import os
os.environ['PRAXIS_DB_PATH'] = 'data/praxis.duckdb'
from praxis.synthetic.seed_memory import seed_decision1_memory
result = seed_decision1_memory(verbose=True)
" 2>&1 | grep -E "(Seed|DM ID|OM ID|ADMITTED|QUARANTINED|REJECTED)"

echo ""
echo "✅ Demo ready. Opening Streamlit at http://localhost:8502"
echo "   Click ▶ Run Signature Demo to see Decision 1 vs Decision 3."
echo ""

# Launch Streamlit
python3 -m streamlit run ui/streamlit_app.py \
    --server.port 8502 \
    --server.headless false \
    --browser.gatherUsageStats false
