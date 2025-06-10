import json
import os
import argparse
import ijson # You may need to install this: pip install ijson
from typing import Set, Dict, Callable, Any, Iterator

# Type hint for our extraction functions
ExtractorFunc = Callable[[Iterator[Any], Set[str]], None]

def extract_from_computers(item_iterator: Iterator[Any], wordlist: Set[str]):
    """Extracts computer-related names, filtering null/empty values at the source."""
    for computer in item_iterator:
        properties = computer.get('Properties', {})
        
        sam_name = properties.get('samaccountname')
        if sam_name: # Check ensures value is not None or empty
            wordlist.add(sam_name.replace('$', ''))

        name = properties.get('name')
        if name: # Check ensures value is not None or empty
            wordlist.add(name.split('.')[0])
        
        spns = properties.get('serviceprincipalnames')
        if spns: # Check ensures list is not None or empty
            # Filter out any potential empty strings within the list itself
            wordlist.update(spn for spn in spns if spn)

def extract_from_users(item_iterator: Iterator[Any], wordlist: Set[str]):
    """Extracts user-related names, filtering null/empty values at the source."""
    for user in item_iterator:
        properties = user.get('Properties', {})

        sam_name = properties.get('samaccountname')
        if sam_name:
            wordlist.add(sam_name)

        name = properties.get('name')
        if name:
            wordlist.add(name.split('@')[0])
            
        spns = properties.get('serviceprincipalnames')
        if spns:
            wordlist.update(spn for spn in spns if spn)

def extract_from_groups(item_iterator: Iterator[Any], wordlist: Set[str]):
    """Extracts group names, filtering null/empty values at the source."""
    for group in item_iterator:
        properties = group.get('Properties', {})
        name = properties.get('name')
        if name:
            wordlist.add(name.split('@')[0])

def extract_from_domains(item_iterator: Iterator[Any], wordlist: Set[str]):
    """Extracts trust names, filtering null/empty values at the source."""
    for domain in item_iterator:
        trusts = domain.get('Trusts', [])
        for trust in trusts:
            target_name = trust.get('TargetDomainName')
            if target_name:
                wordlist.add(target_name)

def extract_generic_name_props(item_iterator: Iterator[Any], wordlist: Set[str]):
    """Extracts 'name' and 'displayname', filtering null/empty values at the source."""
    for item in item_iterator:
        properties = item.get('Properties', {})
        
        display_name = properties.get('displayname')
        if display_name:
            wordlist.add(display_name)
        
        name = properties.get('name')
        if name:
            if '@' in name:
                wordlist.add(name.split('@')[0])
            else:
                wordlist.add(name)

def main():
    """Main function to parse arguments and process files."""
    parser = argparse.ArgumentParser(
        description='''Extract attributes from Bloodhound JSON files into a wordlist.
                       This script ensures all entries are unique and filters out empty/null values.''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('folder_path', type=str, help='The path to the folder containing the Bloodhound JSON files.')
    parser.add_argument('-o', '--output', type=str, default='bloodhound_wordlist.txt', help='The path for the output wordlist file (default: bloodhound_wordlist.txt).')
    args = parser.parse_args()

    folder_path = args.folder_path
    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a valid directory.")
        return

    wordlist: Set[str] = set()

    # Map the 'meta.type' value from the JSON to the correct extractor function
    extractor_map: Dict[str, Callable[[Iterator[Any], Set[str]], None]] = {
        'computers': extract_from_computers,
        'users': extract_from_users,
        'groups': extract_from_groups,
        'domains': extract_from_domains,
        'ous': extract_generic_name_props,
        'containers': extract_generic_name_props,
        'gpos': extract_generic_name_props,
        'certtemplates': extract_generic_name_props,
        'templates': extract_generic_name_props,
        'aiacas': extract_generic_name_props,
        'rootcas': extract_generic_name_props,
        'enterprisecas': extract_generic_name_props,
        'cas': extract_generic_name_props,
        'issuancepolicies': extract_generic_name_props,
        'ntauthstores': extract_generic_name_props,
    }

    print("Starting extraction...")
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing {filename}...")
            try:
                with open(file_path, 'rb') as f:
                    meta_type_gen = ijson.items(f, 'meta.type')
                    meta_type = next(meta_type_gen, None)
                    
                    if meta_type and meta_type in extractor_map:
                        print(f"  -> Detected type: {meta_type}")
                        f.seek(0)
                        item_iterator = ijson.items(f, 'data.item')
                        extractor_map[meta_type](item_iterator, wordlist)
                    else:
                        print(f"  -> Warning: Skipping file. Unknown or unhandled meta.type: '{meta_type}'.")

            except Exception as e:
                print(f"  -> An error occurred processing {filename}: {e}")
    
    # The filtering of empty/null values is now done at the source, so a final cleanup is not needed.
    # The use of a 'set' automatically handles all duplicates.

    with open(args.output, 'w', encoding='utf-8') as f:
        # The list is sorted before writing to ensure the output file is consistent across runs.
        for item in sorted(list(wordlist)):
            f.write(f"{item}\n")

    print(f"\nExtraction complete. {len(wordlist)} unique items saved to '{args.output}'")

if __name__ == "__main__":
    main()s