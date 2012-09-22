srtp
====

SRTP: Subscription Realtime Transfer Protocol project

Websockets and persisting HTTP connections provide the new transport layer for the real-time web.
There does not yet exist a standard application layer.
This project attempts to define a basic application layer, as well as several examples, that can be used by various real-time projects.

Register subscription:
CLIENT SENDS
{
    "source": "/elements",
    "restrict": {
        "foo": "bar"
    }
}

REMOTE HOST RESPONDS
{
    "verb": "create",
    "data" : {
        "new": "element",
        "in": "here"
    }
}
{
    "verb": "update",
    "id": 67990,
    "data" : {
        "new": "change"
    }
}
{
    "verb": "delete",
    "id": 67990
}
... continuing to send over time




