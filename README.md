# UKAP: The Unofficial KissAnime Plugin
An unofficial KissAnime client for Kodi, designed for the Fire Stick, Fire TV, and Windows.

## Overview and Motivation
This plugin was made as a simpler alternative to the fantastic and feature-packed [KissAnime Kodi plugin](https://github.com/HIGHWAY99/repository.thehighway/tree/master/repo/plugin.video.kissanime), which itself is a Kodi front-end for the [KissAnime website](http://kissanime.to).

This plugin hopes to improve over the original in a few key areas.

### Speed
Speed has been an emphasis for this plugin on the slowest popular platform (the Amazon Fire Stick) from day 1, especially for the menus that don't require accessing the site as well as the pages that list the episodes of a particular show.  Everything has been benchmarked on the Fire Stick and compared to other popular apps.  

If the plugin is taking a while to load a page, chances are it's the KissAnime website itself, which usually takes 4-5 seconds on good days to serve content, or a blocked metadata request (and metadata support can be turned off).

### Metadata support
Getting metadata for anime shows has traditionally been a hard problem for primarily 2 reasons:

1. Anime shows often have many different names, and the KissAnime website does not always have the exact same name as metadata providers.

2. Japanese shows do not usually conform to the standard US season-episode format.  Instead, they often use an absolute numbering system or may give subsequent seasons suffixes or entirely new names.

This plugin extends the built-in metahandlers plugin to grab metadata for the shows.  The parameters for searching for and matching against US-provided metadata have been expanded, resulting in more shows getting more metadata matches.

Additionally, users can fix or find metadata for any media they want, in case the plugin got the wrong metadata or nothing at all.

### Code maintainability
The original KissAnime Kodi plugin doesn't seem to be open-source, and the code was initially written as a learning experience for programming.  As a result, it's hard for any user to patch the plugin, as I experienced myself.

This is my first Kodi plugin ever and my first object-oriented project in years.  Although the plugin is not the most well organized codebase out there, and despite the fact that there are some strange implementation patterns (I aplogize in advance), I hope this plugin will be a lot easier to maintain down the line than others.

## Features
### Enhanced metadata support
As mentioned previously, the built-in metahandlers plugin has been extended and modified to work better with anime shows and Japanese media.  There are still some gaps or peculiarities, but my hope is that the support is better than other plugins for similar content.

Furthermore, users can fix or find metadata for shows with incorrect or absent metadata.  The process includes suggestions populated from aliases of the show from the KissAnime website, which often will do the trick!

Note that metadata is stored by the metahandlers plugin in UKAP's own database, instead of in the metahandlers database, because the database structure has been modified.

### Browse
Users can browse the plugin just like the KissAnime website, which includes categories like Popular, Upcoming, Genres, and Alphabetical.

### Search
Users can search for shows through the plugin.  The search function actually uses the website's Advanced Search function, which is surprisingly much more accurate for finding certain shows.

### Account bookmarks
Users can log in to their accounts and browse and modify their bookmarks (no folder support yet).  The username and password are not saved at all by the plugin.

### Last Anime Visited
Users can see the last anime they visited from the main menu, for quick access for continuing a series.

### Quality selection
The default quality of the video can be selected in the settings or individually for each piece of media.

### Widget support
Widgets (in supported skins) can be populated with any page of the plugin (minus search), including the bookmarks and the last anime visited.  Note, however, that having the widgets reload every time could cause KissAnime to throw some errors at you though!

## Known issues
 - Fixing or finding metadata from the search page brings up the search box, prompting the user to re-enter the original search query.
 - Getting metadata for movies may fail if you don't have your own key.
 - This isn't really an issue, but toggling bookmarks is a bit annoying at the moment (it was implemented this way based on what the site does).  Alternatives should be explored if possible.

## Future plans
 - Add list support
 - Investigate possible Trakt integration
 - Add a "Go to page" option for submenus under Browse
 - Sync watched status with the KissAnime website for logged in users
 - Consider adding folder support for bookmarks and lists