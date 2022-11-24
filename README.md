Shane Reilly, Daniel Chandler, Justin Turnau

Equal contribution

How to compile/run this code:

Both the client and the server are written in python .py files. As these are both Python files, compiling/running them follows the normal steps as for any Python (.py) files. All one needs to do in order to run this code is to first run the server.py file in a terminal, then run the client.py files in another terminal. As an addition note, this code was tested using Python version 3.6.9. It has not been tested on previous Python versions. In order to ensure that it runs smoothly, please run this code using Python version 3.6.9 or later.

Major Issues:

A major issue we solved was broadcating information to both all clients and to only specific clients. The solution we used was a global array for each group which stores connection strings. This is a bit of a hacky solution, but for the purposes of the assignment accomplishes the task. It was particularly difficult to figure out how to attach user information with a client thread in such a way that notifying a set of usernames would notify the client connections associated with them. The global array for each group solution worked but is clearly less than elegant.

A major issue that we could not solve was how to prevent new clients from seeing only the previous 2 messages that were sent by previously existing users. We attempted to associate a postcount with a user such that when a user joined, they would get a viewable_postcount variable for example 4 (where 4 posts have already been made before they got here) and when viewing a message, utilize a user's viewable_postcount number - 2 to check if they are allowed to view a message/post. This proved difficult, however, because we could not find a way to cleanly associate a viewable_postcount variable with a user, as users were only strings in our model to be stored in a Group class. Perhaps a correct approach to this problem would have been to make users a class with a username and viewable_postcount associated with them. Another possible solution (which we tried but failed to execute) is to associate this viewable_postcount variable with the client thread. This proved rather challenging for the same reasons and overall did not work.

Additional Note:

Our handling of the Public Message Board can seem a bit unintuitive. When a user/client connects to the server, they are automatically put into the Public Message Board group (group 0). The %leave function works properly and allows a user to leave this group, this notifies all users (even those who are no longer in the public message board) that this user has left the public message board. The same thing happens when joining the public message board (group 0).
