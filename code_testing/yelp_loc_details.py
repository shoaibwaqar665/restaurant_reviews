import subprocess

def execute_bash_script(restaurant_slug):
    # Define the bash script file path
    bash_script = './run_curl.sh'

    # Run the bash script with the restaurant_slug argument
    result = subprocess.run([bash_script, restaurant_slug], capture_output=True, text=True)

    # Print the output and error (if any)
    if result.returncode == 0:
        print("Script executed successfully!")
        print("Output:", result.stdout)
    else:
        print("Error executing the script.")
        print("Error:", result.stderr)

# Pass the restaurant slug as an argument
restaurant_slug = 'shakeys-pizza-parlor-burbank'
execute_bash_script(restaurant_slug)
