import json
import os

from datetime import datetime
from flask import Flask, request, render_template, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('sales_tax_amt', type=float, required=True)
parser.add_argument('description', type=str, required=False)

app = Flask(__name__)
api = Api(app)

PORT_NUMBER = 8942
CONFIG_FILE = "config.json"
EXPECTED_CSV_HEADER = "purchase_date,sales_tax_amt,image_filename,description"

class ReceiptController(Resource):

    def __init__(self):
        config = json.load(open(CONFIG_FILE))
        self.image_store_folder_path = config['image_store_folder_path']
        self._ensure_folder_exists(self.image_store_folder_path)
        self.sales_tax_store_folder_path = config['sales_tax_store_folder_path']        
        self._ensure_folder_exists(self.sales_tax_store_folder_path)

        sales_tax_filename = config['sales_tax_filename']
        self.sales_tax_full_path = os.path.join(self.sales_tax_store_folder_path, sales_tax_filename)
        self._validate_sales_tax_file(self.sales_tax_full_path)
        self.html_path = config['html_path']

    def _ensure_folder_exists(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def _validate_sales_tax_file(self, filename):
        try:
            with open(filename, 'r+') as f:
                first_line = f.readline()
                if first_line.strip() != EXPECTED_CSV_HEADER:
                    # Append header if its messed up.
                    content = f.read()
                    f.seek(0,0)
                    f.write(EXPECTED_CSV_HEADER + '\n' + content)
        except IOError:
            with open(filename, 'w') as f:
                f.write(EXPECTED_CSV_HEADER + '\n')


    def _write_entry_to_sales_tax_file(self, purchase_date, sales_tax_amt, image_filename, description):
        with open(self.sales_tax_full_path, 'a') as f:
            f.write('{},{},{},{}'.format(purchase_date.strftime("%Y-%m-%d %H:%M:%S"), sales_tax_amt, image_filename, description))

    def get(self):
        resp = make_response(render_template(self.html_path))
        resp.headers['Content-type'] = 'text/html; charset=utf-8'
        return resp

    def post(self):
        args = parser.parse_args()

        try:
            # save image file to disk
            files = request.files.getlist("file")

            f = files[0]
            filename = f.filename
            target_path = os.path.join(self.image_store_folder_path, filename)
            f.save(target_path)
            f.close()

            purchase_date = datetime.now()

            # store data in row
            self._write_entry_to_sales_tax_file(purchase_date, args.sales_tax_amt, target_path, args.get('description', ""))
        except Exception as e:
            print e
            return {"result": "failure"}

        return {"result": "success"}

api.add_resource(ReceiptController, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_NUMBER)