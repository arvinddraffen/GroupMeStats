from __future__ import unicode_literals
import argparse
import csv
import json
import pickle
import re
import requests
import sys
import time


TOKEN = ""


def main():
    parser = argparse.ArgumentParser(description='Select GroupMe message type(s) for program to use.')
    custom_args = setup_argparser(parser)
    if not set_token(custom_args):
        print("No token provided. Exiting.")
        sys.exit()
    users = set()
    start_time = time.time()
    total_stats = {}
    num_messages = 0
    if custom_args.messages_direct:
        retrieved_chats = get_chats(users)
        chat_ids, chat_info = retrieved_chats[1], retrieved_chats[2]
        if custom_args.id_select is not -1:
            if custom_args.id_select <= len(chat_ids):
                if not custom_args.all_users:
                    users.clear()
                new_chat = []
                new_chat.append(chat_ids[custom_args.id_select])
                chat_ids = new_chat
        if not custom_args.ids_only:
            if custom_args.load:
                retrieved_direct_messages = load_messages('direct', custom_args.encoding_type)
                selected_direct_messages = {}
                for key in retrieved_direct_messages.keys():
                    if key in chat_ids:
                        selected_direct_messages[key] = retrieved_direct_messages[key]
                retrieved_direct_messages = selected_direct_messages
            else:
                retrieved_direct_messages = retrieve_chat_messages(chat_ids, chat_info)
                save_messages(retrieved_direct_messages, 'direct', custom_args.encoding_type)
            print("Retrieving messages " + calc_execution_time(start_time))
            start_time = time.time()
            chat_stats = {}
            chat_stats = determine_user_statistics(retrieved_direct_messages, chat_ids, 'direct', users)
            total_stats.update(chat_stats[0])
            num_messages += chat_stats[1]
    if custom_args.messages_group:
        retrieved_groups = get_groups(users)
        group_ids, group_info = retrieved_groups[1], retrieved_groups[2]
        if custom_args.id_select is not -1:
            try:
                if custom_args.id_select <= len(group_ids):
                    if not custom_args.all_users:
                        users.clear()
                    new_group = []
                    new_group.append(group_ids[custom_args.id_select])
                    group_ids = new_group
            except IndexError:
                print("You entered an invalid group number.\nExiting...\n")
                sys.exit()
        if not custom_args.ids_only:
            if custom_args.load:
                retrieved_group_messages = load_messages('group', custom_args.encoding_type)
                try:
                    selected_group_messages = {}
                    for key in retrieved_group_messages.keys():
                        if key in group_ids:
                            selected_group_messages[key] = retrieved_group_messages[key]
                    retrieved_group_messages = selected_group_messages
                except AttributeError:
                    print("Unable to analyze data due to above error.\n")
                    return
            else:
                retrieved_group_messages = retrieve_group_messages(group_ids, group_info)
                save_messages(retrieved_group_messages, 'group', custom_args.encoding_type)
            print("Retrieving messages " + calc_execution_time(start_time))
            start_time = time.time()
            group_stats = {}
            group_stats = determine_user_statistics(retrieved_group_messages, group_ids, 'group', users)
            total_stats.update(group_stats[0])
            num_messages += group_stats[1]
    if not custom_args.ids_only:
        try:
            write_to_csv(total_stats, num_messages)
            print("Calculating and writing stats " + calc_execution_time(start_time))
        except PermissionError:
            print("\nPlease close the file \'groupme_stats.cv\'")
            print("Unable to write to file.\n")


def setup_argparser(parser):
    """ 
    Add the valid/accepted command-line arguments to the Argument Parser.

    Args:
        parser: ArgumentParser used for command line arguments
    
    Returns:
        result of parser.parse_args() such that provided arguments at runtime can be parsed
    """
    parser.add_argument('--t', '--token',
                        type=str,
                        action='store',
                        dest='token',
                        help='Command line option for entering GroupMe token.')
    parser.add_argument('--c', '--chat', 
                        action='store_true', 
                        dest='messages_direct', 
                        help='Only analyze chats (direct messages)')
    parser.add_argument('--g', '--group', 
                        action='store_true', 
                        dest='messages_group', 
                        help='Only analyze group messages')
    parser.add_argument('--i', '--id', 
                        action='store_true', 
                        dest='ids_only', 
                        help='Only retrieve group/chat ids without retrieving messages')
    parser.add_argument('--s', '--id_select', 
                        type=int, 
                        dest='id_select', 
                        default=-1, 
                        help='''The chat/group ID to retrieve. Must select a type (or types) of message(s) to analyze. Can receive 
                                one group or chat at a time, but can receive both a group and chat at the same index.''')
    parser.add_argument('--a', '--all_users', 
                        action='store_true', 
                        dest='all_users', 
                        help='Override to include all users in resulting CSV file, not just members of specific group or chat')
    parser.add_argument('--l', '--load',
                        action='store_true',
                        dest='load',
                        default=False,
                        help='''Load messages from file rather than retrieve from GroupMe API. Note this will only retrieve messages
                                retrieved from the program's last run.''')
    parser.add_argument('--e', '--encoding_type',
                        type=str,
                        action='store',
                        default='json',
                        dest='encoding_type',
                        help='''Select encoding type between JSON and pickle. If not specified, JSON is the default.
                                Can be set for storing/loading, but a file of the correct type (json or pickle) must be created prior to loading.
                                Valid types are \'json\' or \'pkl\'.''')
    return parser.parse_args()


def set_token(custom_args, from_gui = False):
    """
    Assign the TOKEN variable to its value, provided via command line or file.

    Args:
        custom_args: parsed provided user-provided runtime command line arguments, used to check whether TOKEN was provided via command-line option
    
    Returns:
        True if TOKEN is provided via command-line or retrievable from file. False otherwise.
    
    Raises:
        FileNotFoundError if TOKEN if 'token.txt' file is not available in expected location, after checking for TOKEN via command line option
    """
    global TOKEN
    if from_gui:
        try:
            with open('token.txt', 'r') as token_file:
                TOKEN = token_file.readline().strip('\n')
                return True
        except FileNotFoundError:
            return False
        return False
    else:
        if custom_args.token is not None:
            TOKEN = custom_args.token
            return True
        else:
            try:
                with open('token.txt', 'r') as token_file:
                    TOKEN = token_file.readline().strip('\n')
                    return True
            except FileNotFoundError:
                return False
            return False


def get_groups(users, suppress_print=False):
    """
    Retrieve active and former groups for the GroupMe profile.

    Args:
        users: set containing all user_ids encountered through analysis of groups and/or chats
    
    Returns:
        data: full JSON data retrieved from API request of groups
        g_ids: list of all group ids retrieved from API request of groups
        group_info: dictionary with key of Group ID and value a a list of Group Name and number of messages sent in group
    """
    #Active Groups
    r = requests.get("https://api.groupme.com/v3/groups?token=" + TOKEN + "&per_page=500") # max val allowed per API is 500 for groups
    data = r.json()
    if not suppress_print:
        print("Active Groups")
        print('{0: <2} {1: <40} {2: <10} {3: <12}'.format('#', 'Group Name', 'Group Id', 'Message Count'))
    g_ids = []
    group_info = {}
    usr = []
    i = 0
    for element in data['response']:
        if not suppress_print:
            print('{0: <2} {1: <40} {2: <10} {3: >12}'.format(i, process_name(element['name']), element['group_id'], element['messages']['count']))
        g_ids.append(element['group_id'])
        group_info[element['group_id']] = [element['name'], element['messages']['count']]
        for member in element['members']:
            if member['user_id'] not in users:
                usr.append(member['user_id'])
        i += 1

    # Former Groups
    r = requests.get("https://api.groupme.com/v3/groups/former?token=" + TOKEN + "&per_page=500")
    data = r.json()
    if not suppress_print:
        print("\nFormer Groups (you must rejoin these groups to analyze messages)")
        print('{0: <2} {1: <40} {2: <10}'.format('#', 'Group Name', 'Group Id'))
    for element in data['response']:
        # These groups are not added to g_ids because their messages cannot be later retrieved as former groups
        if not suppress_print:
            print('{0: <2} {1: <40} {2: <10}'.format(i, process_name(element['name']), element['group_id']))
        i += 1
    if not suppress_print:
        print("\n")
    users.update(usr)
    return data, g_ids, group_info


def get_chats(users, suppress_print=False):
    """
    Retrieve active chats for the GroupMe profile.

    Args:
        users: set containing all user_ids encountered through analysis of chats and/or groups

    Returns:
        data: full JSON data retrieved from API request of chats
        c_ids: list of all chat ids retrieved from API request of chats
        chat_info: dictionary with key of Chat ID and value a a list of Other User Name and number of messages sent in chat
    """
    r = requests.get("https://api.groupme.com/v3/chats?token=" + TOKEN + "&per_page=100") # max val allowed per API is 100 for chats
    data = r.json()
    if not suppress_print:
        print('{0: <2} {1: <40} {2: <10} {3: <12}'.format('#', 'Person Name', 'Chat Id', 'Message Count'))
    c_ids = []
    chat_info = {}
    i = 0
    for element in data['response']:
        if not suppress_print:
            print('{0: <2} {1: <40} {2: <10} {3: >12}'.format(i, process_name(element['other_user']['name']), element['other_user']['id'], element['messages_count']))
        c_ids.append(element['other_user']['id'])
        chat_info[element['other_user']['id']] = [element['other_user']['name'], element['messages_count']]
        i += 1
    if not suppress_print:
        print("\n")
    users.update(c_ids)
    return data, c_ids, chat_info

def process_name(name):
    pattern = re.compile(r'([^\s\w]|_)+', re.UNICODE)
    return pattern.sub('', name)


def retrieve_group_messages(group_ids, group_info):
    """
    Retrieve all messages for all groups in group_ids, retrieves for each group sequentially.

    Args:
        group_ids: list of group ids returned from get_groups()

    Returns:
        group_analysis_results: dictionary with each group_id in group_ids as keys and all messages for each group (in the form of a list) as corresponding values
    """
    group_analysis_results = {}
    for group in group_ids:
        print("Analyzing Group Message Thread: " + group_info[group][0])
        messages = []
        r = requests.get("https://api.groupme.com/v3/groups/" + str(group) + "/messages?token=" + TOKEN + "&limit=1")
        messages.append(r.json()['response']['messages'][0])
        message_id = messages[0]['id']
        while True:
            r = requests.get("https://api.groupme.com/v3/groups/" + str(group) + "/messages?token=" + TOKEN + "&before_id=" + str(message_id) + "&limit=100")
            try:
                messages += r.json()['response']['messages']
                message_id = messages[-1]['id']         # oldest message received in last 100 messages returned from API request
            except ValueError:
                break
            print("\rRetrieved " + str(len(messages)) + "/" + str(group_info[group][1]) + " messages.", end='')
        group_analysis_results[group] = messages
        print("")
    return group_analysis_results

    
def retrieve_chat_messages(chat_ids, chat_info):
    """
    Retrieve all messages for all chats in chat_ids, retrieves for each group sequentially.

    Args:
        chat_ids: list of chat ids returned from get_chats()
    
    Returns:
        dm_analysis_results: dictionary with each chat_id (dm) in chat_ids as keys and all messages for each chat (in the form of a list) as corresponding values
    """
    dm_analysis_results = {}
    for dm in chat_ids:
        print("Analyzing Direct Message Thread With User: " + chat_info[dm][0])
        messages = []
        r = requests.get("https://api.groupme.com/v3/direct_messages?token=" + TOKEN + "&other_user_id=" + str(dm))
        messages.append(r.json()['response']['direct_messages'][0])
        message_id = messages[0]['id']
        while True:
            r = requests.get("https://api.groupme.com/v3/direct_messages?token=" + TOKEN + "&other_user_id=" + str(dm) + "&before_id=" + str(message_id))
            try:
                if len(r.json()['response']['direct_messages']) == 0:
                    break
                messages += r.json()['response']['direct_messages']
                message_id = messages[-1]['id']
            except ValueError:
                break
            print("\rRetrieved " + str(len(messages)) + "/" + str(chat_info[dm][1]) + " messages.", end='')
        dm_analysis_results[dm] = messages
        print("")
    return dm_analysis_results


def save_messages(results, msg_type, encoding_type):
    """
    Writes dictionary containing each group/chat and its messages to either a JSON or pkl file. 

    Args:
        results: dictionary with group ids as keys and messages as values (in the format of dictionary returned by retrieve_group_messages() and retrieve_chat_messages())
        msg_type: either 'group' or 'direct' for groups and chats, respectively
        encoding_type: either 'json' or 'pkl' for JSON or pickle, respectively. Encoding type to use specified by command line option
    """
    if encoding_type.lower() == 'json':
        if msg_type.lower() == 'group':
            with open('group_messages.json', 'w', encoding='utf-8') as save_file:
                json.dump(results, save_file, ensure_ascii=False, indent=4)
        elif msg_type.lower() == 'direct':
            with open('direct_messages.json', 'w', encoding='utf-8') as save_file:
                json.dump(results, save_file, ensure_ascii=False, indent=4)
        else:
            return
    elif encoding_type.lower() == 'pkl':
        if msg_type.lower() == 'group':
            with open('group_messages.pkl', 'wb') as save_file:
                pickle.dump(results, save_file)
        elif msg_type.lower() == 'direct':
            with open('direct_messages.pkl', 'wb') as save_file:
                pickle.dump(results, save_file)
        else:
            return
    else:
        print("Unable to save. Invalid encoding type given.")
        return
  
        
def load_messages(msg_type, encoding_type):
    """
    Loads and returns dictionary containing each group/chat and its messages from either a JSON or pkl file.

    Args:
        msg_type: either 'group' or 'direct' for groups and chats, respectively
        encoding_type: either 'json' or 'pkl' for JSON or pickle, respectively. Encoding type to use specified by command line option
    
    Returns:
        dictionary with group ids as keys and a list of messages as values if appropriate file exists. None is returned otherwise.
    """
    if encoding_type.lower() == 'json':
        if msg_type.lower() == 'group':
            try:
                with open('group_messages.json', 'r', encoding='utf-8') as save_file:
                    return json.load(save_file)
            except FileNotFoundError:
                print("File \'group_messages.json\' does not exist.")
                return
        elif msg_type.lower() == 'direct':
            try:
                with open('direct_messages.json', 'r', encoding='utf-8') as save_file:
                    return json.load(save_file)
            except FileNotFoundError:
                print("File \'direct_messages.json\' does not exist.")
                return
        else:
            return
    elif encoding_type.lower() == 'pkl':
        if msg_type.lower() == 'group':
            try:
                with open('group_messages.pkl', 'rb') as save_file:
                    return pickle.load(save_file)
            except FileNotFoundError:
                print("File \'group_messages.pkl\' does not exist.")
                return
        elif msg_type.lower() == 'direct':
            try:
                with open('direct_messages.pkl', 'rb') as save_file:
                    return pickle.load(save_file)
            except FileNotFoundError:
                print("File \'direct_messages.pkl\' does not exist.")
                return
        else:
            return
    else:
        print("Unable to load. Invalid encoding type given.")
        return


def determine_user_statistics(msgs, group_ids, msg_type, users):
    """
    Calls process_message_stats() for every message in each group and returns the cumulative result as the dictionary stats

    Args:
        msgs: list of messages from selected group(s) or chat(s) from which to calculate volume stats
        group_ids: list of group ids from which messages in msgs were retrieved
        msg_type: parameter specifying whether type of 'msgs' is 'group' or 'direct'
        users: users: set containing all user_ids encountered through analysis of chats and/or groups (provided not reset, otherwise empty)
    
    Returns:
        stats: dictionary with key of user id and value of list contaning user's name and various volume stats
        num_messages: the total number of messages analyzed by the program
    """
    num_messages = 0
    stats = dict((element, {
        'name': '',
        'messages_sent': 0, 
        'likes_received': 0, 
        'likes_given': 0, 
        'pct_msgs_liked': 0,
        'self_likes': 0, 
        'words_sent': 0,
        'images_sent': 0}) for element in users)
    if msg_type.lower() == 'group':
        print("Analyzing group messages")
        for group in group_ids:
            for msg in msgs[group]:
                process_message_stats(stats, msg, users)
                num_messages += 1
        for usr in users:
            stats[usr].pop('pct_msgs_liked')
    elif msg_type.lower() == "direct":
        print("Analyzing direct messages")
        for chat in group_ids:
            for msg in msgs[chat]:
                process_message_stats(stats, msg, users)
                num_messages += 1
        for usr in users:
            if not stats[usr]['messages_sent'] == 0:
                stats[usr]['pct_msgs_liked'] = round(stats[usr]['likes_received']/stats[usr]['messages_sent']*100,2)
    else:
        print("Provided message type not recognized")
    return stats, num_messages


def process_message_stats(stats, msg, users):
    """
    Updates volume statistics in stats dict for particular user(s) based on message data

    Args:
        stats: dictionary with key of user id and value of list contaning user's name and various volume stats
        msg: JSON data for a particular GroupMe message to analyze
    """
    if (msg['sender_id']) not in stats.keys():
        stats[msg['sender_id']] = {'name': '', 'messages_sent': 0, 'likes_received': 0, 'likes_given': 0, 'pct_msgs_liked': 0, 'self_likes': 0, 'words_sent': 0, 'images_sent': 0}
        users.update([msg['sender_id']])
    if not bool(stats[msg['sender_id']]['name'] and stats[msg['sender_id']]['name'].strip()):
        stats[msg['sender_id']]['name'] = msg['name']
    stats[msg['sender_id']]['messages_sent'] += 1
    stats[msg['sender_id']]['likes_received'] += len(msg['favorited_by'])
    if len(msg['favorited_by']) > 0:
        for usr in msg['favorited_by']:
            if usr not in stats.keys():
                stats[usr] = {'name': '', 'messages_sent': 0, 'likes_received': 0, 'likes_given': 0, 'pct_msgs_liked': 0, 'self_likes': 0, 'words_sent': 0, 'images_sent': 0}
                users.update(msg['favorited_by'])
            stats[usr]['likes_given'] += 1
    if msg['sender_id'] in msg['favorited_by']:
        stats[msg['sender_id']]['self_likes'] += 1
    if msg['text'] is not None:
        msg['text'].split(' ')
        stats[msg['sender_id']]['words_sent'] += len(msg['text'].split(' '))
    if msg['attachments']:
        for attachment in msg['attachments']:
            if attachment['type'] == 'image':
                stats[msg['sender_id']]['images_sent'] += 1


def write_to_csv(stats, num_messages):
    """
    Writes the calculated stats to the file 'groupme_stats.csv'.

    Args:
        stats: dictionary with key of user id and value of list contaning user's name and various volume stats
        num_messages: the total number of messages analyzed by the program
    """
    with open('groupme_stats.csv', 'w', encoding='utf-8-sig', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        csv_file.write("Analyzed " + str(num_messages) + " messages.\n")
        for key, value in stats.items():
            writer.writerow([key, value])


def calc_execution_time(start_time):
    """
    Returns a formatted string reporting the duration of time from the provided start_time argument to when the function is entered.

    Args:
        start_time: a float representing a time of an event
    
    Returns:
        a formatted string stating the duration between time at which the function was entered and start_time
    """
    execution_time = time.time() - start_time
    if execution_time > 60:
        return ("took {0:.5f} minutes to execute".format((time.time() - start_time)/60))
    else:
        return ("took {0:.5f} seconds to execute".format((time.time() - start_time)))


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("The program " + calc_execution_time(start_time))
