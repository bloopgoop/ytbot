# ytbot

ytbot is a Discord bot made to play Youtube audio in a Discord voice channel. It utilizes the discord API to connect to voice channels and play back audio files. Pytube is used to get a Youtube video's title and audio. 
The bot uses a queue to play back songs in order and has many other useful functions like looping the queue, skipping the song, or jumping to a specific index in the queue.


# Usage
> Prefix every command with a `!`

**BasicCommands:**
|     Command           |Inputs                        |Explanation|
|----------------|-------------------------------|-----------------------------|
|clear_messages|`Number of messages to clear`            |Clears a number of messages from the channel            |
|Join          |`None`            |Joins the voice channel that the user is in            |
|Leave          |`None`|Leaves a voice channel if connected|


 **YtCommands:**
 |     Command           |Inputs                        |Explanation|
|----------------|-------------------------------|-----------------------------|
|clear	|`None`								|Clears the existing queue            |
|jump	|`Index of song in queue`            |Jumps to the index in the queue         |
|loop	|`None`									|Replays the songs in the queue and any songs to be added |
|np		|`None`                   		     |Displays the current song                        |
|pause	|`None`								|Pauses the player|
|play	|`URL or title`           			 |Plays YT audio from a URL. If a title is provided instead of a URL, the bot makes a YT search and plays the first video that shows up            |
|q		|`None`            					|Displays the queue            |
|remove |`Index`							|Removes a song from the queue given an index|
|resume | `None`							|Resumes the player
|skip	|`None`          				  |Skips the current song           |


**Other**
 |     Command           |Inputs                        |Explanation|
|----------------|-------------------------------|-----------------------------|
|help				|`None`            |Displays a message that tells users how to use the bot           |
|reyt|`None`            |Reloads the YTPlayer module, used for testing            |

