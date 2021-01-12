import os
import string
import unicodedata
from rest_framework.response import Response


valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 255

def key_alter(key_list):
    new_keylist = []
    for key in key_list:
        new_key = (key.replace("_", " ")).title()
        new_keylist.append(new_key)
    return new_keylist


def error_message(serializer):
    response = {}
    if isinstance(serializer.errors, list):
        invalid_parameter = (key_alter(list(serializer.errors[-1].keys())))
    else:
        invalid_parameter = (key_alter(list(serializer.errors.keys())))
    if len(invalid_parameter) == 1:
        response['message'] = "Following data is invalid or Missing! <br/> - {}".format(invalid_parameter[0])
    elif len(invalid_parameter) > 1:
        parameters = ""
        for value in invalid_parameter:
            parameters = parameters + ' - ' + value + ' <br/>'
        response['message'] = "Following data is invalid or Missing! <br/>{}".format(parameters)
    else:
        response['messsage'] = "Invalid Request"
    return Response(response)


def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # Replace spaces
    for r in replace:
        filename = filename.replace(r, '_')

    # Keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

    # Keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename) > char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit]


def swagger_data_response(response_desc, schema_data_dict={}, is_list_data=False, non_data_dict={}):
    from drf_yasg import openapi
    response = {}
    if is_list_data:
        response['data'] = openapi.Schema(type=openapi.TYPE_ARRAY,
                                          items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                               properties=schema_data_dict))
    else:
        response['data'] = openapi.Schema(type=openapi.TYPE_OBJECT,
                                          properties=schema_data_dict)
    response.update({
        'status_code': openapi.Schema(type=openapi.TYPE_INTEGER),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    })
    if non_data_dict:
        response.update(non_data_dict)
    return openapi.Response(response_desc,
                            openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties=response
                            ))