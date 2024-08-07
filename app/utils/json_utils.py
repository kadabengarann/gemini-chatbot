from langchain.schema import HumanMessage, AIMessage

# Utility functions (assuming they're already defined)
def messages_from_dict(messages, message_type = ""):
    serialized_messages = []
    for msg in messages:
        serialized_msg = {
            'Id': getattr(msg, 'id', None),
            'Sender': 'human' if isinstance(msg, HumanMessage) else 'AI',
            'Content': msg.content,
            'CreatedDateTime': getattr(msg, 'created_datetime', None),
            'Platform': getattr(msg, 'platform', message_type) or message_type
        }
        serialized_messages.append(serialized_msg)
    return serialized_messages


def messages_to_dict(serialized_messages):
    messages = []
    for serialized_msg in serialized_messages:
        if serialized_msg['Sender'] == 'human':
            msg = HumanMessage(content=serialized_msg['Content'])
        elif serialized_msg['Sender'] == 'AI':
            msg = AIMessage(content=serialized_msg['Content'])
        # Attach additional attributes to the message object
        msg.id = serialized_msg['Id']
        msg.created_datetime = serialized_msg['CreatedDateTime']
        msg.platform = serialized_msg.get('Platform')
        messages.append(msg)
    return messages
