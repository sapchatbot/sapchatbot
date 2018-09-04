####
# SAP Chatbot - Integration Development
# Chatbot Core Functions Module
####
# Version 2.0
# Last Updated on 09-Aug-2018
# Author: Kiran
#################

import requests
import json
import xml.etree.ElementTree as ET


class ReuseCommonUtils:
    """
    A class for common, reusable methods and/or components
    """
    @staticmethod
    def fetchkeyvalue(data, key):
        """
        Fetch value from a key value pair data
        :param data: The array / list of elements
        :param key: key to be searched for
        :return: value for the specified key
        """
        val: str = None
        try:
            val = data[key]
        except KeyError:
            print(key + " not found in " + data)
        except Exception as e:
            print("Exception Occurred - fetchKeyValue() : " + str(e))
        finally:
            return val

def df_query(query):
    """
    Method to post query to Dialog Flow and get response
    :param query: Query to be posted to Dialog Flow
    :return: Response from Dialog Flow
    """
    query = query.strip()  # def
    df_url = "https://api.dialogflow.com/v1/query"
    df_response = ""

    # if there is no query to process, return a blank value
    if query is None:
        return df_response

    # try to build payload and post the query to dialog flow
    try:
        df_request = json.dumps({
            "lang": "en",
            "query": query,
            "sessionId": "12345"
        })
        df_header = {
            # copy auth bearer token from DF Agent
            'Authorization': "Bearer 8834198b087940bbbc577ff8287032dd",
            'Content-Type': "application/json",
        }
        # post payload to DF
        df_post_response = requests.request("POST", df_url, data=df_request, headers=df_header)

        if df_post_response is not None:
            # convert response to json
            df_json = df_post_response.json()

            # print("Response from DF for " + query + " is:")
            # print(df_json)

            df_result = ReuseCommonUtils.fetchkeyvalue(df_json, "result")
            df_action = ReuseCommonUtils.fetchkeyvalue(df_result, "action")
            # check if action is unknown / smalltalk
            if ("smalltalk" in df_action or
                    df_action == 'input.unknown'):
                df_response = df_smalltalk(df_json)  # get response from small talk
            else:
                df_response = df_sap_proc_json(df_json)

    except Exception as e:
        print("Exception Occurred - df_query() : " + str(e))
    finally:
        return df_response


# def df_output(df_json):
#     """
#     Returns the Dialog Flow Output of the processed Dialog Flow Response in JSON
#     :param df_json: Dialog Flow Response in JSON format
#     :return: Processed Response
#     """
#     print(df_json)
#     result = ReuseCommonUtils.fetchkeyvalue(df_json, 'result')
#     print(result)
#     action = ReuseCommonUtils.fetchkeyvalue(result, 'action')
#     # get the generic OData URL from SAP
#     # odata_url = sap_gen_odata_url(action)
#     # return odata_url

def df_sap_proc_json(df_json):
    try:
        print("SAP Process Triggered...")
        payload = {}
        fnamvaluepair =[]
        sap_response = ""

        # fnamvaluepair.append({'Action': action})
        result = ReuseCommonUtils.fetchkeyvalue(df_json, 'result')
        action = ReuseCommonUtils.fetchkeyvalue(result, 'action')
        payload["Action"] = action
        parameters = ReuseCommonUtils.fetchkeyvalue(result, 'parameters')

        for fieldname in parameters:
            for fieldvalue in parameters[fieldname]:
                if fieldvalue == 'null':
                    fieldvalue=""
                fnamvaluepair.append({
                    "Action": "",
                    "FieldName": fieldname,
                    "FieldValue": fieldvalue
                })

        payload["GenItemSet"] = fnamvaluepair
        payload = json.dumps(payload).encode()
        print(payload)

        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'X',
            'Accept': 'application/json',
            'Cache-Control': "no-cache"
        }
        sapurl = 'https://p2000536037trial-trial.apim1.hanatrial.ondemand.com:443/' \
                 'p2000536037trial/ZCB_SERVICE_SRV/GenHeaderSet'
        response = requests.request("POST", sapurl, data=payload, headers=headers)
        return proc_sap_json(response.text)
    except Exception as e:
        return 'Technical Connectivity Issue: Please contact Administration team'


def proc_sap_json(jsonfromsap):
    if not is_json(jsonfromsap):
        return jsonfromsap

    json_resp = json.loads(jsonfromsap)
    print(json_resp)
    results = json_resp["d"]["GenItemSet"]["results"]
    value = ""
    for str in results:
        value += str['FieldName']
        value += '\n'
    return value

# def sap_gen_odata_url(action):
#     """
#     Get the subsequent ODATA URL based on the action of intent in the Dialog Flow
#     :param action: Action from the Dialog Flow Intent
#     :return: subsequent URL of the ODATA Service
#     """
#     odata_path = None
#     url = "https://p1940325576trial-trial.apim1.hanatrial.ondemand.com/p1940325576trial/ZCB_SERVICE_SRV/"
#     actionset = "actionSet('" + action+"')"
#     params = "$format=json"
#     complete_path = url + actionset + "?" + params
#     response = requests.request("GET", complete_path)
#     print("Response from Generic ODATA - " + response.text)
#     try:
#         json_response = json.loads(response.text)
#         if "error" in json_response:
#             # Assumption : OData Method is not maintained for DF Action
#             odata_path = "Error - ODATA_NOT_FOUND : OData URL is not maintained for action - '" + action +"'"
#         elif "d" in json_response:
#             d = ReuseCommonUtils.fetchkeyvalue(json_response, 'd')
#             odata_path = ReuseCommonUtils.fetchkeyvalue(d, 'Odatapath')
#         else:
#             odata_path = response.text
#     except Exception as e:
#         print("getOdataUrl Exception " + str(e))
#         odata_path = response.text
#     finally:
#         return odata_path


def is_json(value):
    try:
        json.loads(value)
    except ValueError as e:
        return False
    return True

def df_smalltalk(df_json):
    """
    Returns a Small Talk Response from Dialog Flow
    :param df_json: JSON Response from Dialog Flow
    :return: Small Talk response as String
    """
    print("Small Talk triggered...")  # debug
    result = ReuseCommonUtils.fetchkeyvalue(df_json,'result')
    speech = ReuseCommonUtils.fetchkeyvalue(result, 'speech')
    return speech
