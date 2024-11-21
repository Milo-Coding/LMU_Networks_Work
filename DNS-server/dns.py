import socket
import glob
import json

PORT = 53
IP = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

def load_zones():
    json_zone = {}
    zone_files = glob.glob('zones/*.zone')

    for zone in zone_files:
        with open(zone) as zone_data:
            data = json.load(zone_data)
            zone_name = data["$origin"]
            json_zone[zone_name] = data
    
    return json_zone

zone_data = load_zones()

# get the flags for the dns response
def get_flags(flags):
    # QR: Response (1 bit)
    QR = '1'

    # Opcode: Standard Query (0000)
    opcode = '0000'

    # Authoritative Answer (1 bit)
    AA = '1'

    # Truncated (0 bit)
    TC = '0'

    # Recursion Desired (1 bit)
    RD = '0'

    # Recursion Available, Zero bits, and RCODE
    RA = '0'
    Z = '000'
    RCODE = '0000'

    return int(QR + opcode + AA + TC + RD, 2).to_bytes(1, byteorder='big') + \
           int(RA + Z + RCODE, 2).to_bytes(1, byteorder='big')

# get question domain for get_recs
def get_question_domain(data):
    state = 0
    expected_length = 0
    domain_string = ''
    domain_parts = []
    x = 0
    y = 0

    for byte in data:
        if state == 1:
            if byte != 0:
                domain_string += chr(byte)

            x += 1

            # add characters to the parts of the domain
            if x == expected_length:
                domain_parts.append(domain_string)
                domain_string = ''
                state = 0
                x = 0
            
            # end of string character
            if byte == 0:
                domain_parts.append(domain_string)
                break
        
        else:
            state = 1
            expected_length = byte

        y += 1

    question_type = data[y:y+2]
    
    return(domain_parts, question_type)

# get the zone for get_recs
def get_zone(domain):
    global zone_data

    zone_name = '.'.join(domain)

    return zone_data[zone_name]

# get the record for the dns response
def get_recs(data):
    domain, question_type = get_question_domain(data)

    if question_type == b'\x00\x01':
        qt = 'a'
    
    zone = get_zone(domain)

    return (zone[qt], qt, domain)

# build the question for the dns response
def build_question(domain_name, rec_type):
    q_bytes = b''
    for part in domain_name:
        length = len(part)
        q_bytes += bytes([length])  # Append length
        for char in part:
            q_bytes += ord(char).to_bytes(1, byteorder='big')  # Append character bytes

    if rec_type == 'a':
        q_bytes += (1).to_bytes(2, byteorder='big')  # QTYPE A
    q_bytes += (1).to_bytes(2, byteorder='big')  # QCLASS IN

    return q_bytes

# convert record to bytes
def rectobytes(domain_name, rec_type, rec_ttl, rec_value):
    response = b'\xc0\x0c'

    if rec_type == 'a':
        response = response + bytes([0]) + bytes([1])

    response = response + bytes([0]) + bytes([1])

    response += int(rec_ttl).to_bytes(4, byteorder='big')

    if rec_type == 'a':
        response = response + bytes([0]) + bytes([4])

        for part in rec_value.split('.'):
            response += bytes([int(part)])
    
    return response

# create a DNS response for the server to return
def build_response(data):
    transaction_id = data[:2]
    flags = get_flags(data[2:4])
    Q_COUNT = (1).to_bytes(2, byteorder='big')  # Correct question count
    records, rec_type, domain_name = get_recs(data[12:])
    an_count = len(records).to_bytes(2, byteorder='big')  # Correct answer count

    NS_COUNT = (0).to_bytes(2, byteorder='big')  # No name servers
    AR_COUNT = (0).to_bytes(2, byteorder='big')  # No additional records

    dns_header = transaction_id + flags + Q_COUNT + an_count + NS_COUNT + AR_COUNT
    dns_question = build_question(domain_name, rec_type)

    dns_body = b''
    for record in records:
        dns_body += rectobytes(domain_name, rec_type, record['ttl'], record['value'])

    return dns_header + dns_question + dns_body

# listen for requests as long as the server is running
while True:
    data, addr = sock.recvfrom(512)
    r = build_response(data)
    sock.sendto(r, addr)
