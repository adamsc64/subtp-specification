# SubTP

## The Subscription Transfer Protocol (SubTP) project
Websockets and COMET-style open HTTP connections provide the new transport layer for the real-time web. There does not yet exist a standard application layer for realtime socket connections, such as HTTP provides over TCP.

This project is an experiment in progress to develop an application layer around the paradigm of registering subscriptions to collections of mutable data resources. Please fork it and feel free to report issues or feature requests!

I'm using [socket.io](http://socket.io) as a transport layer because of its robust namespacing features and its out of the box implementation of heartbeats, timeouts, and reconnection support.

### Why would I use it?
* You have a collection of serverside resources and you want your application to subscribe to changes in real-time on the clientside.
* You want to make data updates between the clientside and serverside seamless and in real-time.
* You want to use the easy-to-use Javascript API that socket.io provides.

### Example implementations
* Django models: [django-subtp](http://github.com/adamsc64/django-subtp) - Easy way to register signal handlers to your Django models and broadcast the changes over SubTP. The only catch is you have to serve Django behind a tornadio2 webserver to handle the real-time stuff.
* MongoDB: [mongo-subtp](http://github.com/adamsc64/mongo-subtp) - Easy way to tail the MongoDB oplog, normalize the results to SubTP, and broadcast changes over tornadio2.

### What it specifies
* Resource identification: SubTP allows clients to subscribe to URI style namespaces customized for your application.
* Client and server emit events to each other over socket.io's event API.
* Data operations: SubTP broadcasts four events using the names of the basic functions of persistent storage: `create`, `read`, `update` and `delete` (CRUD). This is in addition to the events that socket.io provides out of the box (e.g., `connect` and `disconnect`).
* Registration: The client begins a session by emitting a `register` event with the details of its subscription.
* Real-time responses: The server responds by continually streaming results according to the criteria of the subscription.
* Bidirectionality: The client can push events to the server or the server can push events to the client.

### What's It Look Like?
A basic example looks like:

#### A client first registers a subscription
The subscription specifies the kind of data expected back and is identified by a given `name`.
```js
var elements = io.connect("/io/elements");

var subscription = {
    "name": "MyContract",
    "from": "2012-07-05T12:53:12Z",
    "filter": {
        "foo": "bar"
    }
};
elements.emit("register", subscription);
```

#### Remote host fulfils the subscription
As the dataset itself changes, results are broadcast back to the listening client. Only those results that fulfill the conditions of the subscription are those that are sent. In this case, it is only those objects who have a "bar" value set for the "foo" key.

To see the results from the remote host, we can log the results to the in-browser console:
```js
function created(element) {
    console.log("Created:");
    console.log(element);
}
function updated(element) {
    console.log("Updated:");
    console.log(element);
}
function deleted(element) {
    console.log("Deleted:");
    console.log(element);
}

elements.on("create", created);
elements.on("update", updated);
elements.on("delete", deleted);
```

When events are received, for example a create, update, and delete event for an item with {"foo": "bar"}, the console logger will display them like this:
```js
Created:
{
    "id": 67990,
    "data" : {
        "new": "element",
        "here": "with",
        "foo": "bar",
        "and": "having",
        "_id": 67990
    }
}
Updated:
{
    "id": 67990,
    "data" : {
        "new": "change"
    }
}
Deleted:
{
    "id": 67990
}
... continuing to send over time
```

#### Client pushes data back to the server
Even while receiving events about a particular dataset, the client can also push CRUD operations back up to the server, perhaps in response to its own application logic or user interaction.

```js
if (application_logic_condition === true) {
    var myelement = {
        "id": 67990,
        "data": {
            "new": "changed again"
        }
    };
    elements.emit("update", element);
}
```

The client should immediately receive the update back because it is still subscribing to events for the kinds of objects that have {"foo": "bar"}:

```js
Updated:
{
    "id": 67990,
    "data" : {
        "new": "changed again"
    }
}
```

