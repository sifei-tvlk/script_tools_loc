import pandas as pd
import re

suffix_jp = [
    "県",
    "市",
    "郡",
    "町",
    "島",
    "区",
    "村"
]

# Load the CSV file
df = pd.read_csv('bracket_check_jp.csv')

# Filter out rows where is-remove is TRUE
df = df[df['is-remove'] != True]

# Function to extract alias from local_name
def extract_alias(name, synonym):
    # Match both half-width () and full-width （）
    match = re.search(r'^(.*?)\s*[\(（](.*?)[\)）]', str(name))
    if not match:
        return None
    if synonym:
        alias = [match.group(1).strip(), match.group(2).strip()]
    else:
        alias = [match.group(1).strip()]
    to_extend = []
    for i, a in enumerate(alias):
        for suffix in suffix_jp:
            if a.endswith(suffix):
                to_extend.append(a[:-len(suffix)])
                break
    alias.extend(to_extend)
    return alias

# Apply alias extraction where is-synonym is TRUE
df['alias'] = df.apply(
    lambda row: extract_alias(row['local-name'], row['is-synonym']),
    axis=1
)

# Export to a new CSV file
df.to_csv('bracket_check_jp_alias.csv', index=False)
print("Processed file saved as: bracket_check_jp_alias.csv")