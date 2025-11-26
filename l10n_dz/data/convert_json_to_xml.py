#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de conversion des fichiers JSON du plan comptable algérien vers XML Odoo 19
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_xml_header():
    """Créer l'en-tête XML Odoo"""
    root = ET.Element('odoo')
    data = ET.SubElement(root, 'data', {'noupdate': '1'})
    return root, data

def prettify_xml(elem):
    """Formater le XML de manière lisible"""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def clean_xml_id(prefix, id_val, code=None):
    """Créer un XML ID propre et unique"""
    if code:
        # Nettoyer le code pour le XML ID
        clean_code = str(code).replace(' ', '_').replace('-', '_').replace('à', 'a')
        return f"{prefix}_{clean_code}"
    return f"{prefix}_{id_val}"

def convert_account_groups():
    """Convertir account_group.json vers XML"""
    print("Conversion des groupes de comptes...")

    with open('account_group.json', 'r', encoding='utf-8') as f:
        groups = json.load(f)

    root, data = create_xml_header()

    # Créer un mapping id -> xml_id pour résoudre les références parent
    id_to_xmlid = {}

    # Premier passage : créer les XML IDs
    for group in groups:
        code = group.get('code_prefix_start', '')
        xml_id = clean_xml_id('account_group', group['id'], code)
        id_to_xmlid[group['id']] = xml_id

    # Deuxième passage : créer les records
    for group in groups:
        xml_id = id_to_xmlid[group['id']]

        record = ET.SubElement(data, 'record', {
            'id': xml_id,
            'model': 'account.group'
        })

        # Nom
        name = group.get('name', '').strip()
        if name:
            ET.SubElement(record, 'field', {'name': 'name'}).text = name

        # Code prefix start
        code_start = group.get('code_prefix_start', '').strip()
        if code_start:
            ET.SubElement(record, 'field', {'name': 'code_prefix_start'}).text = code_start

        # Code prefix end
        code_end = group.get('code_prefix_end', '').strip()
        if code_end:
            ET.SubElement(record, 'field', {'name': 'code_prefix_end'}).text = code_end

        # Parent
        parent_id = group.get('parent_id')
        if parent_id and parent_id in id_to_xmlid:
            ET.SubElement(record, 'field', {
                'name': 'parent_id',
                'ref': id_to_xmlid[parent_id]
            })

    # Écrire le fichier XML
    xml_string = prettify_xml(root)
    with open('account_group_data.xml', 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f"✓ {len(groups)} groupes de comptes convertis -> account_group_data.xml")
    return id_to_xmlid

def convert_account_accounts(group_id_mapping):
    """Convertir account_account.json vers XML"""
    print("\nConversion des comptes...")

    with open('account_account.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    root, data = create_xml_header()

    # Mapping des types de comptes Odoo
    account_type_mapping = {
        'equity': 'equity',
        'asset_cash': 'asset_cash',
        'asset_receivable': 'asset_receivable',
        'asset_current': 'asset_current',
        'asset_non_current': 'asset_non_current',
        'asset_fixed': 'asset_fixed',
        'asset_prepayments': 'asset_prepayments',
        'liability_payable': 'liability_payable',
        'liability_credit_card': 'liability_credit_card',
        'liability_current': 'liability_current',
        'liability_non_current': 'liability_non_current',
        'income': 'income',
        'income_other': 'income_other',
        'expense': 'expense',
        'expense_depreciation': 'expense_depreciation',
        'expense_direct_cost': 'expense_direct_cost',
        'off_balance': 'off_balance'
    }

    for account in accounts:
        code = account.get('code', '').strip()
        if not code:
            continue

        xml_id = clean_xml_id('account_account', account['id'], code)

        record = ET.SubElement(data, 'record', {
            'id': xml_id,
            'model': 'account.account'
        })

        # Code
        ET.SubElement(record, 'field', {'name': 'code'}).text = code

        # Nom
        name = account.get('name', '').strip()
        if name:
            ET.SubElement(record, 'field', {'name': 'name'}).text = name

        # Type de compte
        account_type = account.get('account_type', 'equity')
        account_type = account_type_mapping.get(account_type, account_type)
        ET.SubElement(record, 'field', {'name': 'account_type'}).text = account_type

        # Groupe parent
        group_id = account.get('group_id')
        if group_id and group_id in group_id_mapping:
            ET.SubElement(record, 'field', {
                'name': 'group_id',
                'ref': group_id_mapping[group_id]
            })

        # Reconcile
        reconcile = account.get('reconcile')
        if reconcile is not None:
            ET.SubElement(record, 'field', {
                'name': 'reconcile',
                'eval': 'True' if reconcile else 'False'
            })

        # Deprecated
        deprecated = account.get('deprecated', False)
        if deprecated:
            ET.SubElement(record, 'field', {
                'name': 'deprecated',
                'eval': 'True'
            })

        # Note
        note = account.get('note')
        if note:
            ET.SubElement(record, 'field', {'name': 'note'}).text = note

    # Écrire le fichier XML
    xml_string = prettify_xml(root)
    with open('account_account_data.xml', 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f"✓ {len(accounts)} comptes convertis -> account_account_data.xml")

def main():
    """Fonction principale"""
    print("="*60)
    print("Conversion du Plan Comptable Algérien - JSON vers XML Odoo 19")
    print("="*60)

    # Conversion des groupes
    group_id_mapping = convert_account_groups()

    # Conversion des comptes
    convert_account_accounts(group_id_mapping)

    print("\n" + "="*60)
    print("✓ Conversion terminée avec succès!")
    print("="*60)
    print("\nFichiers générés:")
    print("  - account_group_data.xml")
    print("  - account_account_data.xml")
    print("\nN'oubliez pas de mettre à jour __manifest__.py pour inclure ces fichiers.")

if __name__ == '__main__':
    main()
