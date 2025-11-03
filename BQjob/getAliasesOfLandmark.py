import pandas as pd
from tqdm import tqdm
import json
import os
from datetime import datetime

from LocgiApi import LandmarkDataService, LLMService
from UserUtils import UserInput


def log_message(message, level="INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def create_llm_prompt(landmark_name, aliases_str):
    """Create the LLM prompt for filtering aliases"""
    return f"""You are a linguistic expert and an avid traveller. As a traveller, you know the names of places and landmarks around the world. As a linguistic expert, you understand how people type or refer to location names using aliases.
You are working for an online travel agent (OTA) that maintains aliases for a given location. However, the sourcing is outdated, and the aliases are dirty and not separated by country.
The company currently operates in the following languages:

 Bahasa Indonesia


 English


 Thai


 Malay


 Vietnamese


 Japanese


 Korean


 Simplified Chinese


 Traditional Chinese


There is also a global audience, which represents the common way an international traveller would type or say the location name.
You will be given the actual landmark or location name and a list of aliases for that geo. Your task is to filter and return only the valid aliases for the above languages.
Important Instructions

 No ambiguity: Do not allow aliases that might be ambiguous (e.g., "CA" could mean "California" or "Canada").

 Proper form only: Typos and mispronunciations are not allowed.

 Strict alias list: Only allow aliases from the provided list. Never create your own alias.


 Slang allowed: Common slang is allowed (e.g., "jkt" for Jakarta).

 No ISO codes: Country ISO codes or ISO-3166 codes are not allowed (e.g., "HK" for Hong Kong).

 No regional codes: State or regional codes are not allowed (e.g., "NJ" for New Jersey, "ON" for Ontario).

 No archaic forms: Only allow contemporary dialects. Do not allow archaic or outdated names (e.g., "Angora" for Ankara, "Stambul" for Istanbul).

 No local references: Do not allow internal/local shorthand unless it is widely used internationally in that language (e.g., "HH" for Hamburg should be excluded).

 Landmark consistency check:

 Verify that each alias logically and linguistically makes sense with the actual landmark name provided.

 Reject aliases that refer to something else, another nearby location, or a different entity type (e.g., if the landmark is "Eiffel Tower," exclude aliases like "Paris" or "France").

 Accept only aliases that correctly refer to the same specific place or landmark, not its broader region or city unless commonly interchangeable.




Input format:

 Location Name: {landmark_name}


 Aliases: {aliases_str if aliases_str else "No aliases provided - please suggest appropriate aliases for this location in the supported languages"}

CRITICAL OUTPUT REQUIREMENTS:
- Output ONLY a valid JSON array of strings containing the filtered aliases
- Do NOT include any explanations, comments, or additional text
- Do NOT include any markdown formatting
- Do NOT include any code blocks or backticks
- The output must be parseable as a JSON array
- Example format: ["alias1","alias2","alias3"]
- If no valid aliases are found, return an empty array: []"""

def save_batch_results(results, batch_num, total_processed, output_filename):
    """Save results in batches to the same file"""
    if not results:
        return
    
    result_df = pd.DataFrame(results)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(output_filename)

    # Append to the same file
    result_df.to_csv(output_filename, mode='a', header=not file_exists, index=False)
    log_message(f"Batch {batch_num} saved: {len(results)} landmarks appended to {output_filename}")
    log_message(f"Total processed so far: {total_processed} landmarks")

def main():
    # Choose environment
    env = 'production'
    locgi_url = UserInput.get_locgi_url(env)
    
    # Read the CSV file
    df = pd.read_csv("withLandmarkId.csv")
    
    results = []
    batch_size = 100
    batch_num = 1
    total_processed = 0
    total_errors = 0
    output_filename = "filtered_aliases_result.csv"
    
    log_message(f"Starting processing of {len(df)} landmarks")
    log_message(f"Batch size: {batch_size}")
    log_message(f"Environment: {env}")
    log_message(f"Output file: {output_filename}")
    
    # Remove existing output file if it exists
    if os.path.exists(output_filename):
        os.remove(output_filename)
        log_message(f"Removed existing output file: {output_filename}")
    
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Processing landmarks"):
        landmark_id = row.get('landmarkId')
        landmark_name = row.get('name')
        
        if pd.isna(landmark_id) or not landmark_id:
            log_message(f"Skipping row {i}: No landmarkId", "WARNING")
            continue
            
        try:
            landmark = LandmarkDataService.get_landmark_by_id(landmark_id, locgi_url)
            
            if not landmark:
                log_message(f"No landmark data found for ID: {landmark_id}", "WARNING")
                total_errors += 1
                continue
                
            landmark_name = landmark.get('name', landmark_name)
            aliases = landmark.get('aliases', [])
            
            # Format aliases as comma-separated string (even if empty)
            aliases_str = ', '.join(aliases) if isinstance(aliases, list) and aliases else str(aliases) if aliases else ""
            
            log_message(f"Processing landmark: {landmark_name} (ID: {landmark_id})")
            
            # Create the LLM prompt
            prompt = create_llm_prompt(landmark_name, aliases_str)
            
            llm_result = LLMService.ask_llm_with_prompt(prompt, locgi_url)
            
            if llm_result:
                # Store LLM result as string without JSON parsing
                result = {
                    'landmarkId': landmark_id,
                    'name': landmark_name,
                    'original_aliases': aliases if aliases else [],
                    'filtered_aliases': llm_result,  # Store as string
                    'processed_at': datetime.now().isoformat(),
                    'batch_number': batch_num
                }
                results.append(result)
                total_processed += 1
                
                log_message(f"Successfully processed landmark: {landmark_name}")
                log_message(f"LLM output: {llm_result}")
                
                # Save batch when reaching batch size
                if len(results) >= batch_size:
                    save_batch_results(results, batch_num, total_processed, output_filename)
                    results = []  # Reset for next batch
                    batch_num += 1
            else:
                log_message(f"No LLM result for landmark: {landmark_name}", "ERROR")
                total_errors += 1
                continue
                
        except Exception as e:
            log_message(f"Error processing landmark {landmark_id}: {str(e)}", "ERROR")
            total_errors += 1
            continue
    
    # Save remaining results
    if results:
        save_batch_results(results, batch_num, total_processed, output_filename)
    
    # Final summary
    log_message(f"Processing completed!")
    log_message(f"Total landmarks processed: {total_processed}")
    log_message(f"Total errors: {total_errors}")
    log_message(f"Total batches created: {batch_num}")
    
    # Create a summary file
    summary = {
        'total_landmarks_in_input': len(df),
        'total_processed': total_processed,
        'total_errors': total_errors,
        'total_batches': batch_num,
        'batch_size': batch_size,
        'environment': env,
        'output_file': output_filename,
        'processed_at': datetime.now().isoformat()
    }
    
    with open("processing_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    log_message(f"Summary saved to processing_summary.json")
    log_message(f"All results saved to: {output_filename}")

if __name__ == "__main__":
    main()

