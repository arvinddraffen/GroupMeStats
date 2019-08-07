from __future__ import unicode_literals
import argparse
import csv
import json
import pickle
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
    if custom_args.messages_direct:
        retrieved_chats = get_chats(users, custom_args)
        chat_ids = retrieved_chats[1]
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
                retrieved_direct_messages = retrieve_chat_messages(chat_ids)
                save_messages(retrieved_direct_messages, 'direct', custom_args.encoding_type)
            print("Retrieving messages " + calc_execution_time(start_time))
            start_time = time.time()
            group_stats = {}
            group_stats = determine_user_statistics(retrieved_direct_messages, chat_ids, 'direct', users)
            total_stats.update(group_stats)
    if custom_args.messages_group:
        retrieved_groups = get_groups(users, custom_args)
        group_ids = retrieved_groups[1]
        if custom_args.id_select is not -1:
            if custom_args.id_select <= len(group_ids):
                if not custom_args.all_users:
                    users.clear()
                new_group = []
                new_group.append(group_ids[custom_args.id_select])
                group_ids = new_group
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
                retrieved_group_messages = retrieve_group_messages(group_ids)
                save_messages(retrieved_group_messages, 'group', custom_args.encoding_type)
            print("Retrieving messages " + calc_execution_time(start_time))
            start_time = time.time()
            group_stats = {}
            group_stats = determine_user_statistics(retrieved_group_messages, group_ids, 'group', users)
            total_stats.update(group_stats)
    if not custom_args.ids_only:
        try:
            write_to_csv(total_stats)
            print("Calculating and writing stats " + calc_execution_time(start_time))
        except PermissionError:
            print("\nPlease close the file \'groupme_stats.cv\'")
            print("Unable to write to file.\n")

def setup_argparser(parser):
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

def set_token(custom_args):
    global TOKEN
    if custom_args.token is not None:
        TOKEN = custom_args.token
        return True
    else:
        try:
            with open('token.txt', 'r') as token_file:
                TOKEN = token_file.readline()
                return True
        except FileNotFoundError:
            return False
        return False

def get_groups(users, custom_args):
    r = requests.get("https://api.groupme.com/v3/groups?token=" + TOKEN)
    data = r.json()
    print('{0: <2} {1: <40} {2: <10}'.format('#', 'Group Name', 'Group Id'))
    g_ids = []
    usr = []
    i = 0
    for element in data['response']:
        #print(element['group_id'])
        print('{0: <2} {1: <40} {2: <10}'.format(i, element['name'], element['group_id']))
        g_ids.append(element['group_id'])
        for member in element['members']:
            if member['user_id'] not in users:
                usr.append(member['user_id'])
        i += 1
    print("")
    users.update(usr)
    return data, g_ids

def get_chats(users, custom_args):
    r = requests.get("https://api.groupme.com/v3/chats?token=" + TOKEN)
    data = r.json()
    print('{0: <2} {1: <40} {2: <10}'.format('#', 'Person Name', 'Chat Id'))
    c_ids = []
    i = 0
    for element in data['response']:
        print('{0: <2} {1: <40} {2: <10}'.format(i, element['other_user']['name'], element['other_user']['id']))
        c_ids.append(element['other_user']['id'])
        i += 1
    print("")
    users.update(c_ids)
    return data, c_ids

def retrieve_group_messages(group_ids):
    group_analysis_results = {}
    for group in group_ids:
        print("Analyzing Group Message Thread with ID: " + group)
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
            print("\rRetrieved " + str(len(messages)) + " messages.", end='')
        group_analysis_results[group] = messages
        print("")
    return group_analysis_results

def retrieve_chat_messages(chat_ids):
    dm_analysis_results = {}
    for dm in chat_ids:
        print("Analyzing Direct Message Thread with ID: " + dm)
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
            print("\rRetrieved " + str(len(messages)) + " messages.", end='')
        dm_analysis_results[dm] = messages
        print("")
    return dm_analysis_results

def save_messages(results, msg_type, encoding_type):
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
    if encoding_type.lower() == 'json':
        if msg_type.lower() == 'group':
            try:
                with open('group_messages.json', 'rb') as save_file:
                    return json.load(save_file, encoding='utf-8')
            except FileNotFoundError:
                print("File \'group_messages.json\' does not exist.")
                return
        elif msg_type.lower() == 'direct':
            try:
                with open('direct_messages.json', 'rb', encoding='utf-8') as save_file:
                    return json.load(save_file, encoding='utf-8')
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
    stats = dict((element, {
        'name': '',
        'messages_sent': 0, 
        'likes_received': 0, 
        'likes_given': 0, 
        'self_likes': 0, 
        'words_sent': 0,
        'images_sent': 0}) for element in users)
    if msg_type.lower() == 'group':
        print("Analyzing group messages")
        for group in group_ids:
            for msg in msgs[group]:
                process_message_stats(stats, msg)
    elif msg_type.lower() == "direct":
        print("Analyzing direct messages")
        for chat in group_ids:
            for msg in msgs[chat]:
                process_message_stats(stats, msg)
    else:
        print("Provided message type not recognized")
    return stats

def process_message_stats(stats, msg):
    if (msg['sender_id']) not in stats.keys():
        stats[msg['sender_id']] = {'name': '', 'messages_sent': 0, 'likes_received': 0, 'likes_given': 0, 'self_likes': 0, 'words_sent': 0, 'images_sent': 0}
    if not bool(stats[msg['sender_id']]['name'] and stats[msg['sender_id']]['name'].strip()):
        stats[msg['sender_id']]['name'] = msg['name']
    stats[msg['sender_id']]['messages_sent'] += 1
    stats[msg['sender_id']]['likes_received'] += len(msg['favorited_by'])
    if len(msg['favorited_by']) > 0:
        for usr in msg['favorited_by']:
            if usr not in stats.keys():
                stats[usr] = {'name': '', 'messages_sent': 0, 'likes_received': 0, 'likes_given': 0, 'self_likes': 0, 'words_sent': 0, 'images_sent': 0}
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

def write_to_csv(stats):
    with open('groupme_stats.csv', 'w', encoding='utf-8-sig', newline = '') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in stats.items():
            writer.writerow([key, value])

def calc_execution_time(start_time):
    execution_time = time.time() - start_time
    if execution_time > 60:
        return ("took {0:.5f} minutes to execute".format((time.time() - start_time)/60))
    else:
        return ("took {0:.5f} seconds to execute".format((time.time() - start_time)))

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("The program " + calc_execution_time(start_time))
