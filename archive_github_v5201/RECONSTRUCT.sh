#!/bin/bash
# ═══════════════════════════════════════════════════
# BIONIC OS v5201 — SCRIPT DE RECONSTRUCTION
# Directive x5302/x5304 — Protocole BCE-4X
# Autorite : STEEVE-MAX
# ═══════════════════════════════════════════════════
# 
# USAGE:
#   1. Rassembler les parts fractionnees
#   2. Reconstruire les ZIP originaux
#   3. Extraire le code
#
# PREREQUIS:
#   - Tous les fichiers .part_* dans le meme repertoire
#   - unzip installe
# ═══════════════════════════════════════════════════

echo "═══ BIONIC OS v5201 — RECONSTRUCTION ═══"
echo ""

# Etape 1: Reconstruire ZIP #1 (Backup Complet)
echo "[1/4] Reconstruction BIONIC_OS_BACKUP_COMPLET_v5201.zip..."
cat BIONIC_OS_BACKUP_COMPLET_v5201.zip.part_* > BIONIC_OS_BACKUP_COMPLET_v5201.zip
echo "  OK — $(ls -lh BIONIC_OS_BACKUP_COMPLET_v5201.zip | awk '{print $5}')"

# Etape 2: Reconstruire ZIP #2 (7 Blocs)
echo "[2/4] Reconstruction BIONIC_OS_7BLOCS_v5201.zip..."
cat BIONIC_OS_7BLOCS_v5201.zip.part_* > BIONIC_OS_7BLOCS_v5201.zip
echo "  OK — $(ls -lh BIONIC_OS_7BLOCS_v5201.zip | awk '{print $5}')"

# Etape 3: Verification
echo "[3/4] Verification des ZIP..."
unzip -t BIONIC_OS_BACKUP_COMPLET_v5201.zip > /dev/null 2>&1 && echo "  Backup Complet: VALIDE" || echo "  Backup Complet: ERREUR"
unzip -t BIONIC_OS_7BLOCS_v5201.zip > /dev/null 2>&1 && echo "  7 Blocs: VALIDE" || echo "  7 Blocs: ERREUR"
unzip -t BIONIC_OS_MONGODB_DUMP_v5201.zip > /dev/null 2>&1 && echo "  MongoDB Dump: VALIDE" || echo "  MongoDB Dump: ERREUR"

# Etape 4: Instructions
echo "[4/4] Instructions d'extraction:"
echo "  unzip BIONIC_OS_BACKUP_COMPLET_v5201.zip -d /app/"
echo "  unzip BIONIC_OS_MONGODB_DUMP_v5201.zip -d /tmp/restore/"
echo ""
echo "═══ RECONSTRUCTION TERMINEE ═══"
