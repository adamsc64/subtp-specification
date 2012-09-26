# SubTP

## The Subscription Transfer Protocol (SubTP) project
Websockets and COMET-style open HTTP connections provide the new transport layer for the real-time web. There does not yet exist a standard application layer for realtime socket connections, such as HTTP provides over TCP.

Taking the [socket.io](http://socket.io) project, with its implementation of heartbeats, timeouts, and reconnection support, to be one of the most mature means of transporting data between server and client in real time, this project attempts to define a basic application layer on top of socket.io, built around the paradigm of subscribing to collections of resources. This repo also offers several examples that can be used to implement various real-time projects.

### What it specifies
* SubTP allows clients to subscribe to namespaces customized for your application representing `resources`.
* Client and server emit events to eachother over socket.io's event API.
* Besides the canonical events that socket.io provides out of the box (`connect`, `message`, and `disconnect`), SubTP defines four custom events using the names of the basic functions of persistent storage: `create`, `read`, `update` and `delete` (CRUD).
* The client begins a session by registering a `subscription`.
* The server responds by continually streaming results honoring the subscription.
* Once the connection is established, the protocol is bidirectional. The client can push events to the server or the server can push events to the client.

### Why would I use it?
* You have a collection of serverside resources and you want your application to subscribe to changes in real-time on the clientside.
* You want to use the easy-to-use Javascript API that socket.io provides.

### What's It Look Like?
A basic example looks like:

#### A client first registers a subscription
The subscription specifies the kind of data expected back and is identified by a given `name`.
```js
{
    "create": {
        "subscription": {
            "name": "MyContract",
            "from": "2012-07-05T12:53:12Z",
            "filter": {
                "foo": "bar"
            }
        }
    }
}
```

In code:
```js
var elements = io.connect("/elements");

var subscription = {
    "subscription": {
        "name": "MyContract",
        "from": "2012-07-05T12:53:12Z",
        "filter": {
            "foo": "bar"
        }
    }
};
elements.emit("create", subscription);
```

#### Remote host honors the subscription
As the dataset itself changes, results are broadcast back to the listening client. Only those results that fulfill the conditions of the subscription are those that are sent.
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
        }
    }
}
{
    "update": {
        "id": 67990,
        "data" : {
            "new": "change"
        }
    }
}
{
    "delete": {
        "id": 67990
    }
}
```
... continuing to send over time

#### Client pushes data back to the server
Even while receiving events about a particular dataset, the client can also push CRUD operations back up to the server, perhaps in response to its own application logic or user interaction.

```js
var update = {
    "id": 67990,
    "data": {
        "new": "change"
    }
};
elements.emit("update", update);
```
