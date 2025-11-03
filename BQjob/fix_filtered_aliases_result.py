import re
from pathlib import Path
import csv
import json
import ast


def fix_file(input_path: Path, output_path: Path) -> None:
    # Read raw text
    raw = input_path.read_text(encoding="utf-8")

    # 1) Remove accidental markdown code fences that were injected into the CSV
    #    Forms observed: ```json\n ... \n``` living inside a quoted cell
    cleaned = raw.replace("```json\n", "").replace("\n```", "")

    # 2) Collapse broken empty-array cells caused by a newline before the closing quote
    #    Observed pattern: "[]\n" (still inside the same quoted cell)
    cleaned = cleaned.replace('\"[]\n', '\"[]')

    # 3) As a slightly more general safeguard, collapse any single newline that occurs
    #    immediately before a closing quote within a quoted cell of the row.
    #    This targets cases like "[...some content...]\n" -> "[...some content...]"
    #    but avoids touching legitimate row separators. We only do this when the newline
    #    is followed by a \" then a comma or end of line.
    cleaned = re.sub(r"\n(?=\"(?:,|\r?$))", "", cleaned)

    # Write a temporary cleaned CSV text so we can validate with csv module
    temp_path = output_path.with_suffix(".tmp.csv")
    temp_path.write_text(cleaned, encoding="utf-8")

    # 4) Validate and re-emit via csv reader/writer to ensure well-formed CSV
    #    We expect header: landmarkId,name,original_aliases,filtered_aliases,processed_at,batch_number
    with temp_path.open("r", encoding="utf-8", newline="") as f_in, \
         output_path.open("w", encoding="utf-8", newline="") as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        row_num = 0
        fixed_rows = 0
        # Prepare additional outputs: JSONL and TSV without quote-doubling
        jsonl_path = output_path.with_suffix("")
        jsonl_path = jsonl_path.with_name(jsonl_path.name + "_records.jsonl")
        tsv_path = output_path.with_suffix(".tsv")

        jsonl_f = jsonl_path.open("w", encoding="utf-8")
        tsv_f = tsv_path.open("w", encoding="utf-8", newline="")
        tsv_writer = csv.writer(tsv_f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')

        for row in reader:
            row_num += 1
            # Try to coerce rows to expected length (6). If not, try a simple join heuristic.
            if len(row) == 0:
                continue

            if row_num == 1:
                # Write header as-is
                writer.writerow(row)
                # Also write TSV header
                tsv_writer.writerow(row)
                continue

            if len(row) > 6:
                # If split due to stray commas inside an unquoted field, try to merge extras into filtered_aliases
                # Heuristic: we know filtered_aliases is the 4th column (index 3). Merge tail back until length == 6.
                # Join using comma to preserve content.
                while len(row) > 6:
                    # Prefer merging into column 3 if it looks like part of JSON/text
                    if len(row) >= 5:
                        row[3] = row[3] + "," + row.pop(4)
                    else:
                        # Fallback: merge last two columns
                        row[-2] = row[-2] + "," + row.pop(-1)
                fixed_rows += 1

            if len(row) < 6:
                # Try to pad by merging trailing items from next positions is not feasible here; we just write as-is.
                # It's safer to skip or write with placeholders. We'll write with empty placeholders to reach 6.
                row = row + [""] * (6 - len(row))
                fixed_rows += 1

            # Normalize doubled quotes inside JSON-like columns: original_aliases (idx 2), filtered_aliases (idx 3)
            def normalize_json_like(cell: str) -> str:
                # Only touch when it looks like a JSON array with possible doubled quotes
                if cell.startswith("[") and cell.endswith("]"):
                    return cell.replace('""', '"')
                return cell

            if len(row) >= 4:
                row[2] = normalize_json_like(row[2])
                row[3] = normalize_json_like(row[3])

            writer.writerow(row)
            # Write TSV row too
            tsv_writer.writerow(row)

            # Emit JSONL: parse the alias columns into proper arrays
            def parse_original_aliases(text: str):
                text = text.strip()
                if not text or text == '[]':
                    return []
                # Try JSON first
                try:
                    return json.loads(text)
                except Exception:
                    pass
                # Try Python literal (handles single quotes)
                try:
                    val = ast.literal_eval(text)
                    if isinstance(val, list):
                        return val
                except Exception:
                    pass
                return []

            def parse_filtered_aliases(text: str):
                text = text.strip()
                if not text or text == '[]':
                    return []
                try:
                    return json.loads(text)
                except Exception:
                    # try to repair common doubling
                    try:
                        return json.loads(text.replace('""', '"'))
                    except Exception:
                        return []

            try:
                record = {
                    "landmarkId": row[0],
                    "name": row[1],
                    "original_aliases": parse_original_aliases(row[2]) if len(row) > 2 else [],
                    "filtered_aliases": parse_filtered_aliases(row[3]) if len(row) > 3 else [],
                    "processed_at": row[4] if len(row) > 4 else None,
                    "batch_number": row[5] if len(row) > 5 else None,
                }
                jsonl_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception:
                # Skip malformed record in JSONL
                pass

        jsonl_f.close()
        tsv_f.close()

    # Remove temp
    try:
        temp_path.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    input_csv = base / "filtered_aliases_result.csv"
    output_csv = base / "filtered_aliases_result_fixed.csv"

    fix_file(input_csv, output_csv)
    print(f"Wrote fixed CSV to: {output_csv}")
    print(f"Also wrote JSONL to: {output_csv.with_suffix('').with_name(output_csv.stem + '_records.jsonl')}")
    print(f"Also wrote TSV (no doubled quotes) to: {output_csv.with_suffix('.tsv')}")


