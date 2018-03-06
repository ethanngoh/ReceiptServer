import json
import os

from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('purchase_time_ms', type=int, required=True)
parser.add_argument('sales_tax_amt', type=float, required=True)
parser.add_argument('description', type=float, required=False)
args = parser.parse_args()

app = Flask(__name__)
api = Api(app)

PORT_NUMBER = 8942
CONFIG_FILE = "config.json"
EXPECTED_CSV_HEADER = "purchase_time_ms,sales_tax_amt,image_filename,description"

class ReceiptController(Resource):

    def __init__(self):
        config = json.loads(CONFIG_FILE)
        self.image_store_folder_path = config['image_store_folder_path']
        self._ensure_folder_exists(self.image_store_folder_path)
        self.sales_tax_store_folder_path = config['sales_tax_store_folder_path']        
        self._ensure_folder_exists(self.sales_tax_store_folder_path)

        self.sales_tax_filename = config['sales_tax_filename']
        self._validate_sales_tax_file(self.sales_tax_filename)

        with open(self.config['html_path'], 'r') as f:
            self.html = f.read()

    def _ensure_folder_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def _validate_sales_tax_file(self, filename):
        with open(filename, 'r+') as f:
            first_line = f.readline()
            if first_line.strip() != EXPECTED_CSV_HEADER:
                # Append header if its messed up.
                content = f.read()
                f.seek(0,0)
                f.writeline(EXPECTED_CSV_HEADER + '\n' + content)

    def _write_entry_to_sales_tax_file(self, purchase_time_ms, sales_tax_amt, image_filename, description):
        with open(filename, 'a') as f:
            a.write('{},{},{},{}'.format(purchase_time_ms, sales_tax_amt, image_filename, description))

    def get(self):
        return self.html

    def post(self):
        args = parser.parse_args()

        try:
            # save image file to disk
            files = request.files.getlist("files")
            f = files[0]
            filename = f.filename
            target_path = os.path.join(self.image_store_folder_path, filename)
            f.save(target_path)
            f.close()

            # store data in row
            self._write_entry_to_sales_tax_file(args.purchase_time_ms, args.sales_tax_amt, args.image_filename, args.get('description', ""))
        except:
            return {"result": "failure"}

        return {"result": "success"}

api.add_resource(ReceiptController, '/')

if __name__ == '__main__':
    app.run(port=PORT_NUMBER)