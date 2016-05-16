# Example mapping.py

RESOURCE_ACTIONS = (
    'create',
    'delete',
    'get',
    'update',
)
RESOURCE_MAPPING = {
    'conversations': {
        'content': {
            # https://developer.layer.com/docs/platform/messages#downloading-a-rich-content-message-part
            'get': { 
                'endpoint_base': ['conversations', 'content'],
                'ids': ['conversation_uuid', 'content_id'],
                'verb': 'get',
            },
            # https://developer.layer.com/docs/platform/messages#initiating-a-rich-content-upload
            'upload': { 
                'endpoint_base': ['conversations', 'content'],
                'ids': ['conversation_uuid'],
                'verb': 'post',
            },
        },
        # https://developer.layer.com/docs/platform/conversations#create-a-conversation
        'create': {
            'endpoint_base': ['conversations'],
            'ids': None,
            'verb': 'post',
        },
        # https://developer.layer.com/docs/platform/conversations#delete-a-conversation
        'delete': {
            'endpoint_base': ['conversations'],
            'ids': ['conversation_uuid'],
            'verb': 'delete',
        },
        # https://developer.layer.com/docs/platform/conversations#retrieve-one-conversation-system-perspective-
        'get': { # System Perspective Conversations
            'endpoint_base': ['conversations'],
            'ids': ['conversation_uuid'],
            'verb': 'get',
        },
        'messages': {
            # https://developer.layer.com/docs/platform/messages#deleting-messages
            'delete': { 
                'endpoint_base': ['conversations', 'messages'],
                'ids': ['conversation_uuid', 'message_uuid'],
                'verb': 'delete',
            },
            # https://developer.layer.com/docs/platform/messages#retrieve-messages-system-perspective-
            'get': { 
                'endpoint_base': ['conversations', 'messages'],
                'ids': ['conversation_uuid', 'message_uuid'],
                'verb': 'get',
            },
            # https://developer.layer.com/docs/platform/messages#send-a-message
            'send': { 
                'endpoint_base': ['conversations', 'messages'],
                'ids': ['conversation_uuid'],
                'verb': 'post',
            },
        },
        # https://developer.layer.com/docs/platform/conversations#edit-a-conversation
        'update': {
            'endpoint_base': ['conversations'],
            'ids': ['conversation_uuid'],
            'verb': 'patch',
        },
    }
}