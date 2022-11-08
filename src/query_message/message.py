# Author: Gabriela Cunha
# Created at: 30/10/22
# Last update: 03/11/22
# Description: PDU of a query: Header, Data

def build_message(name, type, flag):
    message = "1," + flag + ",0,0,0,0;" + name + "," + type + ";"

    return message

def parse_message(message):
    fields = message.split(";")
    header_fields = fields[0].split(",")
    data_fields = fields[1].split(",")

    message_id = header_fields[0]
    flags = header_fields[1]
    name = data_fields[0]
    type = data_fields[1]

    return (message_id, flags, name, type)

def build_query_db_version_response(message, value):
    (message_id, flags, name, type) = parse_message(message)

    response = ""
    response += message_id + "," + "V+A" + ",0,0,0,0;" + str(value) + "," + str(type) + ";"

    return response

def build_query_init_transfer_response(message, entries):
    (message_id, flags, name, type) = parse_message(message)

    response = ""
    response += message_id + "," + "T+A" + ",0,0,0,0;" + str(name) + "," + str(entries) + ";" #nr entries no type, MUDAR

    return response

def build_query_response(message, response_values, authorities_values, extra_values):
    (message_id, flags, name, type) = parse_message(message)

    message_response = ""
    num_values = len(response_values)
    num_authorities = len(authorities_values)
    num_extra = len(extra_values)

    if flags == "Q+R":
        flags_response = "R+A" #A sempre ?
    else:
        flags_response = "A"

    message_response += message_id + "," + flags_response + ",0" + "," + str(num_values) + "," + str(num_authorities) + "," + str(num_extra) + ";" + name + "," + type + ";"

    for record in response_values:
        message_response += name + " " + type + " " + record.value + " " + str(record.ttl) + " " + str(record.priority) + ","

    message_response = message_response[:-1] + ";"

    for record in authorities_values:
        message_response += name + " " + "NS" + " " + record.value + " " + str(record.ttl) + " " + str(record.priority) + ","

    message_response = message_response[:-1] + ";"

    for record in extra_values:
        message_response += record.name + " " + "A" + " " + record.value + " " + str(record.ttl) + " " + str(record.priority) + ","

    message_response = message_response[:-1] + ";"

    return message_response

