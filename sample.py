from flask import Flask, request, jsonify
import json

app = Flask(__name__)
@app.route('/receive_data', methods=['POST'])
def receive_data():
    try:
        data1 = request.json.get('ping_status')
        data2 = request.json.get('interface_status')
        data3 = request.json.get('layer_info')
        data1 = json.loads(data1)
        data2 = json.loads(data2)
        data3 = json.loads(data3)


        # Process the data as needed
        print(f"------------------------------------------------> JSON RECIEVED <---------------------------------------------------------------------------------------------\n\n")
        for i,j in data1.items():
            print(f"\nDevice {i} is {j}\n")

        for k,l in data2.items():
            print(f"\n\nThe device ---> {k}\n")
            print("Interface status\n")
            print("-------------------\n\n")
            for m,n in l.items():
                print(f"Interface  {m} ---> {n} \n")

        print('<------Starting Layer Info------->')
        for ip, det in data3.items():
            print(f"\n Print Layer2 & 3 information of --> {ip}\n")
            print('IFCONFIG output \n')
            print(det['ifconfig'])
            print("\nROUTE information\n")
            print(det['route'])
            print('\nARP information\n')
            print(det['arp'])




        print('-------------------------------------------------> Finished <-------------------------------------------------------------------------------------------------\n\n')



        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)