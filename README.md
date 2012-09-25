# subtp-specification

## SubTP: Subscription Transfer Protocol project

* Websockets and COMET-style open HTTP connections provide the new transport layer for the real-time web.
* There does not yet exist a standard application layer for realtime socket connections, such as HTTP provides over TCP.
* This project attempts to define a basic application layer, as well as offer several examples, that can be used to implement various real-time projects.

### What it specifies

* SubTP allows clients to subscribe to socket.io namespaces custom for your application.
* Client and server emit events over socket.io using JSON.
* Besides the canonical socket.io events (`connect`, `message`, and `disconnect`), SubTP defines four custom events using the names of the four classic functions of persistent storage: `create`, `read`, `update` and `delete` (CRUD).
* The client begins by registering a `contract`.
* The server responds by continually streaming results honoring the contract.


### What's It Look Like?

A basic example looks like:

#### A client first defines a contract
```js
{
    "create": {
        "contract": {
            "name": "MyContract",
            "from": "2012-07-05T12:53:12Z",
            "filter": {
                "foo": "bar"
            }
        }
    }
}
```

#### Remote host honors the contract.
```js
{
    "create": {
        "id": 67990,
        "data" : {
            "new": "element",
            "here": "with",
            "foo": "bar",
            "and": "having",
            "_id": 67990
        },
        "contract": {
            "name": "MyContract"
        }
    }
}
{
    "update": {
        "id": 67990,
        "data" : {
            "new": "change"
        },
        "contract": {
            "name": "MyContract"
        }
    }
}
{
    "delete": {
        "id": 67990,
        "contract": {
            "name": "MyContract"
        }
    }
}
```
... continuing to send over time




