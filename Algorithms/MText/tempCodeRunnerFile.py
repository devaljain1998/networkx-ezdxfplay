# Saving the file:
try:
    dwg.saveas(output_file_path + output_file)
    print(f'Success in saving file: {output_file_path + output_file}')
except Exception as e:
    print(f'Failed to save the file due to the following exception: {e}')
    sys.exit(1)