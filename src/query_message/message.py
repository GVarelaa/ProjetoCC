# Author: Gabriela Cunha
# Created at: 30/10/22
# Last update: 03/11/22
# Description: PDU of a query: Header, Data

def build_message(name, type_of_value, flag):
    if flag == None:
        flag = "Q+R"
    else:
        flag = "Q"

    message = "1," + flag + ",0,0,0,0;" + name + "," + type_of_value + ";"
    print(message)

    return message

def parse_message(message):
    fields = message.split(";")
    header_fields = fields[0].split(",")
    data_fields = fields[1].split(",")

    message_id = header_fields[0]
    flags = header_fields[1]
    name = data_fields[0]
    type_of_value = data_fields[1]

    return (message_id, flags, name, type_of_value)

def build_query_response(message, response_values, authorities_values, extra_values):
    (message_id, flags, name, type_of_value) = parse_message(message)

    message_response = ""
    num_values = len(response_values)
    num_authorities = len(authorities_values)
    num_extra = len(extra_values)

    if flags == "Q+R":
        flags_response = "R+A" #A sempre ?
    else:
        flags_response = "A"

    message_response += message_id + "," + flags_response + ",0" + "," + str(num_values) + "," + str(num_authorities) + "," + str(num_extra) + ";" + name + "," + type_of_value + ";"

    for (value, ttl, priority) in response_values:
        message_response += name + " " + type_of_value + " " + str(value) + " " + str(ttl) + " " + str(priority) + ","

    message_response = message_response[:-1] + ";"

    for (value, ttl, priority) in authorities_values:
        message_response += name + " " + "NS" + " " + str(value) + " " + str(ttl) + " " + str(priority) + ","

    message_response = message_response[:-1] + ";"

    for (name, type_of_value, value, ttl, priority) in extra_values:
        message_response += name + " " + type_of_value + " " + str(value) + " " + str(ttl) + " " + str(priority) + ","

    message_response = message_response[:-1] + ";"

    return message_response

