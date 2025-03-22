# # Reading the uploaded file and cleaning the Google-specific prefix
# file_path = 'responses/ugcposts_1742678271.json'

# with open(file_path, 'r', encoding='utf-8') as file:
#     data = file.read()

# # Removing the Google prefix ")]}'\n"
# clean_data = data.lstrip(")]}'\n")

# # Attempting to parse the cleaned data as JSON
# import json

# try:
#     parsed_data = json.loads(clean_data)
#     result = "JSON parsed successfully"
# except json.JSONDecodeError as e:
#     parsed_data = None
#     result = f"JSON parsing failed: {e}"

# # store result in a file
# with open('result.json', 'w', encoding='utf-8') as file:
#     json.dump(parsed_data, file, ensure_ascii=False, indent=4)

# result

# Reading the uploaded file
import json
file_path = 'responses/ugcposts_1742678271.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = file.read()

# Removing the Google prefix ")]}'\n"
clean_data = data.lstrip(")]}'\n")

# Attempting to parse the cleaned data as JSON
try:
    parsed_data = json.loads(clean_data)
    result = "JSON parsed successfully"
except json.JSONDecodeError as e:
    parsed_data = None
    result = f"JSON parsing failed: {e}"

with open('results.json', 'w', encoding='utf-8') as file:
    json.dump(parsed_data, file, ensure_ascii=False, indent=4)

result
