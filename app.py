from flask import Flask, render_template, request, send_file
import pandas as pd
import urllib.parse

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if request.method == 'POST':
        print("Processing POST request to /process route...")

        # Handle file upload
        if 'file' in request.files and request.files['file'].filename != '':
            print("File detected in request...")
            file = request.files['file']
            # Read the CSV file
            try:
                df = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                print("Empty or invalid file. Returning error message.")
                return render_template('index.html', error_message='Empty or invalid file. Please upload a valid CSV file.')
        # Handle manual text input
        else:
            print("No file detected in request. Parsing manual input...")
            data = request.form['text_input']
            print("Manual input data:", data)  # Print manual input data
            # Check if data is empty or only whitespace
            if not data.strip():
                print("No data entered. Returning error message.")
                return render_template('index.html', error_message='No data entered. Please provide data manually or upload a CSV file.')
            # Parse text input as CSV-like data
            data = data.strip().split('\n')
            data = [line.split(',', 1) for line in data]

            # Convert to DataFrame if data is not empty
            if data:
                df = pd.DataFrame(data, columns=['Name', 'Address'])
            else:
                print("Invalid input format. Returning error message.")
                return render_template('index.html', error_message='Invalid input. Please enter data in a valid format.')
        
        # Group people by identical addresses and sort names
        grouped = df.groupby('Address')['Name'].apply(lambda x: sorted(x)).sort_index()

        # Generate output data including both names and addresses
        results = []
        for address, names in grouped.items():
            results.append({'names': ', '.join(names), 'address': address})

        # Debugging: Print results
        print("Results:", results)

        # Verify data before rendering template
        if not results:
            print("No results to display. Returning error message.")
            return render_template('index.html', error_message='No results to display. Please check your input data.')

        print("Rendering results template...")
        return render_template('results.html', results=results)


@app.route('/download')
def download():
    address_names = request.args.lists()

    # Initialize lists to store names and addresses
    names_list = []
    addresses_list = []

    for address, names in address_names:
        # Convert names and addresses to plain text
        names_text = '\n'.join(urllib.parse.unquote(name) for name in names)
        address_text = urllib.parse.unquote(address)
        
        # Append to lists
        names_list.append(names_text)
        addresses_list.append(address_text)

    # Join lists into strings with each item on a new line
    names_text = '\n'.join(names_list)
    addresses_text = '\n'.join(addresses_list)

    # Generate tabular format for download
    output = f"Name\tAddress\n{names_text}\t{addresses_text}"

    output_file = 'output.txt'
    with open(output_file, 'w') as f:
        f.write(output)

    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
